from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from artifacts import load_and_validate_metadata
from deep_embeddings import extract_embedding_from_image, load_efficientnet_backbone
from ecg_io import ECGRecord, load_ecg_mat
from handcrafted_features_v2 import HANDCRAFTED_FEATURES, extract_enhanced_handcrafted_features
from reproducibility import set_global_seed
from scalogram import build_3channel_scalogram, save_scalogram_png


LABEL_NAMES = {0: "Normal", 1: "Arrhythmia", 2: "Other / Unknown"}


class HybridPredictionError(RuntimeError):
    pass


@dataclass
class HybridArtifacts:
    model_name: str
    classifier: Any
    scaler: Any
    pca: Any
    features: list[str]
    metadata: dict[str, Any]
    deep_model: Any
    deep_transform: Any
    device: str
    embedding_dim: int


def assess_risk(predicted_class: int, confidence: float, heart_rate: float) -> str:
    if predicted_class == 1:
        risk = "HIGH" if confidence >= 0.85 else "MEDIUM"
    elif predicted_class == 2:
        risk = "MEDIUM" if confidence >= 0.80 else "LOW"
    else:
        risk = "LOW"

    if confidence < 0.60 and risk == "LOW":
        risk = "MEDIUM"
    if heart_rate > 120 or heart_rate < 40:
        risk = {"LOW": "MEDIUM", "MEDIUM": "HIGH", "HIGH": "HIGH"}[risk]
    return risk


def load_hybrid_artifacts(config, model_name: str | None = None) -> HybridArtifacts:
    model_name = model_name or config.active_model_name
    required_paths = {
        "classifier": config.model_artifact_path(model_name),
        "features": config.feature_list_path(model_name),
        "scaler": config.scaler_path(model_name),
        "pca": config.pca_path(model_name),
        "metadata": config.metadata_path(model_name),
    }
    missing = [f"{name}: {path}" for name, path in required_paths.items() if not path.exists()]
    if missing:
        raise FileNotFoundError(
            f"Missing {model_name} artifacts. Run notebook 05 first:\n" + "\n".join(missing)
        )

    features = list(joblib.load(required_paths["features"]))
    try:
        metadata = load_and_validate_metadata(required_paths["metadata"], features)
    except ValueError as exc:
        raise HybridPredictionError(
            f"Version check failed: Feature-list hash mismatch for model metadata of {model_name}. "
            f"Please verify model artifacts are consistent. Error: {exc}"
        ) from exc

    deep_model, transform, device, expected_dim = load_efficientnet_backbone(model_name)

    metadata_dim = int(metadata.get("embedding_dimension", expected_dim))
    if metadata_dim != expected_dim:
        raise HybridPredictionError(
            f"Metadata embedding dimension {metadata_dim} does not match "
            f"{model_name} dimension {expected_dim}."
        )

    return HybridArtifacts(
        model_name=model_name,
        classifier=joblib.load(required_paths["classifier"]),
        scaler=joblib.load(required_paths["scaler"]),
        pca=joblib.load(required_paths["pca"]),
        features=features,
        metadata=metadata,
        deep_model=deep_model,
        deep_transform=transform,
        device=device,
        embedding_dim=expected_dim,
    )


class HybridECGPredictor:
    def __init__(self, config, model_name: str | None = None):
        self.config = config
        set_global_seed(config.seed)
        self.artifacts = load_hybrid_artifacts(config, model_name=model_name)
        self.runtime_scalogram_dir = (
            config.output_dir / "runtime_scalograms" / self.artifacts.model_name
        )
        self.runtime_scalogram_dir.mkdir(parents=True, exist_ok=True)

    def _build_feature_frame(
        self,
        *,
        ecg: np.ndarray,
        sampling_frequency: int,
        age: int,
        sex: int,
        record_id: str,
        status_callback=None,
    ) -> tuple[pd.DataFrame, np.ndarray, dict[str, float], dict[str, float]]:
        if ecg.ndim != 2:
            raise HybridPredictionError(f"{record_id}: expected 2D ECG data, got {ecg.shape}.")
        if ecg.shape[0] < 12:
            raise HybridPredictionError(
                f"{record_id}: unexpected lead count: {ecg.shape[0]} (expected at least 12 leads)."
            )
        if sampling_frequency != 500:
            raise HybridPredictionError(
                f"{record_id}: unexpected sampling rate: {sampling_frequency} Hz (expected 500 Hz)."
            )

        timings: dict[str, float] = {}
        
        if status_callback:
            status_callback("2/6 Bandpass filtering and CWT scalogram generation")
        started = time.perf_counter()
        image = build_3channel_scalogram(
            ecg,
            fs=sampling_frequency,
            lead_indices=self.config.lead_indices,
            target_size=self.config.model_target_size(self.artifacts.model_name),
        )
        timings["preprocessing_scalogram_seconds"] = time.perf_counter() - started

        if status_callback:
            status_callback("3/6 EfficientNet embedding extraction")
        started = time.perf_counter()
        embedding = extract_embedding_from_image(
            image,
            model=self.artifacts.deep_model,
            transform=self.artifacts.deep_transform,
            device=self.artifacts.device,
            expected_dim=self.artifacts.embedding_dim,
        )
        timings["embedding_seconds"] = time.perf_counter() - started

        if status_callback:
            status_callback("4/6 Handcrafted HRV feature extraction")
        started = time.perf_counter()
        handcrafted = extract_enhanced_handcrafted_features(
            ecg[1],
            fs=sampling_frequency,
        )
        timings["handcrafted_seconds"] = time.perf_counter() - started

        # Explicitly concatenate features into Series and reindex
        handcrafted_series = pd.Series({name: float(handcrafted[name]) for name in HANDCRAFTED_FEATURES})
        deep_series = pd.Series({f"eff_{index:04d}": float(value) for index, value in enumerate(embedding)})
        meta_series = pd.Series({"age": float(age), "sex": float(sex)})
        
        combined_series = pd.concat([handcrafted_series, deep_series, meta_series])
        
        if status_callback:
            status_callback("5/6 Schema validation, scaling, and PCA")
            
        frame = pd.DataFrame([combined_series]).reindex(columns=self.artifacts.features)

        # Assert no NaN/Inf values
        values = frame.to_numpy(dtype=np.float64)
        if not np.isfinite(values).all():
            raise HybridPredictionError(
                f"{record_id}: Schema validation failed - feature vector contains NaN or Inf values after reindexing."
            )
            
        # Assert column order exactly matches the feature list
        if list(frame.columns) != self.artifacts.features:
            raise HybridPredictionError(
                f"{record_id}: Schema validation failed - column order does not match saved feature list."
            )

        return frame, image, handcrafted, timings

    def predict_record(self, record: ECGRecord, status_callback=None) -> dict[str, Any]:
        total_started = time.perf_counter()
        
        if status_callback:
            status_callback("1/6 Loading raw .mat/.hea record")
            
        if not record.mat_path.exists():
            raise FileNotFoundError(f"ECG MAT file not found: {record.mat_path}")
        if not record.hea_path.exists():
            raise FileNotFoundError(f"ECG header file not found: {record.hea_path}")
            
        try:
            ecg = load_ecg_mat(record.mat_path)
        except Exception as exc:
            raise HybridPredictionError(f"Corrupt MAT file or failed to parse: {exc}") from exc
            
        frame, image, handcrafted, timings = self._build_feature_frame(
            ecg=ecg,
            sampling_frequency=record.sampling_frequency,
            age=record.age,
            sex=record.sex,
            record_id=record.record_id,
            status_callback=status_callback,
        )

        if status_callback:
            status_callback("6/6 LightGBM classification and risk assignment")
            
        started = time.perf_counter()
        transformed = self.artifacts.scaler.transform(frame)
        if self.artifacts.pca is not None:
            transformed = self.artifacts.pca.transform(transformed)
        predicted_class = int(self.artifacts.classifier.predict(transformed)[0])

        if hasattr(self.artifacts.classifier, "predict_proba"):
            probabilities = self.artifacts.classifier.predict_proba(transformed)[0]
            classes = [int(value) for value in self.artifacts.classifier.classes_]
            probability_map = {
                LABEL_NAMES.get(cls, str(cls)): float(probability)
                for cls, probability in zip(classes, probabilities)
            }
            confidence = float(probabilities[classes.index(predicted_class)])
        else:
            probability_map = {}
            confidence = 1.0
        timings["classifier_seconds"] = time.perf_counter() - started

        scalogram_path = self.runtime_scalogram_dir / f"{record.record_id}.png"
        save_scalogram_png(image, scalogram_path)

        heart_rate = float(handcrafted["heart_rate"])
        risk = assess_risk(predicted_class, confidence, heart_rate)
        timings["total_seconds"] = time.perf_counter() - total_started

        digits = "".join(character for character in record.record_id if character.isdigit())
        patient_id = int(digits) if digits else record.record_id

        return {
            "patient": patient_id,
            "record_id": record.record_id,
            "prediction": LABEL_NAMES.get(predicted_class, str(predicted_class)),
            "predicted_class": predicted_class,
            "confidence": round(confidence * 100, 2),
            "risk": risk,
            "heart_rate": round(heart_rate, 2),
            "hrv": round(float(handcrafted["hrv"]), 2),
            "sdnn": round(float(handcrafted["sdnn"]), 2),
            "rmssd": round(float(handcrafted["rmssd"]), 2),
            "pnn50": round(float(handcrafted["pnn50"]), 4),
            "age": record.age,
            "sex": record.sex,
            "probabilities": probability_map,
            "scalogram_path": str(scalogram_path),
            "model_name": self.artifacts.model_name,
            "status": "ok",
            "error": "",
            **{key: round(value, 6) for key, value in timings.items()},
        }

    def predict_safe(self, record: ECGRecord) -> dict[str, Any]:
        try:
            return self.predict_record(record)
        except Exception as exc:
            return {
                "patient": record.record_id,
                "record_id": record.record_id,
                "prediction": "",
                "predicted_class": "",
                "confidence": 0.0,
                "risk": "",
                "heart_rate": "",
                "hrv": "",
                "sdnn": "",
                "rmssd": "",
                "pnn50": "",
                "age": record.age,
                "sex": record.sex,
                "probabilities": {},
                "scalogram_path": "",
                "model_name": self.artifacts.model_name,
                "status": "error",
                "error": f"{type(exc).__name__}: {exc}",
                "total_seconds": 0.0,
            }

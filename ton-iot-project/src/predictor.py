"""
src/predictor.py
Load all saved artifacts and run inference on new feature data.
"""
import hashlib
import joblib
import json
import numpy as np
import pandas as pd
from pathlib import Path
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import config


def _compute_hash(feature_list: list) -> str:
    return hashlib.sha256(str(feature_list).encode()).hexdigest()


def load_artifacts(models_dir: str = None) -> dict:
    """
    Load all model artifacts from the models directory.

    Returns
    -------
    dict with keys: 'feature_list', 'label_encoders', 'scaler',
                    'binary_model', 'binary_metadata',
                    'multiclass_model', 'multiclass_metadata'
    """
    if models_dir is None:
        models_dir = config.MODELS_DIR

    mdir = Path(models_dir)
    artifacts = {}

    # Feature list + hash verification
    feature_list_path = mdir / "feature_list.pkl"
    feature_metadata_path = mdir / "feature_metadata.json"
    assert feature_list_path.exists(), f"Missing: {feature_list_path}"
    artifacts['feature_list'] = joblib.load(feature_list_path)

    if feature_metadata_path.exists():
        with open(feature_metadata_path) as f:
            feature_meta = json.load(f)
        expected_hash = feature_meta.get("feature_hash", "")
        actual_hash = _compute_hash(artifacts['feature_list'])
        if expected_hash and expected_hash != actual_hash:
            raise ValueError(
                f"Feature list hash mismatch!\n"
                f"Expected: {expected_hash}\n"
                f"Got: {actual_hash}\n"
                "The loaded feature_list.pkl may not match the stored metadata."
            )
        print("[predictor] Feature hash integrity: OK")

    # Label encoders and scaler
    artifacts['label_encoders'] = joblib.load(mdir / "label_encoders.pkl")
    artifacts['scaler'] = joblib.load(mdir / "scaler.pkl")

    # Binary model
    binary_path = mdir / "best_binary_model.pkl"
    if binary_path.exists():
        artifacts['binary_model'] = joblib.load(binary_path)
        with open(mdir / "binary_model_metadata.json") as f:
            artifacts['binary_metadata'] = json.load(f)
        print(f"[predictor] Binary model loaded: {artifacts['binary_metadata']['model_name']}")

    # Multi-class model
    multiclass_path = mdir / "best_multiclass_model.pkl"
    if multiclass_path.exists():
        artifacts['multiclass_model'] = joblib.load(multiclass_path)
        with open(mdir / "multiclass_model_metadata.json") as f:
            artifacts['multiclass_metadata'] = json.load(f)
        print(f"[predictor] Multiclass model loaded: {artifacts['multiclass_metadata']['model_name']}")

    return artifacts


def predict_binary(X: pd.DataFrame, artifacts: dict) -> dict:
    """
    Run binary classification inference.

    Parameters
    ----------
    X : pd.DataFrame — feature matrix aligned to feature_list
    artifacts : dict — output of load_artifacts()

    Returns
    -------
    dict: {'predictions': array, 'probabilities': array, 'confidence': array}
    """
    feature_list = artifacts['feature_list']
    X = X.reindex(columns=feature_list, fill_value=0)

    model = artifacts['binary_model']
    preds = model.predict(X)
    probas = model.predict_proba(X)
    confidence = probas.max(axis=1)

    return {
        "predictions": preds,
        "probabilities": probas,
        "confidence": confidence,
        "labels": ["benign", "attack"],
    }


def predict_multiclass(X: pd.DataFrame, artifacts: dict) -> dict:
    """
    Run multi-class attack type classification.

    Parameters
    ----------
    X : pd.DataFrame — feature matrix aligned to feature_list
    artifacts : dict — output of load_artifacts()

    Returns
    -------
    dict: {'predictions': array, 'probabilities': array, 'confidence': array, 'classes': list}
    """
    feature_list = artifacts['feature_list']
    X = X.reindex(columns=feature_list, fill_value=0)

    model = artifacts['multiclass_model']
    preds = model.predict(X)
    probas = model.predict_proba(X)
    confidence = probas.max(axis=1)

    classes = list(model.classes_)

    return {
        "predictions": preds,
        "probabilities": probas,
        "confidence": confidence,
        "classes": classes,
    }

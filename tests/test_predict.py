from __future__ import annotations

import sys
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_DIR / "src"
sys.path.insert(0, str(PROJECT_DIR))
sys.path.insert(0, str(SRC_DIR))

from config import CONFIG
from ecg_io import ECGRecord, discover_records
from hybrid_predictor import HybridECGPredictor


def test_active_model_predictions_are_valid():
    model_name = CONFIG.active_model_name
    predictor = HybridECGPredictor(CONFIG, model_name=model_name)
    records = discover_records(CONFIG.raw_dataset_dir, limit=3)
    assert len(records) == 3

    for record in records:
        result = predictor.predict_record(record)
        assert result["status"] == "ok"
        assert result["prediction"] in {"Normal", "Arrhythmia", "Other / Unknown"}
        assert 0.0 <= result["confidence"] <= 100.0
        assert result["risk"] in {"LOW", "MEDIUM", "HIGH"}
        assert np.isfinite(result["total_seconds"])
        assert Path(result["scalogram_path"]).exists()
        assert result["model_name"] == model_name


def test_b0_predictions_are_valid():
    predictor = HybridECGPredictor(CONFIG, model_name=CONFIG.prototype_model_name)
    records = discover_records(CONFIG.raw_dataset_dir, limit=3)
    assert len(records) == 3

    for record in records:
        result = predictor.predict_record(record)
        assert result["status"] == "ok"
        assert result["prediction"] in {"Normal", "Arrhythmia", "Other / Unknown"}
        assert 0.0 <= result["confidence"] <= 100.0
        assert result["risk"] in {"LOW", "MEDIUM", "HIGH"}
        assert np.isfinite(result["total_seconds"])
        assert Path(result["scalogram_path"]).exists()


def test_bad_mat_path_is_isolated():
    predictor = HybridECGPredictor(CONFIG, model_name=CONFIG.active_model_name)
    record = discover_records(CONFIG.raw_dataset_dir, limit=1)[0]
    bad_record = ECGRecord(
        record_id="BROKEN_RECORD",
        mat_path=PROJECT_DIR / "missing.mat",
        hea_path=record.hea_path,
        age=record.age,
        sex=record.sex,
        dx_codes=record.dx_codes,
        label=record.label,
        label_name=record.label_name,
        sampling_frequency=record.sampling_frequency,
        n_leads=record.n_leads,
        n_samples=record.n_samples,
    )
    result = predictor.predict_safe(bad_record)
    assert result["status"] == "error"
    assert "missing.mat" in result["error"]


def test_predict_script_integration():
    # Run predict.py as a script via subprocess
    test_csv = PROJECT_DIR / "test_predictions.csv"
    if test_csv.exists():
        test_csv.unlink()

    completed = subprocess.run(
        [sys.executable, str(PROJECT_DIR / "predict.py"), "--limit", "3", "--output", str(test_csv)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, f"predict.py failed: {completed.stdout}\n{completed.stderr}"
    assert test_csv.exists(), "test_predictions.csv was not created"

    # Read and validate contents
    df = pd.read_csv(test_csv)
    assert len(df) == 3
    assert "status" in df.columns
    assert "prediction" in df.columns
    assert "confidence" in df.columns
    assert "risk" in df.columns

    # Verify no NaN values for successful predictions
    success_rows = df[df["status"] == "ok"]
    if not success_rows.empty:
        assert not success_rows["prediction"].isnull().any()
        assert not success_rows["confidence"].isnull().any()
        assert not success_rows["risk"].isnull().any()

    # Clean up
    test_csv.unlink()



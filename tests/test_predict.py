from __future__ import annotations

import sys
from pathlib import Path

import numpy as np


PROJECT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_DIR / "src"
sys.path.insert(0, str(PROJECT_DIR))
sys.path.insert(0, str(SRC_DIR))

from config import CONFIG
from ecg_io import ECGRecord, discover_records
from hybrid_predictor import HybridECGPredictor


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
    predictor = HybridECGPredictor(CONFIG, model_name=CONFIG.prototype_model_name)
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


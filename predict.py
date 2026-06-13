from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent
SRC_DIR = PROJECT_DIR / "src"
sys.path.insert(0, str(PROJECT_DIR))
sys.path.insert(0, str(SRC_DIR))

from config import CONFIG
from ecg_io import discover_records
from hybrid_predictor import HybridECGPredictor


def explain_result(result: dict) -> str:
    if result.get("status") != "ok":
        return result.get("error", "Prediction failed.")
    try:
        from explain import explain_prediction

        return explain_prediction(
            cls=int(result["predicted_class"]),
            confidence=float(result["confidence"]) / 100.0,
            hr=float(result["heart_rate"]),
            hrv=float(result["hrv"]),
            age=int(result["age"]),
            sex_code=int(result["sex"]),
            risk=str(result["risk"]),
        )
    except Exception:
        return (
            f"{result['prediction']} predicted with {result['confidence']:.1f}% "
            f"confidence. Assigned risk: {result['risk']}."
        )


def run_predictions(
    *,
    model_name: str,
    limit: int,
    output_path: Path,
) -> pd.DataFrame:
    predictor = HybridECGPredictor(CONFIG, model_name=model_name)
    records = discover_records(CONFIG.raw_dataset_dir, limit=limit)

    rows = []
    for index, record in enumerate(records, start=1):
        result = predictor.predict_safe(record)
        result["explanation"] = explain_result(result)
        result["probabilities"] = json.dumps(result.get("probabilities", {}), sort_keys=True)
        rows.append(result)
        print(
            f"[{index}/{len(records)}] {record.record_id}: "
            f"{result['status']} {result.get('prediction', '')} "
            f"{result.get('confidence', 0)}%"
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows)
    frame.to_csv(output_path, index=False)
    return frame


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Hybrid ECG prediction pipeline")
    parser.add_argument("--model-name", default=CONFIG.active_model_name)
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_DIR / "predictions.csv",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    frame = run_predictions(
        model_name=args.model_name,
        limit=args.limit,
        output_path=args.output,
    )
    errors = int((frame["status"] == "error").sum()) if not frame.empty else 0
    print(f"Saved {len(frame)} predictions to {args.output}; errors={errors}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())


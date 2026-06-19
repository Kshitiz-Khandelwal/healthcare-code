"""
scripts/validate_all.py
Validates that all required artifacts exist and have non-zero size.
Also verifies feature hash integrity between feature_metadata.json and feature_list.pkl.

Run from the project root:
    python scripts/validate_all.py
"""
import json
import hashlib
import os
import sys
import joblib
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

REQUIRED_ARTIFACTS = [
    "outputs/models/feature_list.pkl",
    "outputs/models/label_encoders.pkl",
    "outputs/models/scaler.pkl",
    "outputs/models/feature_metadata.json",
    "outputs/models/best_binary_model.pkl",
    "outputs/models/binary_model_metadata.json",
    "outputs/models/best_multiclass_model.pkl",
    "outputs/models/multiclass_model_metadata.json",
    "outputs/reports/TON_IoT_Final_Report.md",
    "outputs/reports/sample_predictions.csv",
    "outputs/plots/label_distribution.png",
    "outputs/plots/type_distribution.png",
    "outputs/plots/correlation_heatmap.png",
    "outputs/plots/confusion_matrix_binary_LGBMClassifier.png",
    "outputs/plots/confusion_matrix_multiclass.png",
    "outputs/plots/feature_importance_multiclass.png",
    "outputs/plots/roc_curve_binary.png",
]


def compute_hash(feature_list):
    return hashlib.sha256(str(feature_list).encode()).hexdigest()


def main():
    print("=" * 60)
    print("TON_IoT Artifact Validation")
    print("=" * 60)

    all_passed = True

    # Check all required artifact files
    for artifact_path in REQUIRED_ARTIFACTS:
        p = Path(artifact_path)
        exists = p.exists()
        size_ok = p.stat().st_size > 0 if exists else False
        status = "[OK]" if (exists and size_ok) else "[MISSING/EMPTY]"
        if not (exists and size_ok):
            all_passed = False
        print(f"  {status}  {artifact_path}")

    # Feature hash integrity check
    print()
    print("Feature Hash Integrity Check:")
    feature_list_path = Path("outputs/models/feature_list.pkl")
    feature_meta_path = Path("outputs/models/feature_metadata.json")

    if feature_list_path.exists() and feature_meta_path.exists():
        feature_list = joblib.load(feature_list_path)
        actual_hash = compute_hash(feature_list)
        with open(feature_meta_path) as f:
            meta = json.load(f)
        expected_hash = meta.get("feature_hash", "")
        if actual_hash == expected_hash:
            print(f"  [OK] Hash match: {actual_hash[:16]}...")
        else:
            print(f"  [ERROR] HASH MISMATCH!")
            print(f"    Expected: {expected_hash}")
            print(f"    Got:      {actual_hash}")
            all_passed = False
    else:
        print("  [ERROR] Cannot check — feature_list.pkl or feature_metadata.json missing")
        all_passed = False

    print()
    if all_passed:
        print("ALL CHECKS PASSED")
    else:
        print("SOME CHECKS FAILED — see above")
        sys.exit(1)


if __name__ == "__main__":
    main()

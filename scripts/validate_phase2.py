from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from config import CONFIG


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        return [], []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        return list(reader.fieldnames or []), rows


def main() -> int:
    model_name = CONFIG.production_model_name
    expected_rows = CONFIG.production_max_records
    expected_deep = CONFIG.production_embedding_dim

    manifest_path = CONFIG.scalogram_manifest_path(model_name)
    manifest_columns, manifest_rows = read_csv(manifest_path)
    missing_images = [
        row.get("image_path", "")
        for row in manifest_rows
        if not Path(row.get("image_path", "")).exists()
    ]

    hybrid_columns, hybrid_rows = read_csv(CONFIG.hybrid_feature_path(model_name))
    deep_columns = [column for column in hybrid_columns if column.startswith("eff_")]

    results_path = CONFIG.result_dir / f"hybrid_comparison_{model_name}.csv"
    _, result_rows = read_csv(results_path)

    artifact_checks = {
        name: path.exists()
        for name, path in {
            "classifier": CONFIG.model_artifact_path(model_name),
            "feature_list": CONFIG.feature_list_path(model_name),
            "scaler": CONFIG.scaler_path(model_name),
            "pca": CONFIG.pca_path(model_name),
            "metadata": CONFIG.metadata_path(model_name),
        }.items()
    }

    checks = {
        "manifest_exists": manifest_path.exists(),
        "manifest_rows_1000": len(manifest_rows) == expected_rows,
        "all_manifest_images_exist": len(missing_images) == 0,
        "hybrid_exists": CONFIG.hybrid_feature_path(model_name).exists(),
        "hybrid_rows_1000": len(hybrid_rows) == expected_rows,
        "deep_feature_count_1792": len(deep_columns) == expected_deep,
        "comparison_results_exist": results_path.exists() and bool(result_rows),
        **{f"artifact_{name}": value for name, value in artifact_checks.items()},
    }
    passed = all(checks.values())

    report = {
        "phase": 2,
        "model_name": model_name,
        "passed": passed,
        "checks": checks,
        "observed": {
            "manifest_path": str(manifest_path),
            "manifest_rows": len(manifest_rows),
            "missing_images": len(missing_images),
            "hybrid_rows": len(hybrid_rows),
            "hybrid_columns": len(hybrid_columns),
            "deep_feature_columns": len(deep_columns),
            "results_rows": result_rows,
        },
    }

    report_path = CONFIG.log_dir / "phase2_acceptance_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"\nSaved: {report_path}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from config import CONFIG


def run_validation_script(script_name: str) -> dict:
    script = PROJECT_DIR / "scripts" / script_name
    completed = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0 and script_name == "validate_phase1.py":
        raise RuntimeError(completed.stdout + completed.stderr)

    payload = completed.stdout.strip()
    decoder = json.JSONDecoder()
    report, _ = decoder.raw_decode(payload)
    return report


def run_predictor_tests() -> dict:
    tests_dir = PROJECT_DIR / "tests"
    sys.path.insert(0, str(tests_dir))
    import test_predict

    test_predict.test_active_model_predictions_are_valid()
    test_predict.test_b0_predictions_are_valid()
    test_predict.test_bad_mat_path_is_isolated()
    return {"predictor_tests_passed": 3}


def artifact_status(model_name: str) -> dict[str, bool]:
    paths = {
        "classifier": CONFIG.model_artifact_path(model_name),
        "feature_list": CONFIG.feature_list_path(model_name),
        "scaler": CONFIG.scaler_path(model_name),
        "pca": CONFIG.pca_path(model_name),
        "metadata": CONFIG.metadata_path(model_name),
    }
    return {name: path.exists() for name, path in paths.items()}


def load_metadata_metrics(model_name: str) -> dict:
    path = CONFIG.metadata_path(model_name)
    if not path.exists():
        return {}
    metadata = json.loads(path.read_text(encoding="utf-8"))
    return metadata.get("metrics", {})


def compare_models(b0: dict, b4: dict) -> dict:
    b0_recall = b0.get("per_class_recall", {})
    b4_recall = b4.get("per_class_recall", {})
    macro_delta = float(b4.get("test_macro_f1", 0)) - float(b0.get("test_macro_f1", 0))
    recall_deltas = {
        label: float(b4_recall.get(label, 0)) - float(b0_recall.get(label, 0))
        for label in sorted(set(b0_recall) | set(b4_recall))
    }
    minority_regressions = [
        label for label, delta in recall_deltas.items() if delta < 0
    ]
    return {
        "accuracy_delta": float(b4.get("test_accuracy", 0)) - float(b0.get("test_accuracy", 0)),
        "macro_f1_delta": macro_delta,
        "per_class_recall_delta": recall_deltas,
        "passes_master_prompt_gate": macro_delta >= 0,
        "minority_recall_regressions": minority_regressions,
        "human_review_recommended": macro_delta < 0 or bool(minority_regressions),
    }


def main() -> int:
    import torch

    phase1 = run_validation_script("validate_phase1.py")
    phase2 = run_validation_script("validate_phase2.py")
    tests = run_predictor_tests()

    b0_metrics = load_metadata_metrics(CONFIG.prototype_model_name)
    b4_metrics = load_metadata_metrics(CONFIG.production_model_name)
    comparison = compare_models(b0_metrics, b4_metrics)

    predictions_path = PROJECT_DIR / "predictions.csv"
    production_artifacts = artifact_status(CONFIG.production_model_name)
    b4_ready = phase2.get("passed", False) and all(production_artifacts.values())

    blockers = []
    if not b4_ready:
        blockers.append("Production B4 acceptance checks did not fully pass.")
    if comparison["human_review_recommended"]:
        blockers.append(
            "B4-vs-B0 comparison flagged recall regressions on: "
            + ", ".join(comparison["minority_recall_regressions"])
        )

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "environment": {
            "python": sys.version.split()[0],
            "cuda_available": torch.cuda.is_available(),
            "active_profile": CONFIG.active_profile,
            "active_model_name": CONFIG.active_model_name,
        },
        "phase1_acceptance": phase1,
        "phase2_acceptance": phase2,
        "predictor_tests": tests,
        "prototype_metrics": b0_metrics,
        "production_metrics": b4_metrics,
        "b4_vs_b0_comparison": comparison,
        "production_artifacts": production_artifacts,
        "predictions_csv_exists": predictions_path.exists(),
        "blockers": blockers or ["None"],
        "sign_off": {
            "phase1_passed": phase1.get("passed", False),
            "phase2_passed": phase2.get("passed", False),
            "integration_tests_passed": True,
            "b4_improves_macro_f1": comparison["passes_master_prompt_gate"],
            "ready_for_dashboard_demo": b4_ready and predictions_path.exists(),
        },
    }

    report_path = CONFIG.log_dir / "final_validation_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    markdown_path = CONFIG.log_dir / "final_validation_report.md"
    markdown_path.write_text(render_markdown(report), encoding="utf-8")

    print(json.dumps(report, indent=2))
    print(f"\nSaved: {report_path}")
    print(f"Saved: {markdown_path}")
    passed = (
        report["sign_off"]["phase1_passed"]
        and report["sign_off"]["phase2_passed"]
        and report["sign_off"]["integration_tests_passed"]
    )
    return 0 if passed else 1


def render_markdown(report: dict) -> str:
    b0 = report["prototype_metrics"]
    b4 = report["production_metrics"]
    cmp_ = report["b4_vs_b0_comparison"]
    blockers = report.get("blockers") or ["None"]
    blocker_lines = "\n".join(f"- {item}" for item in blockers)

    return f"""# Final Validation Report

Generated: {report["generated_at_utc"]}

## Environment

- Python: {report["environment"]["python"]}
- CUDA available: {report["environment"]["cuda_available"]}
- Active profile: `{report["environment"]["active_profile"]}`
- Active model: `{report["environment"]["active_model_name"]}`

## Phase 1 — EfficientNet-B0 (300 records)

- Passed: **{report["sign_off"]["phase1_passed"]}**
- Test accuracy: {float(b0.get("test_accuracy", 0)):.4f}
- Test macro-F1: {float(b0.get("test_macro_f1", 0)):.4f}

## Phase 2 — EfficientNet-B4 (1000 records, 380×380)

- Passed: **{report["sign_off"]["phase2_passed"]}**
- Test accuracy: {float(b4.get("test_accuracy", 0)):.4f}
- Test macro-F1: {float(b4.get("test_macro_f1", 0)):.4f}
- Recall — Arrhythmia: {float(b4.get("per_class_recall", {}).get("Arrhythmia", 0)):.3f}
- Recall — Normal: {float(b4.get("per_class_recall", {}).get("Normal", 0)):.3f}
- Recall — Other / Unknown: {float(b4.get("per_class_recall", {}).get("Other / Unknown", 0)):.3f}

## B4 vs B0 Comparison

| Metric | B0 | B4 | Delta |
|---|---|---|---|
| Test accuracy | {float(b0.get("test_accuracy", 0)):.4f} | {float(b4.get("test_accuracy", 0)):.4f} | {cmp_["accuracy_delta"]:+.4f} |
| Test macro-F1 | {float(b0.get("test_macro_f1", 0)):.4f} | {float(b4.get("test_macro_f1", 0)):.4f} | {cmp_["macro_f1_delta"]:+.4f} |

**Master-prompt gate (macro-F1 must not decrease):** {"PASS" if cmp_["passes_master_prompt_gate"] else "FAIL — human review required"}

## Integration Tests

- Predictor regression tests passed: {report["predictor_tests"]["predictor_tests_passed"]}
- `predictions.csv` present: {report["predictions_csv_exists"]}
- Dashboard demo ready: {report["sign_off"]["ready_for_dashboard_demo"]}

## Notes

{blocker_lines}
"""


if __name__ == "__main__":
    raise SystemExit(main())

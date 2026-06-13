# Final Validation Report

Generated: 2026-06-13T22:51:47.689664+00:00

## Environment

- Python: 3.14.6
- CUDA available: False
- Active profile: `production`
- Active model: `efficientnet_b4`

## Phase 1 — EfficientNet-B0 (300 records)

- Passed: **True**
- Test accuracy: 0.8833
- Test macro-F1: 0.8000

## Phase 2 — EfficientNet-B4 (1000 records, 380×380)

- Passed: **True**
- Test accuracy: 0.9200
- Test macro-F1: 0.8952
- Recall — Arrhythmia: 0.956
- Recall — Normal: 0.743
- Recall — Other / Unknown: 0.966

## B4 vs B0 Comparison

| Metric | B0 | B4 | Delta |
|---|---|---|---|
| Test accuracy | 0.8833 | 0.9200 | +0.0367 |
| Test macro-F1 | 0.8000 | 0.8952 | +0.0952 |

**Master-prompt gate (macro-F1 must not decrease):** PASS

## Integration Tests

- Predictor regression tests passed: 3
- `predictions.csv` present: True
- Dashboard demo ready: True

## Notes

- B4-vs-B0 comparison flagged recall regressions on: Other / Unknown

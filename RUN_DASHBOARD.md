# ECG Dashboard Setup & Troubleshooting

## Quick Start

### Terminal 1: Start the Prediction Pipeline
```bash
python predict.py
```
This generates live predictions and saves them to `predictions.csv`.

### Terminal 2: Start the Dashboard
```bash
streamlit run dashboard.py
```
The dashboard will open in your browser at `http://localhost:8501`

---

## Verification Checklist

✓ **Data Loading:** Run this to verify data is ready:
```bash
python -c "import pandas as pd; df = pd.read_csv('predictions.csv'); print(f'Ready: {len(df)} records')"
```

✓ **Full Test Suite:** Run this to verify all dashboard components:
```bash
python test_dashboard.py
```

---

## What Each File Does

| File | Purpose |
|------|---------|
| `dashboard.py` | Streamlit web interface for ECG monitoring |
| `predict.py` | Generates predictions and saves to `predictions.csv` |
| `predictions.csv` | Live data source for the dashboard |
| `test_dashboard.py` | Automated test suite (diagnostic tool) |

---

## Key Data Files

- **predictions.csv** ← Dashboard reads from here
- **session_results.csv** ← Legacy format (not used by current dashboard)
- **ecg_dataset.csv** ← Source ECG records for predictions

---

## Dashboard Displays

The dashboard shows in real-time:
- 22 patient records currently loaded
- Risk distribution: 10 HIGH, 8 MEDIUM, 4 LOW
- Prediction breakdown: 14 Arrhythmia, 5 Normal, 3 Other/Unknown
- Interactive charts: Risk vs HR/HRV, Confidence trends
- Patient alerts sorted by risk level
- AI explanations for HIGH/MEDIUM risk cases

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No data" message | Run `python predict.py` first to generate predictions.csv |
| Charts don't display | Run `python test_dashboard.py` to diagnose |
| Dashboard won't start | Check `streamlit` is installed: `pip install streamlit` |
| Data looks stale | Restart both scripts; dashboard refreshes every 3 seconds |

---

## For Developers

- Dashboard auto-refreshes every 3 seconds
- Required columns: `patient`, `prediction`, `confidence`, `risk`, `heart_rate`, `hrv`, `explanation`
- Risk levels: HIGH (red), MEDIUM (yellow), LOW (green)
- Predictions: Arrhythmia, Normal, Other/Unknown

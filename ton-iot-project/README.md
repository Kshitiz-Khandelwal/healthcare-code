# TON_IoT Network Intrusion Detection

## Project Overview

End-to-end machine learning pipeline for IoT/IIoT network intrusion detection using the TON_IoT dataset (UNSW Canberra). Mirrors the healthcare ECG classification pipeline in structure, discipline, and documentation standards.

**Dataset**: TON_IoT Network Dataset — 211,044 network flow records × 44 features  
**Source**: https://research.unsw.edu.au/projects/toniot-datasets  
**License**: CC BY 4.0

---

## Dataset Location

```
C:\Users\Admin\Desktop\Kshitiz\thon iot dataset\train_test_network.csv
```

---

## Python Environment Setup

```bash
# Use the existing venv (same as healthcare project)
C:\Users\Admin\Desktop\Kshitiz\venv\Scripts\python.exe -m pip install -r requirements.txt
```

Or create a fresh venv:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

---

## Notebook Execution Order

Run notebooks in this exact order, one at a time:

1. `notebooks/01_data_exploration.ipynb` — Dataset audit and class distribution
2. `notebooks/02_feature_engineering.ipynb` — Feature engineering + artifact saving
3. `notebooks/03_binary_classification.ipynb` — Binary (benign vs attack) classifiers
4. `notebooks/04_multiclass_classification.ipynb` — Multi-class (attack type) classifiers
5. `notebooks/05_model_comparison_and_report.ipynb` — Final comparison + report generation

**Before running each notebook**: Use `Kernel > Restart & Run All` to ensure a clean run.

---

## Project Structure

```
ton-iot-project/
├── README.md               ← this file
├── PROJECT_CONTEXT.md      ← dataset schema, attack taxonomy, feature rationale
├── ARCHITECTURE.md         ← system layout, src/ module API
├── DECISIONS.md            ← engineering and design decisions
├── TASKS.md                ← phase-by-phase checklist
├── config.py               ← all configuration values (SEED, paths, params)
├── requirements.txt        ← Python dependencies
├── notebooks/              ← Jupyter notebooks (run in order)
├── src/                    ← Modular Python library
├── scripts/                ← Validation and utility scripts
├── tests/                  ← Integration tests
├── outputs/
│   ├── models/             ← Saved model artifacts (.pkl, .json)
│   ├── plots/              ← Generated charts and confusion matrices
│   └── reports/            ← Markdown reports and prediction CSVs
└── ton-iot-dashboard-build/ ← Next.js dashboard (Vercel)
```

---

## Key Configuration

All configuration lives in `config.py`:
- `SEED = 42`
- `DATA_PATH` — path to raw CSV
- `MAX_ROWS = None` — set to integer for smoke tests
- `TEST_SIZE = 0.20` — 80/20 stratified split
- `BINARY_TARGET = "label"`, `MULTICLASS_TARGET = "type"`

---

## Quick Results Reference

*(Filled after Phase 5 completes)*

| Metric | Binary (Best) | Multi-Class (Best) |
|---|---:|---:|
| Model | TBD | TBD |
| Test Accuracy | TBD | TBD |
| Test Macro-F1 | TBD | TBD |
| Test Weighted-F1 | TBD | TBD |
| Test AUC | TBD | TBD |

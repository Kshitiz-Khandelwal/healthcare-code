# TON_IoT Network Intrusion Detection — Codex Master Prompt (v1)

*Copy and paste the entire prompt below into a new Codex/AI session when you start your work.*

---

# Directives for TON_IoT Intrusion Detection Pipeline Implementation

You are a senior pair-programming AI coding assistant. We are developing an end-to-end machine learning pipeline for network intrusion detection using the **TON_IoT dataset** (UNSW Canberra). The dataset contains IoT/IIoT network traffic flows with both a binary label (benign vs. attack) and a multi-class attack type label.

**This project mirrors the structure of the Healthcare ECG classification project** (`ecg_pipeline_master_prompt_v2.md`). Use that project's discipline, guardrails, and documentation standards as your benchmark.

---

## General Rules (apply across ALL phases)

- All configuration values (`SEED`, `DATA_PATH`, `MAX_ROWS`, `TEST_SIZE`, output paths) must live in `config.py` only. Never hardcode them inside notebooks or scripts.
- `SEED = 42` must be set for `random`, `numpy`, and `scikit-learn` (`random_state`) in every notebook and script. LightGBM and XGBoost must also use `random_state=42`.
- `n_jobs=1` must be used in all sklearn/LightGBM/XGBoost calls to prevent parallel execution issues.
- Never mark a checklist item `[x]` in `TASKS.md` unless the corresponding run actually executed and produced the referenced artifact/metric. Do not fabricate numbers.
- Commit after each phase with a descriptive message. Do NOT commit large binary artifacts (`.pkl`, large feature CSVs) — confirm `.gitignore` covers `outputs/models/*.pkl` and `outputs/*.csv`.
- Read **Guardrails & Escalation Rules** at the end of this prompt before starting.

---

## 📂 Phase 0: Load Project Context & Verify Environment

1. Locate and read these files in the project root:
   - `README.md` — dataset path, notebook order, setup.
   - `PROJECT_CONTEXT.md` — dataset schema, attack taxonomy, feature engineering rationale.
   - `ARCHITECTURE.md` — system layout, `src/` module API.
   - `DECISIONS.md` — engineering and design justifications.
   - `TASKS.md` — completed items and targets.
   - `config.py` — all configuration values.

2. **Environment check**:
   - Confirm Python version ≥ 3.9.
   - Confirm `pandas`, `scikit-learn`, `lightgbm`, `xgboost`, `shap`, `matplotlib`, `seaborn`, `joblib` are importable.
   - Confirm `SEED = 42` is applied consistently.

3. **Directory layout check**:
   - Confirm `outputs/models/`, `outputs/plots/`, `outputs/reports/` exist (create if missing).
   - Confirm naming conventions for versioned artifacts are documented in `ARCHITECTURE.md`.

**Definition of Done — Phase 0**: All context files read and summarized in your working notes; environment check passed; directory structure confirmed.

---

## 🔍 Phase 1: Data Exploration & Audit

**Notebook**: `notebooks/01_data_exploration.ipynb`

1. Load `train_test_network.csv` from `config.DATA_PATH`.
2. Confirm shape: expect ~211,044 rows × 44 columns.
3. Display dtypes, `head(5)`, and `describe()` for numeric columns.
4. Count and display missing values per column. The dataset uses `-` as a placeholder for missing categoricals. Document this.
5. Plot and save `label` distribution (binary: 0=benign, 1=attack) to `outputs/plots/label_distribution.png`.
6. Plot and save `type` distribution (multi-class: all attack types + normal) to `outputs/plots/type_distribution.png`.
7. Plot and save correlation heatmap for numeric columns to `outputs/plots/correlation_heatmap.png`.
8. List unique values for: `proto`, `service`, `conn_state`.
9. List cardinality (unique count) for all columns. Flag high-cardinality columns.
10. Print 5 sample rows per `type` category.
11. Generate and save `outputs/reports/data_audit.md`.

**Acceptance Checks**:
- No notebook cell errors.
- Exact class counts per `type` documented.
- Missing value pattern documented.
- All 3 plots saved.
- `data_audit.md` saved.

---

## 🔧 Phase 2: Feature Engineering

**Notebook**: `notebooks/02_feature_engineering.ipynb`

**Columns to DROP** (before encoding):
- `src_ip`, `dst_ip` — raw IPs not generalizable.
- `dns_query`, `ssl_subject`, `ssl_issuer`, `http_uri`, `http_user_agent`, `ssl_cipher`, `weird_addl` — extreme cardinality.
- `ssl_version`, `http_method`, `http_version`, `http_orig_mime_types`, `http_resp_mime_types` — complex encoding, low predictive value in initial model.

**Missing value handling**:
- Replace all `-` with `NaN`.
- Fill numeric NaN with column median (fit on train only).
- Fill categorical NaN with `"unknown"`.

**Categorical encoding**:
- `proto`, `service`, `conn_state`, `weird_name` → `LabelEncoder()` (fit on train only).

**Boolean field encoding**:
- `dns_AA`, `dns_RD`, `dns_RA`, `dns_rejected`, `ssl_resumed`, `ssl_established`, `weird_notice` → treat `-` as 0, `T`/`True` as 1, `F`/`False` as 0.

**Numeric transformations**:
- `log1p` transform: `duration`, `src_bytes`, `dst_bytes`, `src_ip_bytes`, `dst_ip_bytes`, `src_pkts`, `dst_pkts`, `missed_bytes`.

**Derived features to CREATE**:
- `is_well_known_src_port`: `int(src_port < 1024)` — privileged source port.
- `is_well_known_dst_port`: `int(dst_port < 1024)` — privileged destination port.
- `byte_ratio`: `src_bytes / (dst_bytes + 1)` — traffic asymmetry.
- `avg_src_pkt_size`: `src_bytes / (src_pkts + 1)` — normalized source packet size.
- `avg_dst_pkt_size`: `dst_bytes / (dst_pkts + 1)` — normalized destination packet size.

**Scaling**:
- Fit `StandardScaler` on train split only. Transform train and test.

**Train/Test Split**:
- Stratified 80/20 split using `train_test_split(stratify=y, test_size=0.20, random_state=SEED)`.
- Apply separately for binary (stratify on `label`) and multi-class (stratify on `type`).

**Artifacts to save**:
- `outputs/feature_matrix_binary.csv` — feature matrix + `label` column.
- `outputs/feature_matrix_multiclass.csv` — feature matrix + `type` column.
- `outputs/models/feature_list.pkl` — exact list of feature column names in order.
- `outputs/models/label_encoders.pkl` — dict of fitted LabelEncoder objects.
- `outputs/models/scaler.pkl` — fitted StandardScaler.
- `outputs/models/feature_metadata.json` — feature count, encoding summary, hash of feature list.

**Feature list hash**: Use `hashlib.sha256(str(feature_list).encode()).hexdigest()` — save in `feature_metadata.json`.

**Acceptance Checks**:
- Zero NaN/Inf in final feature matrix (assert this explicitly).
- Feature count ≥ 20.
- Feature list hash saved.
- All artifacts saved.

---

## 🤖 Phase 3: Binary Classification

**Notebook**: `notebooks/03_binary_classification.ipynb`

**Task**: Classify each flow as benign (`label=0`) or attack (`label=1`).

**Load** feature matrix from `outputs/feature_matrix_binary.csv`. Load feature list from `outputs/models/feature_list.pkl`. Assert feature columns match.

**Models to train** (in this order):
1. `LogisticRegression(random_state=42, max_iter=1000, class_weight='balanced', n_jobs=1)`
2. `RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced', n_jobs=1)`
3. `XGBClassifier(n_estimators=150, learning_rate=0.05, max_depth=6, random_state=42, n_jobs=1, eval_metric='logloss')`
4. `LGBMClassifier(n_estimators=150, learning_rate=0.05, max_depth=6, random_state=42, n_jobs=1, is_unbalance=True, verbose=-1)`

**Evaluation**:
- 5-fold stratified CV (`StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`).
- Compute: CV Accuracy, CV F1 (binary `pos_label=1`), CV AUC.
- Then evaluate each model on the held-out 20% test set: Accuracy, Precision, Recall, F1, AUC.

**Primary metric for model selection**: held-out F1 (attack class).

**Best model**:
- Save as `outputs/models/best_binary_model.pkl`.
- Save `outputs/models/binary_model_metadata.json` containing: training timestamp, seed, best model class name, test accuracy, test F1, test AUC, dataset size, feature count, feature list hash.

**Plots to save**:
- Confusion matrix for each model: `outputs/plots/confusion_matrix_binary_{model_name}.png`.
- ROC curve for all models on test set: `outputs/plots/roc_curve_binary.png`.

**Acceptance Checks**:
- All 4 models trained without error.
- Best model selected by held-out F1 and saved.
- `binary_model_metadata.json` contains feature hash.
- All plots saved.

---

## 🎯 Phase 4: Multi-Class Classification

**Notebook**: `notebooks/04_multiclass_classification.ipynb`

**Task**: Classify each flow into its attack type (`type` column).

**Load** feature matrix from `outputs/feature_matrix_multiclass.csv`. Load feature list. Assert columns match.

**Models**: Same 4 as Phase 3, but with multi-class support.
- For XGBoost: use `objective='multi:softmax'`, `num_class=<n_classes>`.
- For LightGBM: use `objective='multiclass'`, `num_class=<n_classes>`.
- For LR and RF: multi-class is native.

**Evaluation**:
- 5-fold stratified CV.
- Compute: CV Accuracy, CV Macro-F1, CV Weighted-F1.
- Held-out 20% test: Accuracy, Macro-F1, Weighted-F1, per-class Precision/Recall/F1.

**Primary metric**: held-out **Macro-F1** (analogous to ECG project).

**Best model**:
- Save as `outputs/models/best_multiclass_model.pkl`.
- Save `outputs/models/multiclass_model_metadata.json`.

**Plots to save**:
- Confusion matrix heatmap (best model): `outputs/plots/confusion_matrix_multiclass.png`.
- Feature importance (LightGBM, top 20): `outputs/plots/feature_importance_multiclass.png`.
- Per-class F1 bar chart: `outputs/plots/per_class_f1_multiclass.png`.

**Benchmark vs. Phase 3**: Record how the multi-class best model F1 compares to the binary model on the multi-class task.

**Acceptance Checks**:
- Full per-class classification report printed and saved.
- Confusion matrix heatmap saved.
- Feature importance saved.
- Best model metadata JSON saved with feature hash.
- Sample predictions CSV (20 rows) saved to `outputs/reports/sample_predictions.csv`.

---

## 📊 Phase 5: Model Comparison & Final Report

**Notebook**: `notebooks/05_model_comparison_and_report.ipynb`

1. Load all model results from Phases 3 and 4.
2. Build comparison table: 4 models × {CV Accuracy, CV Macro-F1, Test Accuracy, Test Macro-F1, Test AUC, Runtime}.
3. Render final confusion matrices for the best binary and multi-class models.
4. Render ROC curve + Precision-Recall curve (best models).
5. Render feature importance chart (top 20 features from best multi-class model).
6. Render attack type distribution chart.
7. Render model comparison table as a PNG.
8. Generate `outputs/reports/TON_IoT_Final_Report.md` — comprehensive Markdown report.
9. Ensure `outputs/reports/sample_predictions.csv` is present and has ≥ 20 rows.

**Acceptance Checks**:
- `TON_IoT_Final_Report.md` generated without error.
- All comparison charts saved.
- `sample_predictions.csv` exists.

---

## 🌐 Phase 6: Next.js Dashboard

**Directory**: `ton-iot-dashboard-build/`

Create a Next.js (App Router) dashboard with Tailwind CSS + Recharts + Framer Motion, mirroring the `ecg-dashboard-build/` structure and aesthetic quality.

**Dashboard sections**:
1. Hero — project title, dataset details, key metrics (binary F1, multi-class macro-F1, dataset size).
2. Dataset Overview — attack vs benign split, per-type distribution chart.
3. Feature Engineering — table of all engineered features with rationale column.
4. Binary Classification — confusion matrix, ROC curve, classification report table.
5. Multi-Class Classification — 10×10 confusion matrix heatmap, per-class F1 bar chart.
6. Model Comparison — 4 models × all metrics, highlight winner.
7. Feature Importance — top 20 feature importance bar chart.
8. Sample Predictions — interactive table (predicted type, confidence, true label).
9. System Architecture — pipeline flow diagram.
10. Limitations & Responsible Use.
11. References.

**Acceptance Checks**:
- `npm run build` passes.
- All sections render with real metric values (no placeholder data).
- Deployed to Vercel; URL shared.

---

## 📝 Phase 7: Documentation Suite

Create these files in the project root:

1. **`TON_IoT_Master_Prompt.md`** — this file.
2. **`TON_IoT_Technical_Resource.md`** — full 44-column schema, engineered feature definitions, attack taxonomy, model card.
3. **`TON_IoT_Flow_Diagram.md`** — ASCII + Mermaid system flow diagram.
4. **`TON_IoT_Backend_Schema.md`** — feature matrix schema, artifact registry, prediction output schema.
5. **`outputs/reports/TON_IoT_Final_Report.md`** — generated in Phase 5.

---

## ✅ Phase 8: Validation & Sign-off

1. Run all 5 notebooks top-to-bottom (`Kernel > Restart & Run All`) without errors.
2. Run `scripts/validate_all.py` — checks all expected artifacts exist.
3. Verify `outputs/models/` contains:
   - `feature_list.pkl`, `label_encoders.pkl`, `scaler.pkl`, `feature_metadata.json`
   - `best_binary_model.pkl`, `binary_model_metadata.json`
   - `best_multiclass_model.pkl`, `multiclass_model_metadata.json`
4. Verify `outputs/reports/TON_IoT_Final_Report.md` exists and is non-empty.
5. Confirm feature hash in metadata matches re-computed hash from loaded `feature_list.pkl`.
6. Update `TASKS.md` with final phase completions, dates, and metrics.

---

## 🚧 Guardrails & Escalation Rules

Stop and ask the user before proceeding if any of the following occur:

- Phase 1 acceptance check fails — do not proceed to Phase 2 on a broken or misunderstood dataset.
- A step would overwrite an existing trained model artifact (`*.pkl`) without first backing it up or confirming with the user.
- Phase 4 multi-class macro-F1 is below 0.70 — flag for human review; do not mark Phase 4 as complete.
- `MAX_ROWS` needs to change from `None` (full dataset) — confirm the actual number with the user before running a limited experiment.
- Any data file (`.csv`, manifest, `.pkl`) appears missing or inconsistent with what an earlier phase produced.
- The dashboard build (`npm run build`) fails — stop and report the error output before proceeding to Vercel deployment.
- Feature hash in metadata does not match the loaded feature list — this is a critical mismatch, do not proceed to prediction.

In all other cases, proceed phase-by-phase, validate against the "Acceptance Checks" for each phase, and update `TASKS.md` before moving on.

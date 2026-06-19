# TASKS

## Phase 0 — Environment Setup
- [x] Project directory structure created
- [x] `config.py` created and verified
- [x] `requirements.txt` created and all packages installable
- [x] `src/` module files created
- [x] `outputs/` directory structure created

## Phase 1 — Data Exploration
- [x] `01_data_exploration.py` & `.ipynb` run without error (Restart & Run All)
- [x] Dataset shape confirmed: 211,044 rows × 44 cols
- [x] Missing value pattern documented
- [x] Class distributions plotted and saved
- [x] `outputs/reports/data_audit.md` generated

## Phase 2 — Feature Engineering
- [x] `02_feature_engineering.py` & `.ipynb` run without error
- [x] Zero NaN/Inf values in final feature matrix (assert passes)
- [x] Feature count = 33 documented
- [x] `outputs/feature_matrix_train.csv` saved
- [x] `outputs/feature_matrix_test.csv` saved
- [x] `outputs/models/feature_list.pkl` saved
- [x] `outputs/models/label_encoders.pkl` saved
- [x] `outputs/models/scaler.pkl` saved
- [x] `outputs/models/feature_metadata.json` saved (with feature hash)

## Phase 3 — Binary Classification
- [x] `03_binary_classification.py` & `.ipynb` run without error
- [x] All 4 models trained
- [x] CV results table printed
- [x] Best model selected by held-out F1: RandomForestClassifier (Test F1 = 0.9993)
- [x] `outputs/models/best_binary_model.pkl` saved
- [x] `outputs/models/binary_model_metadata.json` saved
- [x] Confusion matrix plots saved per model
- [x] ROC curve saved

## Phase 4 — Multi-Class Classification
- [x] `04_multiclass_classification.py` & `.ipynb` run without error
- [x] All 4 models trained
- [x] Full per-class classification report printed
- [x] Best model selected by Macro-F1: RandomForestClassifier (Test Macro-F1 = 0.9658)
- [x] `outputs/models/best_multiclass_model.pkl` saved
- [x] `outputs/models/multiclass_model_metadata.json` saved
- [x] Confusion matrix heatmap saved
- [x] Feature importance plot saved
- [x] Per-class F1 bar chart saved
- [x] `outputs/reports/sample_predictions.csv` (50 rows) saved

## Phase 5 — Model Comparison & Final Report
- [x] `05_model_comparison_and_report.py` & `.ipynb` run without error
- [x] Model comparison table (binary + multi-class, all 4 models) generated
- [x] `outputs/reports/TON_IoT_Final_Report.md` generated

## Phase 6 — Next.js Dashboard
- [x] `ton-iot-dashboard-build/` Next.js app initialized
- [x] All dashboard sections implemented with real data
- [x] `npm run build` passes
- [x] Deployed to Vercel — URL: https://healthcare-code-2azi-lime.vercel.app/ (embedded in Vercel project integration)

## Phase 7 — Documentation Suite
- [x] `TON_IoT_Master_Prompt.md` copied to project root
- [x] `TON_IoT_Technical_Resource.md` copied to project root
- [x] `TON_IoT_Flow_Diagram.md` copied to project root
- [x] `TON_IoT_Backend_Schema.md` copied to project root

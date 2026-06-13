# Codex Master Prompt: Hybrid ECG Arrhythmia Implementation & Dashboard Integration

*Copy and paste the entire prompt below into a new Codex/AI session when you start your work.*

---

```markdown
# Directives for Hybrid ECG Arrhythmia Pipeline Implementation

You are a senior pair-programming AI coding assistant. We are developing an end-to-end clinical ECG classification system. We have modularized our signal preprocessing, CWT scalogram generation, handcrafted feature extraction, and model training.

Our target is to implement the final production pipeline using `efficientnet_b4` embeddings, integrate this hybrid logic into `predict.py` and `dashboard.py`, and update the project documentation dynamically.

---

## 📂 Phase 0: Load Project Context
Before writing any code, locate and read these project files in the workspace root:
1. **README.md**: Environment setup and notebook order.
2. **PROJECT_CONTEXT.md**: SNOMED maps, 17 handcrafted feature formulas, and deep wavelet specifications.
3. **ARCHITECTURE.md**: System layout and `src/` modular library API signatures.
4. **DECISIONS.md**: Engineering and clinical design justifications.
5. **TASKS.md**: Completed items and implementation targets.
6. **prompts/coding_guidelines.md**: Code rules (pathlib, SEED = 42, train/test split rules, sequential loop optimizations).

---

## 🏃 Phase 1: Run Baseline & Verify Prototype (Smoke Test)
To verify everything works before doing heavy runs, execute these steps:
1. Run `notebooks/ecg_analysis_phase_workflow.ipynb` to establish baseline handcrafted metrics.
2. Run `notebooks/03_preprocessing_and_scalograms.ipynb` with:
   - `MAX_RECORDS = 300`
   - `TARGET_SIZE = (224, 224)`
   This outputs preprocessed scalograms to `outputs/deep_features/scalograms_3ch_224/` and registers them in `scalogram_manifest_3ch_224.csv`.
3. Run `notebooks/04_efficientnet_embeddings.ipynb` with:
   - `MODEL_NAME = "efficientnet_b0"`
   - `MAX_IMAGES = 300`
   This generates B0 embeddings and creates `hybrid_handcrafted_efficientnet_b0.csv`.
4. Run `notebooks/05_hybrid_feature_training.ipynb` with:
   - `MODEL_NAME = "efficientnet_b0"`
   Verify that models train sequentially (`n_jobs=1`), comparison tables save successfully, and execution finishes under 30 seconds.

---

## 🏆 Phase 2: Final Production Execution (EfficientNet-B4)
Once the prototype executes successfully, run the final pipeline with `efficientnet_b4`:
1. Modify `notebooks/03_preprocessing_and_scalograms.ipynb` configurations:
   - Set `TARGET_SIZE = (380, 380)` (Standard B4 input dimensions).
   - Set `MAX_RECORDS = 1000` (or the full available dataset if hardware allows).
   - Re-run notebook 03.
2. Modify `notebooks/04_efficientnet_embeddings.ipynb` configurations:
   - Set `MODEL_NAME = "efficientnet_b4"`.
   - Set `MAX_IMAGES = 1000` (matching the count from step 1).
   - Re-run notebook 04. This exports `hybrid_handcrafted_efficientnet_b4.csv`.
3. Modify `notebooks/05_hybrid_feature_training.ipynb` configurations:
   - Set `MODEL_NAME = "efficientnet_b4"`.
   - Re-run notebook 05.
   - Confirm that the best hybrid model is saved as `best_hybrid_model_efficientnet_b4.pkl` along with its corresponding features list `best_hybrid_feature_list_efficientnet_b4.pkl`.

---

## 🔄 Phase 3: Implement Fused Predictor (`predict.py`)
Modify `predict.py` to run predictions using the new hybrid model:
1. **Load Artifacts**: Load `best_hybrid_model_efficientnet_b4.pkl`, `best_hybrid_feature_list_efficientnet_b4.pkl`, and the corresponding fitted `scaler.pkl` and `pca.pkl`.
2. **Extract Features on the Fly**: For a selected patient record:
   - Load the raw 12-lead signal matrix from the `.mat` file.
   - Preprocess Leads `I`, `II`, and `V5` via `src/preprocessing.py`.
   - Build a 3-channel CWT scalogram image resized to `(380, 380)` using `src/scalogram.py`.
   - Load the pretrained `efficientnet_b4` model in evaluation mode and extract the 1280-dimension embedding vector.
   - Extract the 17-dimensional handcrafted features via `src/handcrafted_features_v2.py`.
   - Concatenate the handcrafted and deep features, and reindex them to match the exact column list from `best_hybrid_feature_list_efficientnet_b4.pkl`.
3. **Run Predictions**: Apply scaling and PCA, compute probability scores, assign clinical risk levels using the custom vitals rules, and trigger LLM explanations.
4. **Log Output**: Save predictions, confidences, and clinical risks to `predictions.csv`.

---

## 🎛️ Phase 4: Streamlit Dashboard Integration (`dashboard.py`)
Update `dashboard.py` to reflect the new hybrid pipeline metrics:
1. **Scalogram Visualization**: Display the preprocessed 3-channel CWT scalogram image next to the time-series signal plots.
2. **Clinical Metrics Cards**: Add metric cards for the new temporal HRV variables (`SDNN`, `RMSSD`, `pNN50`) on the live session stats panel.
3. **Pipeline Progress**: Display a status message showing that the system is running using the `EfficientNet-B4 + LightGBM` hybrid model.

---

## 📝 Phase 5: Maintain Documentation
Update these files dynamically as you complete each phase:
- **TASKS.md**: Mark items as complete `[x]`, noting date, metrics, and dataset sizes.
- **PROJECT_CONTEXT.md**: Update validation scores (Accuracy, Macro-F1) in the success criteria tables.
- **ARCHITECTURE.md** & **DECISIONS.md**: Document changes to the final parameters.
```

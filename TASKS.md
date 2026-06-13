# Project Task Tracker & Verification Targets

This document serves as the primary roadmap and task verification guide for the ECG Arrhythmia classification project. Use it to track development milestones, code updates, and model evaluation targets.

---

## 🚀 Checklist & Implementation Milestones

### Phase 1: Baseline Analysis & Infrastructure Setup
- [x] Create modular input/output wrapper functions (`src/ecg_io.py`) to discover and load recordings.
- [x] Extract and store enhanced Heart Rate Variability (HRV) metrics, including statistical shape and morphology variables, in `src/handcrafted_features_v2.py`.
- [x] Perform dataset audits for class frequencies, invalid physiological values, and duplicate rows.
- [x] Build and run the baseline modeling notebook `ecg_analysis_phase_workflow.ipynb`.
-   **Verification Checklist**:
    *   Verify that `ecg_dataset.csv` contains all base handcrafted columns.
    *   Ensure classification metrics are evaluated using stratified splits.
    *   **Success Target**: Baseline model establishes a macro-F1 score target (e.g. ~80% or similar).

### Phase 2: Preprocessing and Wavelet Scalograms
- [x] Configure a zero-phase 4th-order Butterworth bandpass filter (`0.5 - 40 Hz`) to eliminate base offsets and artifacts in `src/preprocessing.py`.
- [x] Implement lead z-score scaling to ensure consistent signal scale across records.
- [x] Develop a 3-channel CWT scalogram builder using Leads `I`, `II`, and `V5` with a Complex Morlet wavelet (`cmor1.5-1.0`) in `src/scalogram.py`.
- [x] Write and run `03_preprocessing_and_scalograms.ipynb` to process raw `.mat/.hea` signals and cache PNG scalograms.
-   **Verification Checklist**:
    *   Run script using a testing limit `MAX_RECORDS = 300` and target dimensions `(224, 224)`.
    *   Confirm that generated PNG files are saved to `outputs/deep_features/scalograms_3ch_224/`.
    *   Check that the generated manifest file `scalogram_manifest_3ch_224.csv` contains valid paths and class labels.

### Phase 3: Deep Feature Embeddings
- [x] Build and verify `04_efficientnet_embeddings.ipynb` to extract activations from the target pooling layers.
- [x] Configure PyTorch transforms to resize, tensor-convert, and normalize (using ImageNet mean and standard deviation) the scalogram images.
- [x] Implement a batch extraction loop using a pretrained CNN backbone (`efficientnet_b0`).
- [x] Save extracted 1280-dimension embedding vectors to disk as `.npy` files.
- [x] Merge deep feature tables with tabular handcrafted features on matching `record_id` and `label`.
-   **Verification Checklist**:
    *   Run script with `MAX_IMAGES = 50` as a quick check, then increase to `300`.
    *   Confirm that `outputs/deep_features/features/hybrid_handcrafted_efficientnet_b0.csv` is created.
    *   Ensure the shape of the final output table matches: `(N_samples, 1297)` (17 handcrafted columns + 1280 deep columns + metadata columns).

### Phase 4: Benchmarking and Fused Classifier Evaluation
- [x] Patch and optimize `05_hybrid_feature_training.ipynb`:
  - [x] Set LGBM classifier parameter `n_jobs=1` to prevent thread contention.
  - [x] Set `n_jobs=1` in `cross_validate` to execute loops sequentially and avoid thread bottlenecks.
  - [x] Set cross-validation splits to 3 folds (`CV_FOLDS = 3`) for the testing phase.
  - [x] Limit PCA dimensions to a fixed component size (`PCA_COMPONENTS = 30`) to avoid scaling issues on small datasets.
  - [x] Limit estimators to 150 (`N_ESTIMATORS = 150`).
  - [x] Integrate execution timers in cross-validation blocks.
- [x] Compare model benchmarks: Handcrafted-only, Deep-only, and Hybrid fusion.
- [x] Save the best model and corresponding feature list.
-   **Verification Checklist**:
    *   Confirm that all models train and compile.
    *   Check that the comparative results table `hybrid_comparison_efficientnet_b0.csv` is exported successfully.
    *   Verify that pickled model checkpoints are saved to `outputs/deep_features/models/`.

### Phase 5: Production-Scale Execution
- [ ] Run a 300-record smoke test end-to-end to verify pipeline correctness.
- [ ] Increase the workflow sample size to 3,000+ records to achieve production-grade model validation.
- [ ] Evaluate classification performance to confirm targets are met:
  *   **Accuracy Target**: $\ge 80\%$
  *   **Macro-F1 Target**: $\ge 80\%$
- [ ] Verify that the hybrid classifier outperforms the handcrafted baseline.

### Phase 6: Advanced Research Extensions
- [ ] Add support for alternative pretrained models like `efficientnet_b4` (input size: $380 \times 380$), ConvNeXt, or Vision Transformers.
- [ ] Implement Grad-CAM overlays to visualize which regions of the scalogram the deep learning model uses to make predictions.
- [ ] Update Streamlit dashboard (`dashboard.py`) to support hybrid models.

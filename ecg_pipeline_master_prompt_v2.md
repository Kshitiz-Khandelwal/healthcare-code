# Codex Master Prompt: Hybrid ECG Arrhythmia Implementation & Dashboard Integration (v2)

*Copy and paste the entire prompt below into a new Codex/AI session when you start your work.*

---

# Directives for Hybrid ECG Arrhythmia Pipeline Implementation

You are a senior pair-programming AI coding assistant. We are developing an end-to-end clinical-research ECG classification system. Signal preprocessing, CWT scalogram generation, handcrafted feature extraction, and model training are already modularized.

Our target is to implement the final production pipeline using `efficientnet_b4` embeddings, integrate this hybrid logic into `predict.py` and `dashboard.py`, and update project documentation dynamically — with reproducible, validated, checkpointed runs at every phase.

**General rules that apply across all phases:**
- All configuration values (`MAX_RECORDS`, `TARGET_SIZE`, `MODEL_NAME`, `SEED`, paths) must live in a single config source (e.g., `config.py` or `config.yaml`) rather than being hardcoded separately in each notebook/script. If they currently aren't, consolidate them as part of Phase 0.
- `SEED = 42` must be set for `random`, `numpy`, `torch` (CPU and CUDA if available), `scikit-learn` (`random_state`), and `LightGBM` (`random_state`/`seed`) — verify this in every notebook/script touched.
- Never mark a checklist item `[x]` in `TASKS.md` unless the corresponding run actually executed and produced the referenced artifact/metric. Do not fabricate numbers.
- Commit after each phase with a descriptive message. Do **not** commit large binary artifacts (`.pkl`, embedding `.csv` files, scalogram images) — confirm `.gitignore` covers `outputs/`, `models/*.pkl`, and note where these artifacts physically live instead.
- See **Guardrails & Escalation Rules** at the end of this prompt — read it before starting.

---

## 📂 Phase 0: Load Project Context & Verify Environment

1. Locate and read these project files in the workspace root:
   - **README.md** — environment setup and notebook order.
   - **PROJECT_CONTEXT.md** — SNOMED maps, 17 handcrafted feature formulas, deep wavelet specifications.
   - **ARCHITECTURE.md** — system layout and `src/` modular library API signatures.
   - **DECISIONS.md** — engineering and clinical design justifications.
   - **TASKS.md** — completed items and implementation targets.
   - **prompts/coding_guidelines.md** — code rules (pathlib, `SEED = 42`, train/test split rules, sequential loop optimizations).

2. **Environment verification (new):**
   - Confirm Python version and that `torch`, `torchvision` (or `timm`, whichever library is used to load `efficientnet_b0`/`efficientnet_b4`), `lightgbm`, `scikit-learn`, and the CWT library (e.g., `pywt`) are installed and importable.
   - Check `torch.cuda.is_available()`. Log the result — this materially affects expected runtime for Phase 2 (B4 at 380×380 is significantly more expensive than B0 at 224×224).
   - Confirm `SEED = 42` is applied consistently per the rules above. If any notebook/script is missing seeding, fix it now before generating any artifacts.

3. **Directory layout check (new):**
   - Confirm `outputs/deep_features/`, `models/`, and `logs/` exist (create if missing).
   - Confirm naming conventions for versioned artifacts are documented in `ARCHITECTURE.md` (model name suffix on every saved artifact — model, scaler, PCA, feature list, metadata).

**Definition of Done — Phase 0:** All six context files have been read and summarized in your own working notes; environment check passed (or gaps fixed); config consolidation confirmed or completed; directory structure confirmed.

---

## 🏃 Phase 1: Run Baseline & Verify Prototype (Smoke Test, EfficientNet-B0)

1. Run `notebooks/ecg_analysis_phase_workflow.ipynb` to establish baseline handcrafted metrics.
2. Run `notebooks/03_preprocessing_and_scalograms.ipynb` with:
   - `MAX_RECORDS = 300`
   - `TARGET_SIZE = (224, 224)`
   - Outputs preprocessed scalograms to `outputs/deep_features/scalograms_3ch_224/` and registers them in `scalogram_manifest_3ch_224.csv`.
3. Run `notebooks/04_efficientnet_embeddings.ipynb` with:
   - `MODEL_NAME = "efficientnet_b0"`
   - `MAX_IMAGES = 300`
   - Generates B0 embeddings (1280-dim) and creates `hybrid_handcrafted_efficientnet_b0.csv`.
4. Run `notebooks/05_hybrid_feature_training.ipynb` with:
   - `MODEL_NAME = "efficientnet_b0"`
   - Verify models train sequentially (`n_jobs=1`), comparison tables save successfully, and execution finishes under 30 seconds.

**Acceptance checks (new) — all must pass before proceeding to Phase 2:**
- `scalogram_manifest_3ch_224.csv` has exactly 300 rows, and every referenced image file exists on disk.
- `hybrid_handcrafted_efficientnet_b0.csv` has the expected column count: 17 handcrafted features + 1280 deep-feature columns + identifier/label columns.
- `n_jobs=1` is confirmed in the training code (no parallel sklearn/LightGBM jobs).
- Wall-clock runtime of notebook 05 is logged and confirmed under 30 seconds.
- Record baseline metrics (Accuracy, Macro-F1, per-class recall) — these are your comparison baseline for Phase 2.

**Definition of Done — Phase 1:** All four notebooks executed without error, all acceptance checks pass, baseline metrics recorded. If any check fails, **stop and report** — do not proceed to Phase 2 on a failing baseline.

---

## 🏆 Phase 2: Final Production Execution (EfficientNet-B4)

Once Phase 1 passes cleanly, run the final pipeline with `efficientnet_b4`.

1. **Modify `notebooks/03_preprocessing_and_scalograms.ipynb`:**
   - Set `TARGET_SIZE = (380, 380)` (standard B4 input dimensions).
   - Set `MAX_RECORDS = 1000` (or the full available dataset if hardware allows — confirm with the user before silently reducing or expanding this number).
   - **Checkpointing (new):** Since 1000 records at 380×380 takes substantially longer than the Phase 1 smoke test, persist the manifest incrementally (e.g., append rows every N records, or write to a temp manifest and merge on completion) so a crash/interrupt doesn't require restarting from zero.
   - Re-run notebook 03.

2. **Modify `notebooks/04_efficientnet_embeddings.ipynb`:**
   - Set `MODEL_NAME = "efficientnet_b4"`.
   - Set `MAX_IMAGES = 1000` (matching the count from step 1).
   - **Note:** `efficientnet_b4` produces a **1792-dimensional** embedding vector (not 1280 — that's B0's dimension). Ensure downstream column counts, reindexing, and any hardcoded shape assumptions reflect 1792.
   - Re-run notebook 04. This exports `hybrid_handcrafted_efficientnet_b4.csv`.
   - If `torch.cuda.is_available()` was `False` in Phase 0, log expected CPU runtime before starting this step and confirm with the user that the run should proceed at this scale.

3. **Modify `notebooks/05_hybrid_feature_training.ipynb`:**
   - Set `MODEL_NAME = "efficientnet_b4"`.
   - **Train/test split integrity (new):** Confirm the split is performed at the same patient/record-ID granularity and uses the same seed/methodology as the Phase 1 prototype, so B0 vs. B4 results are comparable and there is no leakage between train and test partitions.
   - Re-run notebook 05.
   - Confirm the best hybrid model is saved as `best_hybrid_model_efficientnet_b4.pkl` along with its corresponding feature list `best_hybrid_feature_list_efficientnet_b4.pkl`.
   - **Versioned transformer artifacts (fix):** Save the fitted feature scaler and PCA as `scaler_efficientnet_b4.pkl` and `pca_efficientnet_b4.pkl` (not generic `scaler.pkl`/`pca.pkl`), so they cannot be accidentally mismatched with a different model version later.
   - **Metadata file (new):** Save `model_metadata_efficientnet_b4.json` containing: training timestamp, dataset size, a hash of the feature list (column names + order), and the recorded metrics below.

4. **Benchmark vs. baseline (new):** Record B4 hybrid metrics (Accuracy, Macro-F1, and per-class recall — especially for any rare/minority arrhythmia classes) alongside the Phase 1 B0 baseline in a comparison table. This comparison feeds Phase 6.

**Definition of Done — Phase 2:** `outputs/deep_features/scalograms_3ch_224/` (or an equivalent B4-sized directory) and `hybrid_handcrafted_efficientnet_b4.csv` exist with 1000 rows and 1792+17+metadata columns; `best_hybrid_model_efficientnet_b4.pkl`, `best_hybrid_feature_list_efficientnet_b4.pkl`, `scaler_efficientnet_b4.pkl`, `pca_efficientnet_b4.pkl`, and `model_metadata_efficientnet_b4.json` all exist; B4 metrics recorded next to B0 baseline.

---

## 🔄 Phase 3: Implement Fused Predictor (`predict.py`)

Modify `predict.py` to run predictions using the new hybrid model.

1. **Load Artifacts:**
   - Load `best_hybrid_model_efficientnet_b4.pkl`, `best_hybrid_feature_list_efficientnet_b4.pkl`, `scaler_efficientnet_b4.pkl`, `pca_efficientnet_b4.pkl`, and `model_metadata_efficientnet_b4.json`.
   - **Version check (new):** Recompute the hash of the loaded feature list and compare it against the hash stored in `model_metadata_efficientnet_b4.json`. If they don't match, raise a clear error rather than proceeding with a possibly-mismatched pipeline.

2. **Extract Features on the Fly:**
   - For a selected patient record, load the raw 12-lead signal matrix from the `.mat` file.
   - Preprocess Leads `I`, `II`, and `V5` via `src/preprocessing.py`.
   - Build a 3-channel CWT scalogram image resized to `(380, 380)` using `src/scalogram.py`.
   - Load the pretrained `efficientnet_b4` model in evaluation mode and extract the **1792-dimension** embedding vector.
   - Extract the 17-dimensional handcrafted features via `src/handcrafted_features_v2.py`.
   - Concatenate the handcrafted and deep features, and reindex to match the exact column list from `best_hybrid_feature_list_efficientnet_b4.pkl`.
   - **Schema validation (new):** After reindexing, assert there are zero NaN/Inf values and that the column order exactly matches the saved feature list. If validation fails, do not proceed to scoring — log the record as `status="error"` with the reason.

3. **Error handling (new):**
   - Handle missing/corrupt `.mat` files, unexpected lead counts, or unexpected sampling rates with clear, specific exceptions. These should not crash the whole batch — log the affected record and continue.

4. **Run Predictions:**
   - Apply scaling and PCA, compute probability scores, assign clinical risk levels using the custom vitals rules, and trigger LLM explanations.
   - **Latency logging (new):** Log per-record timing for preprocessing, embedding extraction, and total inference — useful for the dashboard and for capacity planning.

5. **Log Output:** Save predictions, confidences, clinical risks, and any error statuses to `predictions.csv`.

6. **Integration test (new):** Add `tests/test_predict.py` that runs `predict.py` against 3–5 known sample records and checks that predictions/probabilities fall within expected ranges (or match a previously recorded reference output, as a regression check).

**Definition of Done — Phase 3:** `predict.py` runs end-to-end on at least one real record, schema validation and error handling are exercised (e.g., via a deliberately bad `.mat` path in the test), `predictions.csv` is populated, and `tests/test_predict.py` passes.

---

## 🎛️ Phase 4: Streamlit Dashboard Integration (`dashboard.py`)

1. **Scalogram Visualization:**
   - Display the preprocessed 3-channel CWT scalogram image next to the time-series signal plots.
   - **Missing-file handling (new):** If the scalogram image for a selected record isn't found, show a clear placeholder/message rather than failing the whole page.

2. **Clinical Metrics Cards:**
   - Add metric cards for the new temporal HRV variables (`SDNN`, `RMSSD`, `pNN50`) on the live session stats panel.
   - **Reference ranges (new):** Where clinically-established normal ranges exist for these HRV metrics, color-code or annotate the cards (e.g., normal / borderline / abnormal) so values are interpretable at a glance.

3. **Pipeline Progress:**
   - Display a status message (e.g., `st.status` or `st.spinner`) showing that the system is running the `EfficientNet-B4 + LightGBM` hybrid model, including the current step (preprocessing → scalogram → embedding → handcrafted features → scaling/PCA → prediction).

4. **Performance (new):**
   - Cache model/scaler/PCA loading with `st.cache_resource` so they are not reloaded on every interaction.
   - Cache scalogram/feature computation per-record with `st.cache_data` where appropriate.

5. **Interpretability (new, optional but recommended):**
   - Surface the top contributing features for a given prediction (e.g., via LightGBM `feature_importances_` or SHAP values) so clinicians/reviewers can see what drove a risk classification.

6. **Disclaimer (new):**
   - Add a visible banner noting this dashboard is a research/decision-support tool and is not a standalone diagnostic device — predictions should be reviewed by a qualified clinician.

**Definition of Done — Phase 4:** Dashboard loads a sample record end-to-end, displays scalogram + HRV cards + pipeline status without error, model artifacts are cached, and the disclaimer is visible.

---

## ✅ Phase 5: Maintain Documentation

Update these files as each phase completes — append, don't overwrite history:

- **TASKS.md**: Mark items complete `[x]`, noting date, metrics, dataset sizes, and the git commit hash for that phase's work.
- **PROJECT_CONTEXT.md**: Update validation scores (Accuracy, Macro-F1, per-class recall) in the success criteria tables. Add/update a **model card** section: training data size, model version (`efficientnet_b4`), validation metrics, known limitations (e.g., class imbalance, dataset coverage), and intended use.
- **ARCHITECTURE.md** & **DECISIONS.md**: Document changes to final parameters — including the corrected B4 embedding dimension (1792), the versioned artifact naming convention, and the checkpointing approach added in Phase 2.
- **Changelog format (new):** Each entry should include date/time, phase number, summary of changes, key metrics, and git commit hash, in a consistent append-only format so the history of runs is auditable.

---

## 🧪 Phase 6: Validation, Regression Testing & Sign-off (New)

1. Run the integration test from Phase 3 (`tests/test_predict.py`) and confirm it passes.
2. Compare B4 hybrid metrics against the B0 baseline from Phase 1 (Accuracy, Macro-F1, per-class recall). If Macro-F1 or any minority-class recall **decreases** versus the B0 baseline, flag this explicitly for human review rather than silently proceeding — do not mark Phase 2/6 as complete in `TASKS.md` until this is resolved or explicitly accepted by the user.
3. Generate a final summary report (markdown) covering: artifacts produced and their paths, final metrics vs. baseline, environment details (CUDA used or not, runtime), and any open issues/limitations.

**Definition of Done — Phase 6:** Integration tests pass, B4-vs-B0 comparison is documented with an explicit pass/flag outcome, and the summary report exists.

---

## 🚧 Guardrails & Escalation Rules

Stop and ask the user before proceeding if any of the following occur:

- Any Phase 1 acceptance check fails — do not proceed to the more expensive Phase 2 run on a failing baseline.
- A step would overwrite an existing trained model artifact (`*.pkl`) without first backing it up or confirming with the user.
- Phase 6 shows B4 hybrid metrics regressing versus the B0 baseline (especially for minority arrhythmia classes).
- `MAX_RECORDS` for Phase 2 needs to change from 1000 (either up to "full dataset" or down due to hardware constraints) — confirm the actual number with the user before running.
- `torch.cuda.is_available()` is `False` and the estimated CPU runtime for Phase 2 is large — confirm before committing to the run.
- Any data file (`.mat`, manifest, CSV) appears missing, corrupted, or inconsistent with what earlier phases/notebooks expect.

In all other cases, proceed phase-by-phase, validate against the "Definition of Done" for that phase, and update documentation before moving on.

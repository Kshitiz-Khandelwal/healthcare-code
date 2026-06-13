# ECG Arrhythmia Classification & Deep Hybrid Feature Learning

This repository implements a modular, research-grade hybrid machine learning pipeline for classifying 12-lead Electrocardiogram (ECG) recordings. The system categorizes signals into three distinct classes:
1. **Normal** (SNOMED code `426783006`)
2. **Arrhythmia** (Atrial fibrillation, etc. SNOMED codes `164889003`, `164890007`, `426177001`)
3. **Other / Unknown** (All other diagnostic codes)

By combining **interpretable clinical metrics** (Heart Rate Variability, morphology, statistical shapes) with **high-dimensional deep features** extracted from Continuous Wavelet Transform (CWT) scalogram images, this project builds a robust, explainable framework for computer-aided clinical diagnosis.

---

## 📁 Repository Structure and Directories

```text
healthcare project/
│
├── README.md                           # Main quickstart, data format specifications, and execution instructions
├── PROJECT_CONTEXT.md                  # Comprehensive medical context, SNOMED mappings, and feature breakdown
├── ARCHITECTURE.md                     # Deep-dive system diagram, src/ API specs, and folder structures
├── TASKS.md                            # Detailed development roadmap, checklist, and phase verification targets
├── DECISIONS.md                        # Mathematical, clinical, and engineering rationale for design choices
│
├── prompts/
│   ├── startup_prompt.md               # Transition context loader to feed to new AI coding assistant sessions
│   └── coding_guidelines.md            # Coding standards (seeding, data splitting, paths, style rules)
│
├── src/                                # Reusable modular libraries
│   ├── ecg_io.py                       # I/O functions for loading WFDB MATLAB (.mat) and reading headers (.hea)
│   ├── preprocessing.py                # Butter bandpass filter and z-score normalization
│   ├── scalogram.py                    # CWT scalogram image generator (Morlet scale calculations)
│   └── handcrafted_features_v2.py      # Statistical shapes and temporal HRV features (RMSSD, SDNN)
│
├── notebooks/                          # Sequential pipeline steps
│   ├── ecg_analysis_phase_workflow.ipynb # Handcrafted feature analysis and initial baseline metrics
│   ├── 03_preprocessing_and_scalograms.ipynb # Signal cleaning and scalogram PNG image output generator
│   ├── 04_efficientnet_embeddings.ipynb      # Frozen deep activation vector extractor (timm integration)
│   └── 05_hybrid_feature_training.ipynb      # Classifier benchmarking (tabular vs deep vs hybrid fusion)
│
└── outputs/                            # Cached calculations, models, and metric plots
    └── deep_features/
        ├── manifests/                  # CSV spreadsheets linking files and labels
        ├── scalograms_3ch_224/         # Cache folder for 224x224 RGB scalograms
        ├── features/                   # Processed CSV feature tables for modeling
        ├── models/                     # Pickled joblib checkpoints of classifiers
        └── results/                    # Classification reports and confusion matrices
```

---

## ⚙️ Environment Setup and Installation

### 1. Prerequisites
Ensure you have Python 3.10 or Python 3.11 installed. Verify using:
```powershell
python --version
```

### 2. Set Up Virtual Environment (Recommended)
From your terminal, navigate to the root workspace `C:\Users\Admin\Desktop\Kshitiz` and configure Python's virtual environment:
```powershell
# Create venv if not already present
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\activate
```

### 3. Install Core Dependencies
With the virtual environment activated, install the updated dependencies via:
```powershell
pip install -r requirements.txt
```
The dependencies in `requirements.txt` contain:
- `torch` & `torchvision`: Neural network runtime and transforms.
- `timm`: Pretrained CNN models repository (for EfficientNet backbones).
- `PyWavelets`: High-performance continuous wavelet calculations.
- `Pillow` & `opencv-python`: Image rendering, scaling, and file operations.
- `pandas` & `numpy`: High-speed data manipulation.
- `scikit-learn` & `lightgbm`: Machine learning benchmarks, pipelines, and classifiers.
- `tqdm`: Visual command-line progress indicators.

---

## 🏃 Execution Workflow

Execute the notebooks in the following order inside your Jupyter or VS Code environment:

### Phase 1: Establish Tabular Baseline
Open **[ecg_analysis_phase_workflow.ipynb](file:///C:/Users/Admin/Desktop/Kshitiz/healthcare%20project/healthcare%20project/notebooks/ecg_analysis_phase_workflow.ipynb)**
*   Analyzes structural parameters of `ecg_dataset.csv`.
*   Performs missing value assessments and identifies ranges for physiological values.
*   Trains the initial handcrafted LightGBM baseline model to define baseline F1 targets.

### Phase 2: Signal Preprocessing and Scalogram Generation
Open **[03_preprocessing_and_scalograms.ipynb](file:///C:/Users/Admin/Desktop/Kshitiz/healthcare%20project/healthcare%20project/notebooks/03_preprocessing_and_scalograms.ipynb)**
*   Calculates and saves CWT scalograms for a subset of raw signals.
*   **Parameters to tune for testing**:
    *   `MAX_RECORDS = 300` (Use a small smoke test first. Expand to higher quantities when computing power permits).
    *   `TARGET_SIZE = (224, 224)` (Standard resolution for EfficientNet-B0. For EfficientNet-B4, scale to `(380, 380)`).
*   Output files are saved directly to `outputs/deep_features/scalograms_3ch_224/` and compiled into `scalogram_manifest_3ch_224.csv`.

### Phase 3: Deep Feature Activation Extraction
Open **[04_efficientnet_embeddings.ipynb](file:///C:/Users/Admin/Desktop/Kshitiz/healthcare%20project/healthcare%20project/notebooks/04_efficientnet_embeddings.ipynb)**
*   Initializes the pretrained CNN backbone in inference mode.
*   Loads cached scalogram images and extracts the 1280-dimension activation vectors.
*   Merges deep features with handcrafted tabular columns from `ecg_dataset.csv` on the `record_id` join-key.
*   **Parameters to tune**:
    *   `MODEL_NAME = "efficientnet_b0"` (For higher capacity, replace with `"efficientnet_b4"`).
    *   `BATCH_SIZE = 32` (Reduce to `8` or `16` if running out of RAM or GPU VRAM).
*   Saves the final fused dataset: `outputs/deep_features/features/hybrid_handcrafted_efficientnet_b0.csv`.

### Phase 4: Benchmarking and Fused Classifier Evaluation
Open **[05_hybrid_feature_training.ipynb](file:///C:/Users/Admin/Desktop/Kshitiz/healthcare%20project/healthcare%20project/notebooks/05_hybrid_feature_training.ipynb)**
*   Benchmarcks handcrafted-only, deep-only, and hybrid models.
*   Applies standard scaling and PCA dimensionality reduction.
*   Saves the best-performing model checkpoint as `outputs/deep_features/models/best_hybrid_model_efficientnet_b0.pkl` along with its matching feature list.

---

## 📈 Running the Streamlit Dashboard
To launch the interactive clinical reviewer application:
```powershell
streamlit run dashboard.py
```
This launches a browser session on `http://localhost:8501`. You can upload raw `.mat` ECG waveforms, view their preprocessed tracks, generate local CWT scalograms, and inspect model predictions in real time.

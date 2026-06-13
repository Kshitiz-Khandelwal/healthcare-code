# System Architecture: ECG Hybrid Feature Pipeline

This document details the software architecture, modular Python APIs, and directory structure of the hybrid classification system.

---

## 🏗️ Software Architecture Diagram

The pipeline operates as a sequence of decoupled modules:

```text
  [ Raw ECG Records ] (MATLAB .mat array & WFDB .hea metadata)
          │
          ├──> Read via src/ecg_io.py (Parses demographics, annotations, maps labels)
          │
          ├──> Preprocess via src/preprocessing.py (Bandpass filter, z-score normalize)
          │
          ├──> Split into Dual Feature Paths:
          │
          │    ┌────────────────────────────────────────────────────────┐
          │    │ 1. Tabular Branch (interpretability)                   │
          │    │    src/handcrafted_features_v2.py                      │
          │    │    - Extracts temporal, amplitude, and HRV parameters   │
          │    │    - Outputs 17-dimensional vector                     │
          │    └────────────────────────────────────────────────────────┘
          │    ┌────────────────────────────────────────────────────────┐
          │    │ 2. Deep Branch (waveform morphology)                   │
          │    │    src/scalogram.py                                    │
          │    │    - Generates 3-channel Continuous Wavelet Transform  │
          │    │    - Exports 2D RGB scalogram image cache               │
          │    │    notebooks/04_efficientnet_embeddings.ipynb          │
          │    │    - Feeds scalograms into pretrained CNN              │
          │    │    - Outputs 1280-dimension frozen activation vector   │
          │    └────────────────────────────────────────────────────────┘
          │
          v
  [ Hybrid Feature Fusion ] (Concat handcrafted features + deep features)
          │
          ├──> Train/Test Split (Stratified on class label)
          ├──> StandardScaler (Fit on train split only, transform both)
          ├──> PCA Reduction (Applies to deep feature block: 30 components)
          │
          v
  [ LightGBM Classifier Benchmarking ]
          │
          ├──> Evaluates Acc, Macro-F1, Per-class F1, Confusion Matrix
          └──> Exports: best_hybrid_model.pkl & best_hybrid_feature_list.pkl
```

---

## 🛠️ API Specifications (`src/`)

### 1. `src/ecg_io.py`
This module manages metadata parsing, label mapping, and signal array loading.

#### Class: `ECGRecord`
A frozen dataclass representing a single recording instance.
*   **Properties**:
    *   `record_id` (str): Unique record ID.
    *   `mat_path` (Path): Path to the `.mat` file.
    *   `hea_path` (Path): Path to the `.hea` file.
    *   `age` (int): Age of patient (-1 if missing).
    *   `sex` (int): Sex of patient (1 = Male, 0 = Female, -1 if missing).
    *   `dx_codes` (tuple[str, ...]): Diagnostic SNOMED-CT codes.
    *   `label` (int): Mapped target label (`0`, `1`, or `2`).
    *   `label_name` (str): Label name string.
    *   `sampling_frequency` (int): Sampling rate in Hz.
    *   `n_leads` (int): Total leads recorded.
    *   `n_samples` (int): Length of recording.

#### Function: `map_dx_to_label`
```python
def map_dx_to_label(dx_codes: Iterable[str]) -> int
```
*   **Inputs**: An iterable of diagnostic codes.
*   **Outputs**: Mapped class label integer (0 for Normal, 1 for Arrhythmia, 2 for Other).
*   **Logic**: Matches codes against predefined SNOMED sets using set intersection.

#### Function: `parse_hea_file`
```python
def parse_hea_file(hea_path: str | Path) -> dict
```
*   **Inputs**: Absolute or relative path to the `.hea` file.
*   **Outputs**: Dictionary containing parsed metadata properties (`record_id`, `age`, `sex`, `dx_codes`, `label`, etc.).

#### Function: `discover_records`
```python
def discover_records(dataset_root: str | Path, limit: int | None = None) -> list[ECGRecord]
```
*   **Inputs**: Root directory path and an optional integer limit.
*   **Outputs**: Sorted list of validated `ECGRecord` instances.

#### Function: `load_ecg_mat`
```python
def load_ecg_mat(mat_path: str | Path) -> np.ndarray
```
*   **Inputs**: Path to the `.mat` file.
*   **Outputs**: A 2D Float32 numpy array with shape `(leads, samples)`. If the array is transposed, it is automatically corrected.

---

### 2. `src/preprocessing.py`
Handles noise removal and baseline normalization.

#### Function: `bandpass_filter`
```python
def bandpass_filter(signal: np.ndarray, fs: int = 500, low_hz: float = 0.5, high_hz: float = 40.0, order: int = 4) -> np.ndarray
```
*   **Inputs**: 1D signal array, sampling rate, lower cutoff, upper cutoff, filter order.
*   **Outputs**: Zero-phase filtered signal (using forward-backward `scipy.signal.filtfilt`).

#### Function: `zscore`
```python
def zscore(signal: np.ndarray, eps: float = 1e-8) -> np.ndarray
```
*   **Inputs**: 1D signal array, and epsilon value to prevent division by zero.
*   **Outputs**: Normalized signal with zero mean and unit variance.

#### Function: `preprocess_selected_leads`
```python
def preprocess_selected_leads(ecg_leads_first: np.ndarray, lead_indices: tuple[int, ...], fs: int = 500) -> list[np.ndarray]
```
*   **Inputs**: Full 2D ECG array, tuple of target lead indices, and sampling frequency.
*   **Outputs**: List of preprocessed 1D arrays corresponding to selected leads.

---

### 3. `src/scalogram.py`
Transforms time-series signals into time-frequency images using pywt.

#### Function: `cwt_scalogram`
```python
def cwt_scalogram(
    signal: np.ndarray,
    fs: int = 500,
    wavelet: str = "cmor1.5-1.0",
    min_hz: float = 0.5,
    max_hz: float = 40.0,
    n_freqs: int = 128,
    target_size: tuple[int, int] = (224, 224),
) -> np.ndarray
```
*   **Inputs**: 1D preprocessed signal and scale config parameters.
*   **Outputs**: Normalized 2D Uint8 grayscale scalogram array with dimensions matching `target_size`.

#### Function: `build_3channel_scalogram`
```python
def build_3channel_scalogram(
    ecg_leads_first: np.ndarray,
    fs: int = 500,
    lead_indices: tuple[int, int, int] = (0, 1, 10),
    target_size: tuple[int, int] = (224, 224),
) -> np.ndarray
```
*   **Inputs**: Raw 2D ECG array, sampling rate, lead selection tuple (defaults to I, II, V5), and target dimensions.
*   **Outputs**: Stacked RGB scalogram array of shape `(width, height, 3)` for deep network input.

---

### 4. `src/handcrafted_features_v2.py`
Computes traditional statistical and Heart Rate Variability parameters.

#### Function: `extract_enhanced_handcrafted_features`
```python
def extract_enhanced_handcrafted_features(signal: np.ndarray, fs: int = 500) -> dict[str, float]
```
*   **Inputs**: 1D ECG lead signal and sampling rate.
*   **Outputs**: Dictionary containing 17 statistical, HRV, and morphological features.

---

## 📋 Data Schemas & Intermediate Files

### 1. Preprocessed Scalogram Manifest (`scalogram_manifest_3ch_224.csv`)
Columns:
*   `record_id` (str): Unique record ID.
*   `label` (int): Mapped target label (`0`, `1`, `2`).
*   `label_name` (str): Mapped target label name.
*   `image_path` (str): Relative path pointing to the cached PNG image.

### 2. Deep Feature Embeddings CSV (`efficientnet_b0_deep_features.csv`)
Columns:
*   `record_id` (str): Join key matching signal record.
*   `label` (int): Target label integer.
*   `eff_0000` to `eff_1279` (float): Extracted CNN activations from the final global average pooling layer.

### 3. Fused Hybrid Dataset (`hybrid_handcrafted_efficientnet_b0.csv`)
Columns:
*   `filename` (str): Original `.mat` file name.
*   `record_id` (str): Merged join key.
*   `label` (int): Target class label.
*   **Handcrafted Columns** (17): `mean`, `std`, `max`, `min`, `energy`, `zero_crossings`, `skewness`, `kurtosis`, `peak_count`, `heart_rate`, `rr_mean`, `hrv`, `sdnn`, `rmssd`, `pnn50`, `rr_range`, `rr_cv`, `qrs_width_proxy_mean`, `qrs_width_proxy_std`.
*   **Deep Columns** (1280): `eff_0000` through `eff_1279`.

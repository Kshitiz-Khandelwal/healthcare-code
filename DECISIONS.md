# Key Technical & Clinical Decisions Log

This document records the mathematical, clinical, and engineering rationale behind the design of the ECG Arrhythmia hybrid classification pipeline.

---

## 📌 1. Selection of Lead Channels (I, II, V5) for RGB Stacking
*   **Context**: A standard clinical ECG records 12 leads. Generating 2D Continuous Wavelet Transform (CWT) scalograms for all 12 leads for every patient record results in a huge volume of intermediate image files and makes deep model training computationally expensive.
*   **Decision**: We selected **Leads I, II, and V5** to form the Red, Green, and Blue channels of the 2D scalogram images.
*   **Rationale**:
    1.  **Clinical Coverage**: Stacking three leads captures electrical activity across all three dimensions of the heart:
        *   **Lead I (Red channel)**: Measures the horizontal potential difference between the left and right arms (lateral view).
        *   **Lead II (Green channel)**: Follows the heart's main electrical axis from the right arm to the left leg (inferior view).
        *   **Lead V5 (Blue channel)**: Placed on the chest wall to record electrical activity in the left ventricular wall (anterior-lateral view).
    2.  **RGB Compatibility**: Most pretrained computer vision models (like EfficientNet or ResNet) expect 3-channel RGB inputs. Stacking three leads allows us to leverage these models directly without modifying their first convolutional layer, preserving the integrity of their pretrained weights.

---

## 📌 2. Continuous Wavelet Transform (CWT) using Complex Morlet Wavelet
*   **Context**: Converting 1D temporal ECG signals into 2D time-frequency representations requires selecting a transformation method (Short-Time Fourier Transform vs Continuous Wavelet Transform).
*   **Decision**: We chose the CWT with the Complex Morlet Wavelet (`cmor1.5-1.0`).
*   **Rationale**:
    *   **Resolution Limits**: The Short-Time Fourier Transform (STFT) uses a fixed window size, leading to a strict trade-off between time and frequency resolution. In contrast, the CWT scales its window dynamically. It uses short windows for high frequencies (perfect for capturing sharp, rapid events like the QRS complex) and long windows for low frequencies (optimal for capturing slow rhythm variations like P or T waves).
    *   **Morlet Wavelet Formulation**: The Complex Morlet wavelet is defined mathematically as:
        $$\psi(t) = \frac{1}{\sqrt{\pi f_b}} e^{i 2 \pi f_c t} e^{-t^2 / f_b}$$
        Where $f_b$ represents bandwidth and $f_c$ represents center frequency. Using the parameters `cmor1.5-1.0` (bandwidth = 1.5, center frequency = 1.0) provides an excellent balance between time and frequency resolution for ECG signals.
    *   **Scale Conversion**: Scales are computed from target frequencies using the relationship:
        $$\text{scale} = \frac{f_c}{f \cdot \Delta t}$$
        Where $f$ is the target frequency ($0.5 - 40\text{ Hz}$) and $\Delta t = 1/f_s$ ($1/500\text{ s}$). This ensures that the generated scalograms align precisely with cardiac rhythms.

---

## 📌 3. Frozen Embedding Extraction vs. End-to-End Fine-Tuning
*   **Context**: Deep convolutional networks contain millions of parameters. Fully training these models on small target datasets can easily lead to severe overfitting.
*   **Decision**: We use pretrained ImageNet weights to extract activation vectors from the final average pooling layer as frozen features, without running backpropagation.
*   **Rationale**:
    *   **Feature Reusability**: The early and mid-level layers of models trained on ImageNet act as general-purpose edge and pattern detectors. These features transfer well to identifying shapes in wavelet scalograms.
    *   **Lower Computational Burden**: Extracting features in a single forward pass is much faster than full training, allowing the pipeline to run on consumer-grade hardware.
    *   **Tabular Integration**: Using static feature vectors allows us to combine deep features with handcrafted clinical metrics in a single tabular format, enabling benchmarking with fast classifiers like LightGBM.

---

## 📌 4. Single-Threaded Execution (`n_jobs=1`) on Small Datasets
*   **Context**: Initial benchmarcking runs on small testing sets (e.g., 50 records) suffered from severe performance slowdowns, with CPU utilization spiking and training times stretching to minutes.
*   **Decision**: Set both scikit-learn's `cross_validate(n_jobs=1)` and LightGBM's `LGBMClassifier(n_jobs=1)` to run sequentially.
*   **Rationale**:
    *   **Process Spawning Overhead**: Spawning multiple processes in parallel incurs overhead (allocating memory, copying data, initializing threads). For small datasets, this setup cost takes longer than the model training itself.
    *   **Thread Contention**: When the outer cross-validation loop and the inner estimator both try to use all CPU cores (`n_jobs=-1`), the operating system spends more time switching between competing threads than doing real computation. Running sequentially resolves this bottleneck.

---

## 📌 5. Centralized Configuration & Versioned Artifacts
*   **Context**: Notebooks originally duplicated constants (`MAX_RECORDS`, `TARGET_SIZE`, `MODEL_NAME`, paths), which risked mismatched scaler/model pairs after switching from B0 to B4.
*   **Decision**: Consolidate all pipeline constants in `config.py` and suffix every serialized artifact with `{model_name}`.
*   **Rationale**: The B4 backbone produces **1792**-dimensional embeddings (not 1280). Versioned filenames and metadata feature-list hashes prevent silently loading the wrong scaler or PCA during inference.

---

## 📌 6. Incremental Manifest Checkpointing (Phase 2)
*   **Context**: Generating 1000 scalograms at 380×380 on CPU can take hours and may be interrupted.
*   **Decision**: Notebook 03 writes manifest rows and handcrafted feature rows every 25 records.
*   **Rationale**: A crash mid-run can resume from cached PNGs instead of restarting from record zero.

---

## Changelog

| Date (UTC) | Phase | Summary | Key metrics | Commit |
|---|---|---|---|---|
| 2026-06-14 | 0–1 | Centralized config, hardened notebooks, validated B0 smoke test | Acc 88.33%, macro-F1 80.00% | `76d159919b99152566c046d0577afa07a8cd588e` |
| 2026-06-14 | 3–4 | Fused predictor, dashboard integration, regression tests | 2/2 tests pass | pending local commit |
| 2026-06-14 | 2 | EfficientNet-B4 production run on CPU (1000 records, 380×380) | Acc 92.00%, macro-F1 89.52% | pending local commit |

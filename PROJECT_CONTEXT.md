# Project Context: Deep Hybrid ECG Arrhythmia Classification

This document provides the clinical context, medical definitions, and engineering specifications of features used in the ECG Arrhythmia classification project.

---

## 🎯 Clinical Goal
Early detection of cardiac arrhythmias is vital for preventing serious events such as stroke, heart failure, and sudden cardiac arrest. 
Electrocardiograms (ECGs) measure the heart's electrical activity using multiple skin electrodes. While traditional machine learning models rely on statistical summaries of these waveforms, they often miss subtle, non-linear waveshape deformations (e.g., changes in the P-wave or ST-segment). Conversely, deep learning models capture these visual patterns but act as "black boxes."

This project implements a **hybrid feature classification pipeline** that combines:
1. **Handcrafted clinical features** that are easily interpretable by cardiologists.
2. **Deep representation embeddings** extracted from 2D time-frequency scalograms using a convolutional neural network (CNN) model.

By combining these two feature sources, the system leverages both interpretable clinical parameters and detailed visual signal patterns.

---

## 🩺 Clinical Class Mapping & SNOMED-CT Auditing
ECG recordings are labeled using standard SNOMED Clinical Terms (SNOMED-CT). The project maps these high-granularity codes into three primary classes:

| Class Code | Class Name | Target SNOMED-CT Codes | Clinical Description |
|---|---|---|---|
| **0** | **Normal** | `426783006` | **Normal Sinus Rhythm (NSR)**: Regular heart rhythm with normal rate (60–100 bpm), standard P-wave, QRS complex, and T-wave sequence. |
| **1** | **Arrhythmia** | `164889003`, `164890007`, `426177001` | **Atrial Fibrillation (AFib) & Tachycardias**: Arrhythmias marked by rapid and irregular atrial electrical activity, showing absent P-waves and fluctuating R-to-R intervals. |
| **2** | **Other / Unknown** | All other diagnostic codes | Fallback category capturing alternative arrhythmias (e.g., Bradycardias, Bundle Branch Blocks) or recordings with incomplete diagnoses. |

---

## 📐 Detailed Clinical & Handcrafted Feature Specifications

Traditional ECG classification leverages temporal, amplitude, and statistical properties of the preprocessed ECG signal. In our pipeline, `src/handcrafted_features_v2.py` extracts a 17-dimensional feature vector from the primary lead:

### 1. Statistical Time-Domain Features
*   **Mean ($L_1$ norm center)**: Represents the baseline electrical offset.
    $$\text{Mean} = \frac{1}{N} \sum_{i=1}^{N} x_i$$
*   **Standard Deviation ($\sigma$)**: Measures the overall variability of the signal amplitude.
    $$\sigma = \sqrt{\frac{1}{N} \sum_{i=1}^{N} (x_i - \text{Mean})^2}$$
*   **Maximum & Minimum**: Capture absolute peak voltages, helping flag hyper-voltage anomalies or low-voltage artifacts.
*   **Signal Energy ($E$)**: Represents the total electrical power of the recording.
    $$E = \sum_{i=1}^{N} x_i^2$$
*   **Zero Crossing Rate (ZCR)**: The number of times the signal crosses the zero baseline. This metric captures frequency characteristics and noise density.
    $$\text{ZCR} = \sum_{i=1}^{N-1} \mathbb{I}(x_i \cdot x_{i+1} < 0)$$
*   **Skewness**: Measures the asymmetry of the amplitude distribution around the mean (useful for flagging asymmetric waves like tall T-waves).
    $$\text{Skewness} = \frac{\frac{1}{N} \sum_{i=1}^{N} (x_i - \text{Mean})^3}{\sigma^3}$$
*   **Kurtosis**: Measures the peakedness of the signal distribution (useful for flagging sharp R-wave spikes).
    $$\text{Kurtosis} = \frac{\frac{1}{N} \sum_{i=1}^{N} (x_i - \text{Mean})^4}{\sigma^4} - 3$$

### 2. Heart Rate & Heart Rate Variability (HRV) Features
These metrics are calculated using detected R-peaks (peaks in the QRS complex) and their intervals ($RR$ intervals in milliseconds):
*   **Heart Rate (HR)**: The average beats per minute (BPM) over the recording duration.
    $$\text{HR} = \frac{\text{Peak Count}}{\text{Duration in Seconds}} \times 60$$
*   **Mean RR ($RR_{\text{mean}}$)**: The average duration of intervals between successive heartbeats.
    $$RR_{\text{mean}} = \frac{1}{M} \sum_{j=1}^{M} RR_j$$
*   **SDNN (Standard Deviation of NN/RR intervals)**: Measures total autonomic HRV. Higher values indicate normal heart rate fluctuations, while lower values can signal illness or stress.
    $$\text{SDNN} = \sqrt{\frac{1}{M} \sum_{j=1}^{M} (RR_j - RR_{\text{mean}})^2}$$
*   **RMSSD (Root Mean Square of Successive Differences)**: Reflects short-term heartbeat variations, which are primarily driven by vagal (parasympathetic) activity. This metric is a key indicator for irregular rhythms like Atrial Fibrillation.
    $$\text{RMSSD} = \sqrt{\frac{1}{M-1} \sum_{j=1}^{M-1} (RR_{j+1} - RR_j)^2}$$
*   **pNN50**: The percentage of successive RR interval differences that exceed 50 milliseconds.
    $$\text{pNN50} = \frac{1}{M-1} \sum_{j=1}^{M-1} \mathbb{I}(|RR_{j+1} - RR_j| > 50\text{ ms}) \times 100$$
*   **RR Range**: The difference between the longest and shortest RR intervals.
    $$\text{RR Range} = \max(RR) - \min(RR)$$
*   **RR Coefficient of Variation (RR CV)**: A normalized measure of heart rate dispersion.
    $$\text{RR CV} = \frac{\text{SDNN}}{RR_{\text{mean}}}$$

### 3. Morphological Proxies
*   **QRS Width Proxy Mean & Standard Deviation**: The width of the QRS complex indicates how long electrical depolarization takes to travel through the ventricles. Wider complexes can point to conditions like bundle branch blocks. Our pipeline estimates this by measuring the signal duration around each R-peak within a $\pm 30\text{ ms}$ window.

---

## 🖼️ Deep Representations & Continuous Wavelet Transform
To capture transient changes in both time and frequency, the preprocessed ECG signal is converted into a 2D **CWT Scalogram image**:

1.  **Continuous Wavelet Transform (CWT)**: Decomposes the signal using the complex Morlet wavelet ($\psi(t) = e^{-t^2/2} \cos(5t)$). We evaluate scale coefficients across a $0.5 - 40\text{ Hz}$ frequency range.
2.  **3-Channel Stacking**: Leads `I`, `II`, and `V5` represent orthogonal electrical axes. The scalogram for Lead `I` is mapped to the Red channel, Lead `II` to Green, and Lead `V5` to Blue.
3.  **Log Power Scaling**: Applies a logarithmic compression ($P = \log(1 + |C|^2)$) and min-max normalization to fit within standard $[0, 255]$ pixel values.
4.  **Deep Feature Extraction**: The stacked RGB scalogram is resized to $224 \times 224$ (or $380 \times 380$ for B4) and passed through a pretrained CNN. Extracting activations from the final average pooling layer yields a dense 1280-dimension embedding vector that represents the visual structures of the ECG.

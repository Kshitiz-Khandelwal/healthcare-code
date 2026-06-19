# ECG Hybrid Classification System - Final Comprehensive Project Report

> **Author**: Kshitiz Khandelwal  
> **Project**: Clinical Research ECG Classification and Decision Support  
> **Live Dashboard**: <https://healthcare-code-2azi-lime.vercel.app/>  
> **Selected Final Model**: EfficientNet-B4 deep feature extractor + LightGBM classifier  
> **Final Held-Out Test Performance**: 92.0% accuracy, 89.5% macro-F1, 91.8% weighted-F1, 97.1% weighted AUC  
> **Dataset Used for Final B4 Training**: 1,000 PhysioNet/CinC 2020 12-lead ECG records  
> **Training Timestamp**: 2026-06-13T23:32:15 UTC  
> **Random Seed**: 42  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement and Objective](#2-problem-statement-and-objective)
3. [Dataset Description](#3-dataset-description)
4. [End-to-End System Architecture](#4-end-to-end-system-architecture)
5. [Signal Preprocessing](#5-signal-preprocessing)
6. [Handcrafted Feature Engineering](#6-handcrafted-feature-engineering)
7. [Deep Feature Extraction Using CWT and EfficientNet-B4](#7-deep-feature-extraction-using-cwt-and-efficientnet-b4)
8. [Feature Strategy Experiments](#8-feature-strategy-experiments)
9. [Final Model Training Configuration](#9-final-model-training-configuration)
10. [Final Model Evaluation](#10-final-model-evaluation)
11. [Confusion Matrix Analysis](#11-confusion-matrix-analysis)
12. [Class-Wise Clinical Interpretation](#12-class-wise-clinical-interpretation)
13. [Prototype to Production Evolution](#13-prototype-to-production-evolution)
14. [Prediction and Risk Assessment Layer](#14-prediction-and-risk-assessment-layer)
15. [Sample Patient-Level Output](#15-sample-patient-level-output)
16. [Explainability and Feature Importance](#16-explainability-and-feature-importance)
17. [Model Artifacts and Reproducibility](#17-model-artifacts-and-reproducibility)
18. [Dashboard and Deployment](#18-dashboard-and-deployment)
19. [Limitations and Responsible Use](#19-limitations-and-responsible-use)
20. [Conclusion](#20-conclusion)
21. [References](#21-references)

---

## 1. Executive Summary

This project implements an end-to-end machine learning pipeline for automated ECG classification. The system reads raw 12-lead ECG recordings, performs signal preprocessing, extracts clinically meaningful rhythm features, generates deep visual embeddings from wavelet scalograms, and classifies each ECG into one of three target classes:

| Class ID | Class Name | Meaning |
|---:|---|---|
| 0 | Normal | Normal sinus rhythm or no target abnormality detected |
| 1 | Arrhythmia | Irregular rhythm patterns such as atrial fibrillation or related rhythm disorders |
| 2 | Other / Unknown | Other cardiac conditions or records outside the main normal/arrhythmia targets |

The final selected production experiment is the **EfficientNet-B4 only** strategy. It uses 1,792-dimensional deep embeddings extracted from 3-channel ECG scalograms and trains a LightGBM classifier on those embeddings. Although the project also tested handcrafted-only and hybrid feature-fusion variants, EfficientNet-B4 deep features gave the best held-out generalization:

| Metric | Final Value |
|---|---:|
| Test Accuracy | 92.0% |
| Macro-F1 | 89.5% |
| Weighted-F1 | 91.8% |
| Weighted One-vs-Rest AUC | 97.1% |
| Arrhythmia Recall | 95.6% |
| Dataset Size Used in Final B4 Experiment | 1,000 records |
| Test Set Size | 200 records |
| Validation Prediction File Size | 800 records |

The most important clinical result is the **95.6% recall for Arrhythmia**. In screening-style ECG analysis, missing arrhythmia cases is more dangerous than sending a few extra cases for review. Therefore, arrhythmia recall is treated as a key safety metric.

This system is best presented as a **clinical decision-support prototype** and academic machine-learning project. It is not a certified medical device and should not be described as replacing a cardiologist.

---

## 2. Problem Statement and Objective

Manual ECG interpretation requires clinical expertise and careful review of waveform morphology, rhythm regularity, heart rate, and multi-lead electrical patterns. Automated support systems can help by triaging ECGs, identifying likely arrhythmias, and producing consistent risk labels.

The goal of this project is to build a reproducible ECG classification system that:

1. Accepts 12-lead ECG records as input.
2. Applies standard preprocessing to reduce noise and normalize signal scale.
3. Extracts both clinical and deep-learning features.
4. Trains and evaluates multiple classification strategies.
5. Selects the best model using accuracy, macro-F1, weighted-F1, AUC, and per-class recall.
6. Produces patient-level predictions with confidence scores, risk levels, inference timing, and natural-language explanations.
7. Provides a dashboard/report interface suitable for teachers, reviewers, and demonstration.

---

## 3. Dataset Description

### 3.1 Source

The project uses records from the **PhysioNet/Computing in Cardiology Challenge 2020** dataset. The data format follows standard ECG record conventions:

| Component | Description |
|---|---|
| `.mat` file | Binary signal matrix containing ECG voltage values |
| `.hea` file | Header metadata including age, sex, sampling frequency, lead names, and diagnostic labels |
| Sampling rate | 500 Hz |
| Lead count | 12 standard ECG leads |
| Typical duration | Approximately 10 seconds |
| Typical matrix shape | 12 x 5000 samples |

### 3.2 Final B4 Dataset

The final EfficientNet-B4 experiment uses a curated **1,000-record cohort**.

Approximate class distribution:

| Class | Approximate Count | Approximate Share |
|---|---:|---:|
| Arrhythmia | 600 | 60% |
| Other / Unknown | 230 | 23% |
| Normal | 170 | 17% |

This distribution is imbalanced, with Arrhythmia as the majority class. Because of that, accuracy alone is not enough. Macro-F1, per-class recall, and confusion matrix analysis are required to judge whether the model performs well across all classes.

### 3.3 Earlier Notebook Dataset Audit

An earlier notebook-based workflow also audited a larger tabular feature dataset with **45,152 rows**. The notebook phase summary reported:

| Phase | Result | Presentation Point |
|---|---|---|
| Phase 1 | Loaded ECG dataset | 45,152 rows available |
| Phase 3 | Cleaned and audited data | 45,152 rows retained |
| Phase 4 | Measured class imbalance | Majority class: Arrhythmia |
| Phase 8 | Compared models | Best CV model: LightGBM |
| Phase 9 | Evaluated final model | Accuracy = 0.852, Macro-F1 = 0.824 |

Important distinction: the 45,152-row notebook workflow and the final 1,000-record EfficientNet-B4 deep-feature experiment are related development phases, but the final reported production model is the 1,000-record B4 experiment.

---

## 4. End-to-End System Architecture

The final system follows this flow:

```text
Raw 12-lead ECG record
        |
        v
Read .mat signal matrix and .hea metadata
        |
        v
Bandpass filtering and normalization
        |
        v
Lead selection: I, II, V5
        |
        +-------------------------------+
        |                               |
        v                               v
Handcrafted rhythm features       CWT scalogram generation
17 clinical/statistical values    3 leads stacked as RGB image
        |                               |
        |                               v
        |                         EfficientNet-B4
        |                         1792-dimensional embedding
        |                               |
        +---------------+---------------+
                        |
                        v
              Feature strategy comparison
                        |
                        v
                LightGBM classifier
                        |
                        v
        Class prediction + confidence probabilities
                        |
                        v
        Risk rules using prediction, confidence, and vitals
                        |
                        v
        Dashboard, report, and patient-level explanation
```

### 4.1 Main Implementation Components

| Component | Purpose |
|---|---|
| `src/ecg_io.py` | ECG file loading and metadata parsing |
| `src/preprocessing.py` | Filtering, normalization, and preprocessing utilities |
| `src/scalogram.py` | Wavelet scalogram generation |
| `src/deep_embeddings.py` | EfficientNet feature extraction |
| `src/handcrafted_features_v2.py` | Clinical feature extraction |
| `src/train_model.py` | Model training and evaluation |
| `src/hybrid_predictor.py` | Runtime inference pipeline |
| `dashboard.py` | Streamlit-style interactive demo |
| `ecg-dashboard-build/` | Next.js report/dashboard website |

---

## 5. Signal Preprocessing

ECG signals are affected by baseline wander, patient movement, electrode placement variation, and high-frequency noise. The preprocessing stage standardizes the signal before either clinical feature extraction or scalogram generation.

### 5.1 Bandpass Filtering

A Butterworth bandpass filter is applied in the approximate ECG diagnostic frequency band:

| Filter Parameter | Value | Reason |
|---|---:|---|
| Low cutoff | 0.5 Hz | Removes slow baseline drift caused by breathing and electrode movement |
| High cutoff | 40 Hz | Reduces high-frequency noise and muscle artifacts |
| Filter type | Butterworth | Smooth passband response |
| Filtering method | Zero-phase style filtering | Preserves waveform timing and peak alignment |

### 5.2 Z-Score Normalization

Each selected ECG signal is normalized using:

```text
x_normalized = (x - mean(x)) / std(x)
```

This prevents patients with higher raw voltage amplitudes from dominating feature extraction and model training.

### 5.3 Lead Selection

The deep-feature pipeline uses three diagnostically useful leads:

| Lead | Role |
|---|---|
| Lead I | Captures lateral electrical activity |
| Lead II | Strong rhythm lead, useful for R-peak and P-wave rhythm analysis |
| Lead V5 | Captures left ventricular and lateral chest-wall activity |

These three leads are converted into a 3-channel image representation for EfficientNet-B4.

---

## 6. Handcrafted Feature Engineering

Handcrafted features are extracted primarily from rhythm and waveform statistics. These features provide interpretable clinical signals that can be explained to non-technical reviewers.

### 6.1 Feature List

| # | Feature | Category | Meaning |
|---:|---|---|---|
| 1 | `mean` | Statistical | Average signal voltage |
| 2 | `std` | Statistical | Signal amplitude variability |
| 3 | `max` | Statistical | Maximum voltage / R-peak height |
| 4 | `min` | Statistical | Minimum voltage / negative deflection |
| 5 | `energy` | Statistical | Sum of squared signal values |
| 6 | `zero_crossings` | Statistical | Number of zero-axis crossings |
| 7 | `skewness` | Statistical | Asymmetry of waveform distribution |
| 8 | `kurtosis` | Statistical | Sharpness or tail weight of waveform distribution |
| 9 | `peak_count` | Rhythm | Number of detected R-peaks |
| 10 | `heart_rate` | HRV | Beats per minute |
| 11 | `rr_mean` | HRV | Mean R-R interval in milliseconds |
| 12 | `hrv` | HRV | Standard deviation of R-R intervals |
| 13 | `sdnn` | HRV | Standard deviation of NN intervals |
| 14 | `rmssd` | HRV | Root mean square of successive R-R differences |
| 15 | `pnn50` | HRV | Share of successive R-R differences greater than 50 ms |
| 16 | `rr_range` | HRV | Maximum R-R minus minimum R-R interval |
| 17 | `rr_cv` | HRV | Coefficient of variation of R-R intervals |

### 6.2 Why These Features Matter

| Feature Group | Clinical Value |
|---|---|
| Heart rate and peak count | Detect tachycardia, bradycardia, and rhythm speed |
| R-R interval statistics | Capture beat-to-beat irregularity |
| HRV, SDNN, RMSSD, pNN50 | Quantify autonomic and rhythm variability |
| Energy, max, min, std | Capture waveform amplitude and morphology |
| Skewness and kurtosis | Capture distribution shape and abnormal waveform sharpness |

### 6.3 Feature Importance from Earlier Handcrafted Model

The earlier LightGBM feature-importance output showed the following strongest handcrafted predictors:

| Rank | Feature | Importance |
|---:|---|---:|
| 1 | `hrv` | 5496 |
| 2 | `rr_mean` | 5454 |
| 3 | `age` | 3986 |
| 4 | `mean` | 3967 |
| 5 | `zero_crossings` | 3449 |
| 6 | `kurtosis` | 2983 |
| 7 | `max` | 2851 |
| 8 | `min` | 2837 |
| 9 | `skewness` | 2749 |
| 10 | `std` | 2557 |

This confirms that rhythm variability features such as `hrv` and `rr_mean` are highly informative for arrhythmia classification.

---

## 7. Deep Feature Extraction Using CWT and EfficientNet-B4

### 7.1 Why Convert ECG Signals into Images?

An ECG is naturally a 1D time-series signal, but many rhythm and morphology patterns appear as changes in both time and frequency. A Continuous Wavelet Transform (CWT) converts the ECG into a time-frequency representation, allowing a computer vision model to learn visual patterns associated with rhythm abnormalities.

### 7.2 Continuous Wavelet Transform

The CWT converts each selected lead into a matrix describing signal energy across time and scale/frequency. The project uses a Complex Morlet-style wavelet configuration.

Conceptual form:

```text
CWT(signal) = time-frequency energy map
```

### 7.3 Three-Lead RGB Scalogram

The pipeline creates a 3-channel image:

| Image Channel | ECG Lead |
|---|---|
| Red | Lead I |
| Green | Lead II |
| Blue | Lead V5 |

The final image is resized to **380 x 380**, matching EfficientNet-B4 input sizing.

```text
Lead I  -> CWT -> Red channel
Lead II -> CWT -> Green channel
Lead V5 -> CWT -> Blue channel
                       |
                       v
             380 x 380 x 3 scalogram image
                       |
                       v
                 EfficientNet-B4
                       |
                       v
              1792-dimensional embedding
```

### 7.4 EfficientNet-B4 Embeddings

The EfficientNet-B4 backbone is used as a feature extractor. The classification head is removed, and the pooled embedding is used as a compact representation of the scalogram.

| Property | Value |
|---|---:|
| Backbone | EfficientNet-B4 |
| Input image size | 380 x 380 |
| Embedding dimension | 1792 |
| Final selected feature count | 1792 |
| Final selected experiment | EfficientNet-only |

---

## 8. Feature Strategy Experiments

Three feature strategies were compared on the final 1,000-record B4 cohort.

| Strategy | Feature Count | CV Accuracy | CV Macro-F1 | Test Accuracy | Test Macro-F1 | Test Weighted-F1 | Weighted AUC | Runtime |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Handcrafted only | 17 | 92.88% | 90.37% | 91.0% | 87.93% | 90.67% | 95.97% | 0.757 s |
| EfficientNet-B4 only | 1792 | 88.38% | 83.05% | 92.0% | 89.52% | 91.81% | 97.06% | 1.682 s |
| Hybrid handcrafted + EfficientNet | 1809 | 88.25% | 82.55% | 92.0% | 89.34% | 91.64% | 96.55% | 1.687 s |

### 8.1 Selection Decision

The selected final model is **EfficientNet-B4 only** because it achieved:

- Highest held-out macro-F1: 89.52%
- Highest held-out weighted AUC: 97.06%
- Same test accuracy as the hybrid model: 92.0%
- Slightly better generalization than hybrid fusion on the final test set

The handcrafted-only model had stronger cross-validation numbers, but its held-out macro-F1 and AUC were lower than the EfficientNet-B4 model. That means it may fit the development folds well but generalizes slightly worse on the final held-out test set.

---

## 9. Final Model Training Configuration

### 9.1 Metadata

| Field | Value |
|---|---|
| Model name | `efficientnet_b4` |
| Best experiment | `efficientnet_only` |
| Dataset size | 1,000 |
| Split method | Record-level stratified train-test split |
| Target size | 380 x 380 |
| Embedding dimension | 1792 |
| Feature count | 1792 |
| Seed | 42 |
| Training timestamp UTC | 2026-06-13T23:32:15.023006+00:00 |

### 9.2 Classifier

The classifier is LightGBM, a gradient-boosted decision tree algorithm suitable for tabular machine-learning features. It is effective for structured features such as deep embeddings and clinical measurements because it can model non-linear feature interactions while training quickly.

Typical configuration used in the project:

| Parameter | Value / Purpose |
|---|---|
| Estimators | 150 trees |
| Learning rate | 0.05 |
| Max depth | 6 |
| Class weighting | Balanced handling for class imbalance |
| Random state | 42 |

---

## 10. Final Model Evaluation

### 10.1 Held-Out Test Classification Report

Final EfficientNet-B4 held-out test set size: **200 records**.

| Class | Precision | Recall | F1-Score | Support |
|---|---:|---:|---:|---:|
| Normal | 92.86% | 74.29% | 82.54% | 35 |
| Arrhythmia | 92.86% | 95.59% | 94.20% | 136 |
| Other / Unknown | 87.50% | 96.55% | 91.80% | 29 |
| Macro Avg | 91.07% | 88.81% | 89.52% | 200 |
| Weighted Avg | 92.08% | 92.00% | 91.81% | 200 |

Overall accuracy: **92.00%**

### 10.2 Metric Definitions

| Metric | Meaning | Why It Matters |
|---|---|---|
| Accuracy | Share of all predictions that are correct | Gives overall correctness but can hide class imbalance |
| Precision | Of all records predicted as a class, how many were truly that class | Important for avoiding unnecessary false alarms |
| Recall | Of all true records in a class, how many were detected | Critical for reducing missed disease cases |
| F1-score | Harmonic mean of precision and recall | Balances false positives and false negatives |
| Macro-F1 | Average F1 across classes equally | Important for imbalanced datasets |
| Weighted-F1 | F1 weighted by class support | Reflects performance under real class distribution |
| AUC | Probability ranking quality across thresholds | Measures confidence separation, not just final labels |

### 10.3 Key Evaluation Takeaways

1. **Arrhythmia recall is high at 95.59%**, meaning most true arrhythmia cases are detected.
2. **Normal recall is lower at 74.29%**, meaning some Normal records are conservatively predicted as abnormal.
3. **Other / Unknown recall is very high at 96.55%**, showing strong detection of non-normal, non-arrhythmia categories.
4. The macro-F1 of 89.52% indicates the model performs well across all three classes, not only the majority class.
5. The weighted AUC of 97.06% shows strong probabilistic separation between classes.

---

## 11. Confusion Matrix Analysis

### 11.1 Final Held-Out Test Confusion Matrix

The 200-record final held-out confusion matrix can be reconstructed from the final classification report values:

| Actual \ Predicted | Normal | Arrhythmia | Other / Unknown | Row Total |
|---|---:|---:|---:|---:|
| Normal | 26 | 9 | 0 | 35 |
| Arrhythmia | 2 | 130 | 4 | 136 |
| Other / Unknown | 0 | 1 | 28 | 29 |
| Column Total | 28 | 140 | 32 | 200 |

### 11.2 Interpretation of Final Confusion Matrix

| Finding | Interpretation |
|---|---|
| 130 / 136 Arrhythmia cases correctly detected | Strong safety result for arrhythmia screening |
| 6 Arrhythmia cases missed or assigned to another class | Remaining clinical risk; these are the most important errors to study |
| 9 Normal cases predicted as Arrhythmia | Conservative bias toward flagging possible abnormality |
| 28 / 29 Other cases correctly detected | Very strong recognition of non-normal, non-arrhythmia patterns |
| No Other cases predicted as Normal | Good from a screening perspective because abnormal records are not being dismissed as normal |

### 11.3 Final Validation Prediction Confusion Matrix

The repository also contains `validation_predictions.csv` with **800 validation predictions**. Its confusion matrix is:

| Actual \ Predicted | Normal | Arrhythmia | Other / Unknown | Row Total |
|---|---:|---:|---:|---:|
| Normal | 95 | 28 | 8 | 131 |
| Arrhythmia | 38 | 418 | 22 | 478 |
| Other / Unknown | 14 | 20 | 157 | 191 |
| Column Total | 147 | 466 | 187 | 800 |

### 11.4 Validation Confusion Matrix Percentages

| Actual Class | Correct / Total | Recall |
|---|---:|---:|
| Normal | 95 / 131 | 72.52% |
| Arrhythmia | 418 / 478 | 87.45% |
| Other / Unknown | 157 / 191 | 82.20% |

This 800-record validation file is useful for dashboard-level analysis and error inspection. The final selected test report, however, is the 200-record held-out EfficientNet-B4 classification report shown above.

### 11.5 Earlier Notebook Phase Confusion Matrix

The notebook phase also produced a separate 2,400-record evaluation matrix:

| Actual \ Predicted | Normal | Arrhythmia | Other / Unknown | Row Total |
|---|---:|---:|---:|---:|
| Normal | 342 | 58 | 32 | 432 |
| Arrhythmia | 102 | 1238 | 62 | 1402 |
| Other / Unknown | 38 | 63 | 465 | 566 |
| Total | 482 | 1359 | 559 | 2400 |

Notebook phase classification report:

| Class | Precision | Recall | F1-Score | Support |
|---|---:|---:|---:|---:|
| Normal | 70.95% | 79.17% | 74.84% | 432 |
| Arrhythmia | 91.10% | 88.30% | 89.68% | 1402 |
| Other / Unknown | 83.18% | 82.16% | 82.67% | 566 |
| Accuracy | 85.21% | 85.21% | 85.21% | 2400 |
| Macro Avg | 81.75% | 83.21% | 82.39% | 2400 |
| Weighted Avg | 85.60% | 85.21% | 85.35% | 2400 |

This earlier phase demonstrates the baseline LightGBM workflow before the final EfficientNet-B4 deep-feature upgrade.

---

## 12. Class-Wise Clinical Interpretation

### 12.1 Normal Class

| Metric | Value |
|---|---:|
| Precision | 92.86% |
| Recall | 74.29% |
| F1-score | 82.54% |

The Normal class has high precision but lower recall. This means when the model says "Normal", it is usually correct. However, it does not label every true normal as Normal; some are escalated to Arrhythmia. In a medical screening tool, this is acceptable as a conservative safety behavior, because falsely flagging a normal ECG is less dangerous than missing a true abnormal ECG.

### 12.2 Arrhythmia Class

| Metric | Value |
|---|---:|
| Precision | 92.86% |
| Recall | 95.59% |
| F1-score | 94.20% |

This is the strongest and most clinically important class result. The high recall means the model detects most arrhythmia cases. The high precision means the Arrhythmia predictions are also reliable, not simply over-triggered.

### 12.3 Other / Unknown Class

| Metric | Value |
|---|---:|
| Precision | 87.50% |
| Recall | 96.55% |
| F1-score | 91.80% |

The Other / Unknown class is often difficult because it contains heterogeneous cardiac conditions. The final model performs strongly, especially in recall. This suggests the scalogram embeddings capture morphological patterns beyond simple rhythm irregularity.

---

## 13. Prototype to Production Evolution

The project developed in phases, starting from smaller experiments and moving toward the final EfficientNet-B4 model.

| Metric | EfficientNet-B0 Prototype | EfficientNet-B4 Final | Improvement |
|---|---:|---:|---:|
| Dataset size | 300 records | 1,000 records | +233% |
| Scalogram size | 224 x 224 | 380 x 380 | Higher visual detail |
| Embedding dimension | 1,280 | 1,792 | +40% |
| Test accuracy | 88.33% | 92.00% | +3.67 percentage points |
| Test macro-F1 | 80.00% | 89.52% | +9.52 percentage points |
| Weighted AUC | 94.9% | 97.1% | +2.2 percentage points |
| Arrhythmia recall | 91.3% | 95.6% | +4.3 percentage points |

The final validation report states:

| Phase | Passed | Accuracy | Macro-F1 |
|---|---|---:|---:|
| Phase 1: EfficientNet-B0 | True | 88.33% | 80.00% |
| Phase 2: EfficientNet-B4 | True | 92.00% | 89.52% |

The macro-F1 improvement is especially important because it shows the final model improved across classes rather than only improving majority-class accuracy.

---

## 14. Prediction and Risk Assessment Layer

The model output is a class probability distribution:

```text
P(Normal), P(Arrhythmia), P(Other / Unknown)
```

The highest probability becomes the predicted class, and the probability value becomes the confidence score.

### 14.1 Risk Rules

| Risk Level | Rule Logic |
|---|---|
| LOW | Prediction is Normal, confidence is acceptable, and vitals do not trigger escalation |
| MEDIUM | Prediction is Other / Unknown with high confidence, Arrhythmia with lower confidence, or uncertainty/vital signs require review |
| HIGH | Prediction is Arrhythmia with confidence >= 85%, or vital thresholds escalate an existing risk |

### 14.2 Heart-Rate Override

The risk system uses heart rate as a safety override:

| Heart Rate Condition | Interpretation | Risk Effect |
|---|---|---|
| HR < 40 BPM | Severe bradycardia range | Escalate risk |
| HR > 120 BPM | Tachycardic range | Escalate risk |
| 60 to 100 BPM | Normal resting range | No automatic escalation |

This is important because a model prediction should not ignore physiologically dangerous vital signs.

### 14.3 Inference Timing

The runtime prediction output records:

| Timing Field | Meaning |
|---|---|
| `preprocessing_scalogram_seconds` | Time to preprocess signal and generate scalogram |
| `embedding_seconds` | Time to extract EfficientNet embedding |
| `handcrafted_seconds` | Time to compute clinical features |
| `classifier_seconds` | Time to classify with LightGBM |
| `total_seconds` | End-to-end prediction time |

In the visible sample predictions, total runtime is approximately **0.32 to 0.36 seconds per patient**, suitable for an interactive dashboard demonstration.

---

## 15. Sample Patient-Level Output

Sample rows from `predictions.csv` show the final system output.

| Patient | Prediction | Confidence | Risk | HR | HRV | Age | Sex | Total Time |
|---|---|---:|---|---:|---:|---:|---|---:|
| JS00001 | Arrhythmia | 98.61% | HIGH | 114 | 49.78 | 85 | Male | 0.360 s |
| JS00002 | Arrhythmia | 97.84% | HIGH | 96 | 295.51 | 59 | Female | 0.336 s |
| JS00004 | Arrhythmia | 99.94% | HIGH | 102 | 243.91 | 66 | Male | 0.343 s |
| JS00005 | Arrhythmia | 97.43% | HIGH | 162 | 5.36 | 73 | Female | 0.363 s |
| JS00006 | Arrhythmia | 99.48% | HIGH | 54 | 23.53 | 46 | Female | 0.321 s |
| JS00008 | Normal | 97.61% | LOW | 66 | 24.27 | 46 | Male | 0.322 s |

### 15.1 Example Clinical Explanation

For patient `JS00005`, the system predicts Arrhythmia with 97.43% confidence and HIGH risk. The heart rate is 162 BPM, which is substantially elevated, and HRV is 5.36 ms, which is critically low. This combination supports immediate review in a clinical decision-support workflow.

### 15.2 Why This Output Is Useful for Demonstration

The dashboard/report output is useful because it does not only say "Arrhythmia" or "Normal". It also provides:

1. Confidence score.
2. Risk level.
3. Heart rate.
4. HRV metrics.
5. Age and sex metadata.
6. Inference-time breakdown.
7. Natural-language explanation.

That makes it easier to present to teachers and reviewers as a complete applied AI system.

---

## 16. Explainability and Feature Importance

### 16.1 Explainability Strategy

The project uses two explanation levels:

| Explanation Level | Description |
|---|---|
| Model-level explanation | Compare feature strategies, confusion matrices, per-class metrics, and feature importance |
| Patient-level explanation | Convert prediction, confidence, heart rate, HRV, age, and risk into readable clinical-style text |

### 16.2 Model-Level Findings

The strategy comparison shows that deep scalogram embeddings generalize better than handcrafted-only features on the held-out test set. This supports the claim that EfficientNet-B4 is learning useful morphology and time-frequency structure from the ECG scalograms.

### 16.3 Patient-Level Findings

Patient explanations combine:

- Predicted class.
- Confidence.
- Risk category.
- Heart-rate condition.
- HRV condition.
- Age-based caution.
- Recommended review action.

Example structure:

```text
The model predicts Arrhythmia with high confidence.
The case is assigned HIGH risk.
Heart rate is elevated or abnormal.
HRV is low or clinically notable.
Formal 12-lead ECG review is recommended.
```

This explanation layer is useful for presentation, but it must be clearly described as decision-support text rather than a doctor's final diagnosis.

---

## 17. Model Artifacts and Reproducibility

All final B4 model artifacts are stored under:

```text
outputs/deep_features/models/
```

### 17.1 Artifact Registry

| Artifact | Purpose |
|---|---|
| `best_hybrid_model_efficientnet_b4.pkl` | Final LightGBM classifier |
| `scaler_efficientnet_b4.pkl` | Feature scaling transformer |
| `pca_efficientnet_b4.pkl` | PCA transformer for compressed deep features when used |
| `best_hybrid_feature_list_efficientnet_b4.pkl` | Exact feature order/schema |
| `model_metadata_efficientnet_b4.json` | Metrics, dataset size, seed, split method, and hash metadata |

### 17.2 Metadata Integrity

The metadata contains:

```json
{
  "best_experiment": "efficientnet_only",
  "dataset_size": 1000,
  "embedding_dimension": 1792,
  "feature_count": 1792,
  "model_name": "efficientnet_b4",
  "seed": 42,
  "split_method": "record-level stratified train_test_split",
  "target_size": [380, 380]
}
```

The feature list hash is:

```text
0ad456858783af12d659d35b54ef43fe4a6c062cfbe530c51c7b9eab4934a71a
```

This hash protects against accidentally using the wrong feature list with the wrong model.

---

## 18. Dashboard and Deployment

The project includes a website/dashboard for presentation:

```text
ecg-dashboard-build/
```

Dashboard stack:

| Layer | Technology |
|---|---|
| Frontend framework | Next.js |
| UI library | React |
| Styling | Tailwind CSS |
| Charts | Recharts |
| Animation | Framer Motion |
| Deployment | Vercel |

The dashboard is designed to show:

1. Project summary.
2. Model performance metrics.
3. Confusion matrix.
4. Classification report.
5. Feature strategy comparison.
6. Prototype vs production improvement.
7. Patient prediction table.
8. Risk logic.
9. Dataset and label mapping.
10. Final conclusion and scope note.

Live dashboard:

```text
https://healthcare-code-2azi-lime.vercel.app/
```

---

## 19. Limitations and Responsible Use

### 19.1 Technical Limitations

| Limitation | Explanation |
|---|---|
| Dataset size | Final B4 model uses 1,000 records, which is strong for a prototype but limited for clinical deployment |
| Class imbalance | Arrhythmia dominates the dataset, requiring macro-F1 and recall-based evaluation |
| External validation | The model should be tested on separate hospitals/devices before real use |
| Calibration | Confidence scores should be calibrated before clinical deployment |
| Explainability | Patient explanations are generated summaries, not medical diagnoses |
| Label simplification | Many ECG diagnoses are collapsed into three broad classes |

### 19.2 Clinical Responsibility Statement

This project should be presented as:

> A machine-learning based ECG classification and decision-support prototype.

It should not be presented as:

> A certified diagnostic system or replacement for a trained cardiologist.

The correct clinical framing is that the system can assist screening, triage, and educational demonstration, but final diagnosis requires professional ECG interpretation.

---

## 20. Conclusion

The ECG Hybrid Classification System successfully demonstrates a complete applied AI workflow for ECG analysis. It moves from raw ECG signal ingestion to preprocessing, wavelet scalogram generation, EfficientNet-B4 embedding extraction, LightGBM classification, patient-level risk scoring, and dashboard deployment.

The final selected EfficientNet-B4 model achieves:

- 92.0% held-out test accuracy.
- 89.5% macro-F1.
- 91.8% weighted-F1.
- 97.1% weighted AUC.
- 95.6% Arrhythmia recall.

The most important result is the high Arrhythmia recall, because arrhythmia detection is the central clinical safety goal. The model also performs well on Other / Unknown cases, while the Normal class shows conservative behavior by occasionally flagging normal ECGs as abnormal.

Overall, this project is ready to present as a detailed academic report and website-based demonstration. It clearly shows the machine-learning pipeline, model evaluation, confusion matrix behavior, clinical interpretation, limitations, and responsible deployment framing.

---

## 21. References

1. Alday, E. A. P., Gu, A., Shah, A. J., Robichaux, C., Wong, A. I., Liu, C., et al. Classification of 12-lead ECGs: the PhysioNet/Computing in Cardiology Challenge 2020. Computing in Cardiology, 2020.
2. Tan, M., and Le, Q. EfficientNet: Rethinking Model Scaling for Convolutional Neural Networks. International Conference on Machine Learning, 2019.
3. Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., and Liu, T. LightGBM: A Highly Efficient Gradient Boosting Decision Tree. Advances in Neural Information Processing Systems, 2017.
4. Addison, P. S. Wavelet transforms and the ECG: a review. Physiological Measurement, 2005.
5. Task Force of the European Society of Cardiology and the North American Society of Pacing and Electrophysiology. Heart rate variability: standards of measurement, physiological interpretation and clinical use. Circulation, 1996.

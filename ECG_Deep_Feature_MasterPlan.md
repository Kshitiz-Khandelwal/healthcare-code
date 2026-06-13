# ECG Deep Feature Extraction Master Plan

This document refines the enhanced roadmap into a practical, research-grade implementation plan for the current ECG project.

The goal is not only to add deep learning names like EfficientNet-B4, ViT, ASPP, and ConvNeXt. The goal is to build a defensible pipeline where:

1. handcrafted ECG features provide clinical interpretability,
2. deep features capture waveform/scalogram patterns,
3. hybrid features improve performance honestly,
4. evaluation avoids leakage and inflated metrics,
5. final outputs are easy to present.

---

## 1. What The Faculty Advisor Is Asking For

The advisor's instruction can be interpreted as:

```text
Current system:
Raw ECG -> handcrafted features -> ML classifier

Expected enhanced system:
Raw ECG -> handcrafted features
        -> CNN deep features using EfficientNet-B4
        -> transformer / ConvNeXt features if possible
        -> hybrid feature fusion
        -> final classifier and explainability
```

The important phrase is **feature extraction**. The deep models do not have to be trained end-to-end immediately. First, use them as frozen embedding extractors.

---

## 2. Current Project Status

The project currently has:

- raw 12-lead ECG records in `.mat/.hea` format,
- 45,152 records,
- 500 Hz sampling frequency,
- 5,000 samples per record,
- handcrafted feature CSV,
- LightGBM baseline,
- dashboard and prediction scripts.

This means the next phase should not replace the current work. It should extend it.

---

## 3. Corrected Understanding Of Feature Types

### 3.1 Handcrafted / Crafted Features

These are manually designed ECG features. Your current project already has many:

- `mean`
- `std`
- `max`
- `min`
- `peak_count`
- `heart_rate`
- `energy`
- `zero_crossings`
- `hrv`
- `rr_mean`
- `skewness`
- `kurtosis`
- `age`
- `sex`

These are useful because they are explainable.

### 3.2 Enhanced Handcrafted Features

Before jumping to deep models, improve the handcrafted feature set:

- `sdnn`: standard deviation of NN/RR intervals
- `rmssd`: short-term HRV
- `pnn50`: percentage of RR changes greater than 50 ms
- `rr_range`: max RR minus min RR
- `rr_cv`: RR coefficient of variation
- `qrs_width_proxy`: approximate QRS width from R-peak neighborhood
- per-lead amplitude statistics instead of only mean lead signal

These features are clinically meaningful and can improve the baseline.

### 3.3 Deep CNN Features

Deep CNN features are vectors extracted from a pretrained CNN.

For EfficientNet-B4:

```text
ECG signal -> scalogram image -> EfficientNet-B4 -> embedding vector
```

Use the embedding from the layer before the classifier head.

### 3.4 Transformer Features

Transformer features can come from:

- ViT on ECG scalogram images,
- time-series transformers on raw ECG windows,
- ECG-specific pretrained transformer models.

For this project, ViT on scalogram images is easier to implement and explain.

### 3.5 Hybrid Features

Hybrid features combine multiple sources:

```text
handcrafted features + EfficientNet features + optional ConvNeXt/ViT features
```

The final classifier can be:

- LightGBM,
- Logistic Regression,
- MLP,
- stacking ensemble.

Start with LightGBM because the project already uses it successfully.

---

## 4. Important Corrections To The Existing Enhanced Roadmap

### Correction 1: ImageNet Normalization Is Not Always Wrong

The previous roadmap says not to use ImageNet statistics for ECG scalograms. That is too absolute.

Use this rule:

| Situation | Recommended Normalization |
|---|---|
| Frozen ImageNet-pretrained EfficientNet / ConvNeXt / ViT | Use the official pretrained weights transform, usually ImageNet mean/std |
| Training from scratch | Use dataset-specific mean/std |
| Fine-tuning deeply on ECG images | Start with pretrained transform; optionally compare dataset-specific normalization |

Why: pretrained CNNs learned their first-layer filters under ImageNet normalization. If you change normalization without testing, feature quality can degrade.

### Correction 2: Patient-Level Split May Not Be Available

The `.hea` files inspected in this dataset contain age, sex, diagnosis codes, and signal metadata, but no obvious patient ID field.

Therefore:

1. If a patient identifier exists in dataset documentation, use group split.
2. If no patient identifier exists, use stratified record-level split and clearly state the limitation.
3. Do not invent patient IDs from filenames unless documentation confirms the filename pattern represents patients.

Honesty here matters more than pretending to have patient-level validation.

### Correction 3: ASPP Is Optional, Not A First-Step Requirement

ASPP is useful when building a custom CNN segmentation/classification head. But for your immediate goal, it adds complexity.

Recommended order:

1. EfficientNet-B4 frozen features.
2. Hybrid feature table.
3. LightGBM classifier.
4. Only then consider ASPP or fine-tuning.

### Correction 4: EfficientNet-B4 Requires Compute

EfficientNet-B4 uses larger 380x380 inputs and is heavier than B0/B2.

Practical route:

1. Build pipeline using EfficientNet-B0 on 1,000 to 3,000 records.
2. Confirm embeddings and classifier work.
3. Switch to EfficientNet-B4 for the final run.
4. Cache embeddings so they are not recomputed every notebook run.

### Correction 5: Label Mapping Should Be Reviewed

The current label mapping uses:

- Normal: `426783006`
- Arrhythmia: only a few selected SNOMED codes
- Everything else: Other

This is acceptable for a first 3-class project, but for a stronger research presentation, include a label-mapping audit:

- show which SNOMED codes are most frequent,
- justify which codes are mapped to Arrhythmia,
- keep the mapping fixed before training.

---

## 5. Recommended Final Architecture

Use this as the main project diagram:

```text
                 Raw 12-lead ECG (.mat/.hea)
                            |
        ---------------------------------------------
        |                                           |
Handcrafted Feature Branch                  Deep Feature Branch
        |                                           |
HRV, RR, morphology, stats          Preprocess signal and generate scalograms
        |                                           |
LightGBM baseline table             EfficientNet-B4 frozen embedding
        |                                           |
        ---------------- Hybrid Fusion -------------
                            |
             Scaling + optional PCA / feature selection
                            |
                  Final classifier: LightGBM
                            |
       Accuracy, Macro-F1, per-class F1, AUC, confusion matrix
                            |
             SHAP for tabular + Grad-CAM for image branch
```

---

## 6. Implementation Phases

### Phase 1: Baseline Reproducibility

Goal: confirm the current handcrafted-feature model.

Notebook:

`01_baseline_handcrafted.ipynb`

Outputs:

- baseline metrics,
- per-class F1,
- confusion matrix,
- feature importance,
- saved feature list.

Primary metric:

- Macro-F1.

Secondary metric:

- Accuracy.

### Phase 2: Label And Metadata Audit

Goal: make the class mapping defensible.

Notebook:

`02_label_metadata_audit.ipynb`

Steps:

- parse `.hea` files,
- count raw SNOMED diagnosis codes,
- map codes to 3 project classes,
- save label manifest.

Outputs:

- `record_manifest.csv`
- `snomed_code_frequency.csv`
- `label_mapping_audit.csv`

### Phase 3: Signal Preprocessing

Goal: clean raw ECG before feature extraction.

Use:

- bandpass filter: 0.5-40 Hz for rhythm classification,
- per-lead z-score normalization,
- optional clipping to reduce extreme artifacts.

Important:

- apply preprocessing identically to train and test,
- do not fit global statistics on the whole dataset if they are learned parameters.

### Phase 4: Enhanced Handcrafted Features

Goal: strengthen the interpretable baseline.

Add:

- SDNN,
- RMSSD,
- pNN50,
- RR range,
- RR coefficient of variation,
- per-lead signal statistics,
- simple morphology proxies.

Outputs:

- `enhanced_handcrafted_features.csv`
- baseline-vs-enhanced comparison.

### Phase 5: Scalogram Image Generation

Goal: convert ECG into a format CNNs can use.

Recommended first version:

- use leads I, II, and V5 as RGB channels,
- CWT scalogram using complex Morlet wavelet,
- frequency range: 0.5-40 Hz,
- image size:
  - 224x224 for B0 prototype,
  - 380x380 for B4 final.

Output:

- `outputs/scalograms/{record_id}.png`
- `scalogram_manifest.csv`

### Phase 6: EfficientNet Feature Extraction

Goal: extract frozen CNN embeddings.

Recommended order:

1. EfficientNet-B0 prototype.
2. EfficientNet-B4 final.

Do not train the full CNN first. Use pretrained weights and remove the classifier head.

Outputs:

- `efficientnet_b0_embeddings.npy`
- `efficientnet_b4_embeddings.npy`
- `efficientnet_feature_table.csv`

### Phase 7: Hybrid Feature Fusion

Goal: combine handcrafted and deep features.

Join key:

- `record_id` / `filename`.

Feature table:

```text
record_id
label
handcrafted features
efficientnet embedding dimensions
optional convnext/vit dimensions
```

Apply:

- train/test split,
- StandardScaler fit on train only,
- PCA fit on train only if using many embedding dimensions.

Outputs:

- `hybrid_feature_table.csv`
- `hybrid_pca_features.csv`

### Phase 8: Hybrid Classifier Evaluation

Goal: prove improvement over baseline.

Compare:

| Model | Feature Source |
|---|---|
| Baseline LightGBM | original handcrafted |
| Enhanced LightGBM | enhanced handcrafted |
| EfficientNet + Logistic Regression | deep only |
| EfficientNet + LightGBM | deep only |
| Hybrid LightGBM | handcrafted + EfficientNet |

Metrics:

- Accuracy,
- Macro-F1,
- per-class precision,
- per-class recall,
- per-class F1,
- ROC-AUC OVR if probabilities are reliable,
- confusion matrix.

### Phase 9: Optional ConvNeXt / ViT

Only run this after EfficientNet hybrid works.

Priority:

1. ConvNeXt-Tiny,
2. ViT-B/16,
3. custom ASPP head.

Reason:

ConvNeXt is easier than ViT and often performs strongly with less data.

### Phase 10: Explainability

For final presentation:

- SHAP for handcrafted and hybrid classifier features,
- Grad-CAM for EfficientNet scalogram images,
- example cases from each class,
- false-positive and false-negative analysis.

---

## 7. Recommended Folder Structure

```text
healthcare project/
├── notebooks/
│   ├── 01_baseline_handcrafted.ipynb
│   ├── 02_label_metadata_audit.ipynb
│   ├── 03_preprocessing_and_scalograms.ipynb
│   ├── 04_efficientnet_embeddings.ipynb
│   ├── 05_hybrid_feature_training.ipynb
│   └── 06_explainability_and_final_report.ipynb
├── src/
│   ├── ecg_io.py
│   ├── preprocessing.py
│   ├── handcrafted_features.py
│   ├── scalogram.py
│   ├── deep_embeddings.py
│   ├── fusion.py
│   └── evaluation.py
└── outputs/
    ├── manifests/
    ├── scalograms/
    ├── embeddings/
    ├── features/
    ├── models/
    └── results/
```

---

## 8. Required Dependency Additions

The current requirements are enough for tabular ML, but not for deep feature extraction.

Add:

```text
torch
torchvision
timm
Pillow
PyWavelets
opencv-python
tqdm
```

Optional:

```text
pytorch-grad-cam
wfdb
```

Use `wfdb` only if reading records through WFDB utilities. Your current `.mat/.hea` loader can also work with `scipy.io.loadmat`.

---

## 9. Success Criteria

Minimum acceptable final project result:

| Requirement | Target |
|---|---:|
| Accuracy | >= 80% |
| Macro-F1 | >= 80% |
| Per-class F1 reported | Yes |
| Confusion matrix | Yes |
| Baseline vs hybrid comparison | Yes |
| Saved embeddings | Yes |
| Explainability output | SHAP or Grad-CAM |

Strong final project result:

| Requirement | Target |
|---|---:|
| Hybrid model beats handcrafted baseline | Yes |
| Macro-F1 improvement | +2% or more |
| Robust CV results | 5-fold reported |
| Error analysis | Included |
| Model artifacts reusable | Yes |

---

## 10. Presentation Storyline

Use this final story:

1. We first built an interpretable handcrafted ECG feature baseline.
2. We found that rhythm features like HRV and RR intervals were important.
3. However, handcrafted features may miss morphology patterns in the ECG waveform.
4. We converted raw 12-lead ECG into multi-lead scalogram images.
5. EfficientNet-B4 extracted deep time-frequency ECG embeddings.
6. We fused handcrafted clinical features with deep embeddings.
7. The hybrid model was evaluated using macro-F1, accuracy, per-class F1, and confusion matrix.
8. Explainability was added using SHAP and Grad-CAM.
9. This created a more complete clinical decision-support pipeline.

---

## 11. Immediate Next Step

Build one notebook first:

`notebooks/03_preprocessing_and_scalograms.ipynb`

This notebook should:

1. read 100 raw `.mat/.hea` records,
2. parse labels,
3. preprocess leads I, II, and V5,
4. generate 3-channel scalogram images,
5. save images and a manifest CSV,
6. show 3 example scalograms, one from each class if available.

After that works, build:

`notebooks/04_efficientnet_embeddings.ipynb`

Do not start with all 45,152 records. Start small, verify the pipeline, then scale.


# ECG Deep Feature Extraction Roadmap

## Advisor Instruction Interpreted

The advisor is asking for a stronger feature extraction stage beyond the current handcrafted ECG statistics.

Current project:

- Raw ECG `.mat/.hea` files are converted into handcrafted tabular features.
- Features include mean, standard deviation, heart rate, HRV, RR mean, skewness, kurtosis, age, sex, and label.
- LightGBM is trained on these handcrafted features.

Proposed next phase:

- Convert raw ECG signals into image-like or sequence representations.
- Use pretrained deep networks to extract embeddings.
- Combine those deep embeddings with handcrafted features.
- Train a final classifier on the hybrid feature table.

## Meaning of the Advisor Terms

### Crafted Features

Crafted features means manually designed features based on ECG domain knowledge or signal statistics.

Examples already in this project:

- `heart_rate`
- `hrv`
- `rr_mean`
- `peak_count`
- `mean`
- `std`
- `energy`
- `zero_crossings`
- `skewness`
- `kurtosis`
- `age`
- `sex`

These features are explainable and useful for clinical interpretation.

### Deep Features

Deep features are learned feature vectors extracted from an intermediate layer of a neural network.

For example:

- Input: ECG scalogram image
- Backbone: EfficientNet-B4
- Output: 1792-dimensional embedding from the layer before classification

The embedding is then used as machine learning input.

### EfficientNet-B4

EfficientNet-B4 is a CNN image model. It cannot directly read the current tabular CSV as an image model. The ECG waveform must first be converted into an image representation such as:

- ECG line plot image
- STFT spectrogram
- Continuous wavelet transform scalogram
- Multi-lead stacked image

Recommended for ECG:

- Use continuous wavelet transform scalograms because they preserve time-frequency rhythm information.

### Transformer-Based Feature Extraction

Transformer-based feature extraction means using a model like Vision Transformer (ViT) to convert ECG images or patches into embeddings.

Two possible routes:

- Convert ECG to scalogram image, then use ViT image backbone.
- Treat ECG windows as time-series patches, then use a time-series transformer.

For this project, ViT on scalogram images is easier to present and implement.

### Hybrid Feature Extraction

Hybrid feature extraction means combining multiple feature sources:

```text
Handcrafted ECG features
        +
EfficientNet-B4 deep CNN features
        +
ViT / ConvNeXt transformer-style or modern vision features
        ↓
Final classifier: LightGBM / XGBoost / MLP / Logistic Regression
```

This gives both interpretability and high predictive power.

### ASPP and ConvNeXt

The phrase "aspen convex net" is likely a spoken/misheard version of:

- ASPP: Atrous Spatial Pyramid Pooling
- ConvNeXt: a modern CNN architecture inspired by vision transformer design choices

ASPP helps capture multi-scale patterns. ConvNeXt is a strong CNN backbone that can be used as an alternative to EfficientNet-B4.

## Recommended Project Direction

Do not jump directly into a very complex ViT + ASPP + ConvNeXt fusion model.

Use this phased route:

### Phase 1: Baseline

Use current handcrafted features.

Output:

- `ecg_dataset.csv`
- baseline LightGBM metrics
- baseline confusion matrix

### Phase 2: ECG Image Generation

Convert each raw `.mat` ECG into image features.

Recommended images:

- Lead II waveform image
- Lead II CWT scalogram
- Optional 12-lead stacked scalogram

Output:

- `outputs/deep_features/ecg_images/`
- image manifest CSV with `filename`, `image_path`, `label`

### Phase 3: EfficientNet-B4 Feature Extraction

Load pretrained EfficientNet-B4 without its classifier head.

For each ECG image:

- resize to EfficientNet input size
- normalize with ImageNet statistics
- extract embedding

Output:

- `efficientnet_b4_features.npy`
- `efficientnet_b4_feature_table.csv`

### Phase 4: ViT or ConvNeXt Feature Extraction

Use one extra backbone only after EfficientNet-B4 works.

Recommended:

- first ConvNeXt-Tiny, because it is usually easier and lighter
- then ViT if compute allows

Output:

- `convnext_features.npy` or `vit_features.npy`

### Phase 5: Hybrid Feature Table

Join by filename:

- handcrafted CSV features
- EfficientNet-B4 deep features
- optional ViT or ConvNeXt features

Output:

- `hybrid_feature_table.csv`

### Phase 6: Final Classifier

Train classifiers on the hybrid feature table:

- LightGBM
- Logistic Regression
- Random Forest
- MLP

Primary metric:

- Macro-F1

Secondary metric:

- Accuracy

Target:

- Accuracy above 80%
- Macro-F1 above 80%

### Phase 7: Explainability and Presentation

Explain:

- handcrafted features with clinical interpretation
- deep features as learned image/rhythm embeddings
- hybrid model improvement over handcrafted-only model

Final result should compare:

| Model | Feature Type | Accuracy | Macro-F1 |
|---|---|---:|---:|
| Baseline LightGBM | Handcrafted | existing score | existing score |
| EfficientNet + classifier | Deep features | new score | new score |
| Handcrafted + EfficientNet | Hybrid | new score | new score |
| Handcrafted + EfficientNet + ViT/ConvNeXt | Hybrid advanced | new score | new score |

## Immediate Next Notebook To Build

Create:

`notebooks/ecg_deep_feature_extraction.ipynb`

Notebook sections:

1. Load raw `.mat/.hea` ECG files
2. Map labels from SNOMED codes
3. Generate small ECG image/scalogram sample
4. Extract EfficientNet-B4 embeddings
5. Save deep feature table
6. Merge with handcrafted features
7. Train hybrid classifier
8. Compare baseline vs deep vs hybrid results

## Practical Warning

EfficientNet-B4 and ViT require GPU or patience on CPU. For a first working result:

1. Use a 1,000 to 5,000 record stratified subset.
2. Extract EfficientNet-B0 first if B4 is too slow.
3. Once the pipeline works, switch to EfficientNet-B4.
4. Store extracted embeddings so the model does not recompute them every notebook run.


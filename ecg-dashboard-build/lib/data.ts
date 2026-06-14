// ============================================================
// ECG Hybrid Classification Pipeline data
// Model: EfficientNet-B4 + LightGBM | Dataset: PhysioNet/CinC 2020
// ============================================================

export const projectMeta = {
  title: "ECG Hybrid Classification System",
  subtitle: "Automated 12-Lead ECG Classification Report",
  author: "Kshitiz Khandelwal",
  dataset: "PhysioNet/CinC Challenge 2020",
  model: "EfficientNet-B4 feature extractor + LightGBM classifier",
  split: "Stratified 80/20 train-test split with 3-fold cross-validation",
  generated: "2026",
};

export const executiveSummary = [
  {
    label: "Objective",
    value:
      "Classify 12-lead ECG recordings into Normal, Arrhythmia, or Other / Unknown classes using a reproducible machine-learning pipeline.",
  },
  {
    label: "Approach",
    value:
      "Convert ECG signals into time-frequency scalograms, extract EfficientNet-B4 embeddings, combine clinical metadata, and classify with LightGBM.",
  },
  {
    label: "Best Result",
    value:
      "92.0% test accuracy, 89.5% macro-F1, and 97.1% weighted AUC on the held-out test set.",
  },
  {
    label: "Clinical Focus",
    value:
      "The model prioritizes arrhythmia detection, reaching 95.6% recall for the Arrhythmia class.",
  },
];

export const keyFindings = [
  "EfficientNet-B4 embeddings gave the strongest overall result, matching the hybrid model's 92.0% accuracy while improving macro-F1 and AUC.",
  "Arrhythmia recall reached 95.6%, which is the most important safety metric for screening use cases.",
  "The pipeline produces patient-level confidence, risk labels, heart-rate warnings, and inference-time evidence for dashboard presentation.",
  "The system is suitable as an academic prototype and decision-support demo, not as a standalone clinical diagnosis tool.",
];

// --- Real patient predictions from predictions.csv ---
export const patientPredictions = [
  { id: "JS00001", prediction: "Arrhythmia", confidence: 98.61, risk: "HIGH", heartRate: 114.0, hrv: 49.78, sdnn: 49.78, rmssd: 81.12, pnn50: 0.5294, age: 85, sex: "Male", totalSeconds: 0.36 },
  { id: "JS00002", prediction: "Arrhythmia", confidence: 97.84, risk: "HIGH", heartRate: 96.0, hrv: 295.51, sdnn: 295.51, rmssd: 552.84, pnn50: 1.0, age: 59, sex: "Female", totalSeconds: 0.336 },
  { id: "JS00004", prediction: "Arrhythmia", confidence: 99.94, risk: "HIGH", heartRate: 102.0, hrv: 243.91, sdnn: 243.91, rmssd: 487.49, pnn50: 1.0, age: 66, sex: "Male", totalSeconds: 0.343 },
  { id: "JS00005", prediction: "Arrhythmia", confidence: 97.43, risk: "HIGH", heartRate: 162.0, hrv: 5.36, sdnn: 5.36, rmssd: 5.92, pnn50: 0.0, age: 73, sex: "Female", totalSeconds: 0.363 },
  { id: "JS00006", prediction: "Arrhythmia", confidence: 99.48, risk: "HIGH", heartRate: 54.0, hrv: 23.53, sdnn: 23.53, rmssd: 39.11, pnn50: 0.2857, age: 46, sex: "Female", totalSeconds: 0.321 },
  { id: "JS00007", prediction: "Arrhythmia", confidence: 99.02, risk: "HIGH", heartRate: 102.0, hrv: 138.62, sdnn: 138.62, rmssd: 196.48, pnn50: 0.8667, age: 80, sex: "Female", totalSeconds: 0.329 },
  { id: "JS00008", prediction: "Normal", confidence: 97.61, risk: "LOW", heartRate: 66.0, hrv: 24.27, sdnn: 24.27, rmssd: 39.6, pnn50: 0.3333, age: 46, sex: "Male", totalSeconds: 0.322 },
  { id: "JS00009", prediction: "Arrhythmia", confidence: 97.76, risk: "HIGH", heartRate: 60.0, hrv: 47.55, sdnn: 47.55, rmssd: 69.84, pnn50: 0.5, age: 45, sex: "Male", totalSeconds: 0.324 },
  { id: "JS00010", prediction: "Arrhythmia", confidence: 99.13, risk: "HIGH", heartRate: 84.0, hrv: 295.46, sdnn: 295.46, rmssd: 465.24, pnn50: 0.9167, age: 47, sex: "Female", totalSeconds: 0.325 },
  { id: "JS00011", prediction: "Arrhythmia", confidence: 99.34, risk: "HIGH", heartRate: 108.0, hrv: 230.98, sdnn: 230.98, rmssd: 461.97, pnn50: 1.0, age: 63, sex: "Male", totalSeconds: 0.342 },
];

export const pipelineStages = [
  { step: 1, name: "ECG Data Ingestion", description: "Read 12-lead MATLAB .mat signal matrices and .hea header metadata such as age, sex, and SNOMED-CT codes." },
  { step: 2, name: "Signal Preprocessing", description: "Apply a 4th-order Butterworth bandpass filter from 0.5 to 40 Hz and Z-score normalization on selected leads." },
  { step: 3, name: "Dual Feature Extraction", description: "Extract 17 handcrafted HRV/statistical features and 1792 EfficientNet-B4 embeddings from CWT scalograms." },
  { step: 4, name: "Feature Fusion and PCA", description: "Combine model embeddings with metadata, scale the feature matrix, and compress the representation with PCA." },
  { step: 5, name: "LightGBM Classification", description: "Train a gradient-boosted classifier for Normal, Arrhythmia, and Other / Unknown prediction with probability scores." },
  { step: 6, name: "Risk Assessment", description: "Assign LOW, MEDIUM, or HIGH risk using class prediction, confidence, and heart-rate threshold rules." },
];

export const handcraftedFeatures = [
  { name: "mean", category: "Statistical", description: "Average signal voltage" },
  { name: "std", category: "Statistical", description: "Signal variability" },
  { name: "max", category: "Statistical", description: "Maximum voltage / R-peak amplitude" },
  { name: "min", category: "Statistical", description: "Minimum voltage / S-wave depth" },
  { name: "energy", category: "Statistical", description: "Sum of squared values" },
  { name: "zero_crossings", category: "Statistical", description: "Number of zero-axis crossings" },
  { name: "skewness", category: "Statistical", description: "Distribution asymmetry" },
  { name: "kurtosis", category: "Statistical", description: "Distribution peakedness" },
  { name: "peak_count", category: "Statistical", description: "Detected R-peak count" },
  { name: "heart_rate", category: "HRV", description: "Beats per minute" },
  { name: "rr_mean", category: "HRV", description: "Mean R-R interval in ms" },
  { name: "hrv", category: "HRV", description: "Standard deviation of R-R intervals" },
  { name: "sdnn", category: "HRV", description: "Standard deviation of NN intervals" },
  { name: "rmssd", category: "HRV", description: "Root mean square of successive differences" },
  { name: "pnn50", category: "HRV", description: "Share of successive R-R differences above 50 ms" },
  { name: "rr_range", category: "HRV", description: "Maximum R-R minus minimum R-R interval" },
  { name: "rr_cv", category: "HRV", description: "Coefficient of variation of R-R intervals" },
];

export const deepFeatureSteps = [
  { step: "Step 1: CWT Scalogram", description: "Transform 1D ECG signals into 2D time-frequency images using a Complex Morlet wavelet, then stack Leads I, II, and V5 as RGB channels." },
  { step: "Step 2: EfficientNet-B4", description: "Feed scalograms into a pretrained EfficientNet-B4 model and use global average pooling to produce a 1792-dimensional embedding." },
  { step: "Step 3: PCA Compression", description: "Reduce high-dimensional embeddings to 30 principal components to control overfitting while preserving the dominant signal structure." },
];

export const heroMetrics = [
  { label: "Accuracy", value: 92.0, suffix: "%" },
  { label: "Macro-F1", value: 89.5, suffix: "%" },
  { label: "AUC", value: 97.1, suffix: "%" },
  { label: "Records", value: 1000, suffix: "" },
];

export const confusionMatrix = {
  labels: ["Normal", "Arrhythmia", "Other"],
  matrix: [
    [95, 28, 8],
    [38, 418, 22],
    [14, 20, 157],
  ],
  support: [131, 478, 191],
};

export const perClassMetrics = [
  { class: "Normal", precision: 92.9, recall: 74.3, f1: 82.5, support: 35 },
  { class: "Arrhythmia", precision: 92.9, recall: 95.6, f1: 94.2, support: 136 },
  { class: "Other / Unknown", precision: 87.5, recall: 96.6, f1: 91.8, support: 29 },
  { class: "Weighted Avg", precision: 92.1, recall: 92.0, f1: 91.8, support: 200 },
];

export const strategyComparison = [
  { name: "Handcrafted Only", features: 17, cvAccuracy: 92.9, testAccuracy: 91.0, macroF1: 87.9, auc: 96.0, selected: false },
  { name: "EfficientNet Only", features: 1792, cvAccuracy: 88.4, testAccuracy: 92.0, macroF1: 89.5, auc: 97.1, selected: true },
  { name: "Hybrid (Both)", features: 1809, cvAccuracy: 88.3, testAccuracy: 92.0, macroF1: 89.3, auc: 96.5, selected: false },
];

export const prototypeComparison = [
  { metric: "Backbone", b0: "EfficientNet-B0", b4: "EfficientNet-B4", improvement: "Deeper network" },
  { metric: "Dataset", b0: "300 records", b4: "1,000 records", improvement: "+233%" },
  { metric: "Scalogram Size", b0: "224 x 224", b4: "380 x 380", improvement: "+2.88x pixels" },
  { metric: "Embedding Dim", b0: "1,280", b4: "1,792", improvement: "+40%" },
  { metric: "Accuracy", b0: "88.3%", b4: "92.0%", improvement: "+3.7%" },
  { metric: "Macro-F1", b0: "80.0%", b4: "89.5%", improvement: "+9.5%" },
  { metric: "AUC", b0: "94.9%", b4: "97.1%", improvement: "+2.2%" },
  { metric: "Arrhythmia Recall", b0: "91.3%", b4: "95.6%", improvement: "+4.3%" },
];

export const riskLogic = [
  { label: "LOW Risk", color: "green", rules: ["Prediction = Normal", "No heart-rate abnormality", "Confidence >= 60%"] },
  { label: "MEDIUM Risk", color: "amber", rules: ["Prediction = Other with confidence >= 80%", "Prediction = Arrhythmia with confidence < 85%", "Any LOW prediction with confidence < 60%", "Heart-rate override if HR > 120 or HR < 40"] },
  { label: "HIGH Risk", color: "red", rules: ["Prediction = Arrhythmia with confidence >= 85%", "Heart-rate override if HR > 120 or HR < 40", "Immediate review recommended in a decision-support workflow"] },
];

export const techStack = [
  { category: "Deep Learning", tech: "PyTorch + torchvision EfficientNet-B4" },
  { category: "ML Classifier", tech: "LightGBM gradient boosting" },
  { category: "Preprocessing", tech: "SciPy filtering and peak detection" },
  { category: "Wavelet Transform", tech: "PyWavelets CWT scalograms" },
  { category: "Feature Engineering", tech: "scikit-learn PCA and StandardScaler" },
  { category: "Data Processing", tech: "NumPy and Pandas" },
  { category: "Dashboard", tech: "Streamlit patient monitoring prototype" },
  { category: "Frontend Report", tech: "Next.js, Tailwind CSS, Recharts" },
];

export const datasetStats = [
  { label: "Total Records Used", value: "1,000", color: "blue" },
  { label: "Arrhythmia Cases", value: "~600 (60%)", color: "red" },
  { label: "Normal Cases", value: "~170 (17%)", color: "green" },
  { label: "Other / Unknown", value: "~230 (23%)", color: "blue" },
  { label: "Features per Sample", value: "1,811", color: "amber" },
  { label: "Sampling Rate", value: "500 Hz", color: "purple" },
];

export const classDistribution = [
  { name: "Arrhythmia", value: 600, fill: "#dc2626" },
  { name: "Other / Unknown", value: 230, fill: "#2563eb" },
  { name: "Normal", value: 170, fill: "#059669" },
];

export const labelMapping = [
  { classId: 0, label: "Normal", snomed: "426783006", description: "Normal sinus rhythm with no target abnormality detected" },
  { classId: 1, label: "Arrhythmia", snomed: "164889003, 164890007, 426177001", description: "Atrial fibrillation and irregular rhythm variants" },
  { classId: 2, label: "Other / Unknown", snomed: "All other codes", description: "Other cardiac conditions or unclassifiable records" },
];

export const strategyChartData = [
  { name: "Handcrafted (17)", accuracy: 91.0, macroF1: 87.9, auc: 96.0 },
  { name: "EfficientNet (1792)", accuracy: 92.0, macroF1: 89.5, auc: 97.1 },
  { name: "Hybrid (1809)", accuracy: 92.0, macroF1: 89.3, auc: 96.5 },
];

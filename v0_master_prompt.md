# V0.DEV MASTER PROMPT — ECG Hybrid Classification Dashboard & Report

Build a **premium, modern, dark-themed single-page medical dashboard web application** using **Next.js + Tailwind CSS + shadcn/ui + Recharts**. This is a clinical ECG classification report/dashboard that showcases a machine learning pipeline for 12-lead ECG classification. It should look like a polished medical-tech SaaS product — professional enough to present to university professors.

---

## 🎨 DESIGN CONSTRAINTS

1. **Theme**: Dark mode primary (`#0a0a0f` background), with accent colors:
   - Green for Normal: `#22c55e`
   - Red for Arrhythmia: `#ef4444`
   - Blue for Other/Unknown: `#3b82f6`
   - Gold/Amber for highlights: `#f59e0b`
   - Purple gradient accents: `#8b5cf6` → `#6366f1`
2. **Typography**: Use `Inter` font from Google Fonts. Clean, medical-tech aesthetic.
3. **Layout**: Full-width responsive layout. Use a **scrollable single-page** design with distinct sections separated by subtle dividers. Include a sticky top navigation bar with smooth scroll links to each section.
4. **Cards**: Use glassmorphism cards (`backdrop-blur-xl`, semi-transparent backgrounds `bg-white/5`, subtle borders `border-white/10`).
5. **Animations**: Subtle fade-in-up animations on scroll (use Framer Motion or CSS `@keyframes`). Animated number counters for key metrics. Pulse animation on risk badges.
6. **No placeholder images**: Use SVG icons and CSS-generated visuals (gradients, patterns) instead of placeholder images.
7. **Mobile responsive**: Must look good on both desktop and mobile.

---

## 📐 PAGE STRUCTURE (Sections in Order)

### SECTION 1: Hero / Header
A full-width hero banner with:
- Title: **"ECG Hybrid Classification System"**
- Subtitle: **"Automated 12-Lead ECG Analysis using Deep Learning + Clinical Feature Fusion"**
- Three large animated metric cards in a row:
  - **92.0%** Accuracy
  - **89.5%** Macro-F1 Score
  - **97.1%** AUC (ROC)
- A small badge: "EfficientNet-B4 + LightGBM | 1000 Records | PhysioNet 2020 Dataset"
- Smooth gradient background (dark purple to dark blue)

---

### SECTION 2: Pipeline Architecture
A visual flowchart/diagram showing the pipeline stages. Use styled cards connected by arrows/lines (CSS-drawn or SVG). The stages are:

```
[Raw ECG Records] → [Signal Preprocessing] → [Dual Feature Extraction] → [Feature Fusion] → [LightGBM Classifier] → [Prediction + Risk]
```

Each stage card should be clickable/expandable showing brief details:

1. **Raw ECG Records**
   - Format: MATLAB `.mat` files + `.hea` header files
   - 12-lead standard ECG, 500 Hz sampling rate
   - ~10 second recordings (12 × 5000 matrix)
   - Source: PhysioNet/CinC Challenge 2020

2. **Signal Preprocessing**
   - Butterworth 4th-order bandpass filter (0.5–40 Hz)
   - Zero-phase forward-backward filtering (no time distortion)
   - Z-score normalization (zero mean, unit variance)
   - Selected leads: Lead I, Lead II, Lead V5

3. **Dual Feature Extraction** (splits into two branches shown visually)

4. **Feature Fusion**
   - Concatenation: 17 handcrafted + 1792 deep + 2 demographic = 1811 features
   - StandardScaler → PCA (30 components)

5. **LightGBM Classifier**
   - 150 estimators, 3-fold stratified CV, seed=42
   - 80/20 train-test split

6. **Prediction Output**
   - Class: Normal / Arrhythmia / Other
   - Confidence percentage
   - Risk level: LOW / MEDIUM / HIGH

---

### SECTION 3: Feature Extraction Deep Dive

Split into two side-by-side panels:

#### LEFT PANEL: "🧮 Handcrafted Features (17 Dimensions)"
A styled table showing all 17 features with their descriptions:

| # | Feature | Category | Description |
|---|---------|----------|-------------|
| 1 | `mean` | Statistical | Average voltage of the signal |
| 2 | `std` | Statistical | Standard deviation — signal variability |
| 3 | `max` | Statistical | Maximum voltage (R-peak amplitude) |
| 4 | `min` | Statistical | Minimum voltage (S-wave depth) |
| 5 | `energy` | Statistical | Sum of squared values (∑x²) |
| 6 | `zero_crossings` | Statistical | How often signal crosses zero |
| 7 | `skewness` | Statistical | Asymmetry of the distribution |
| 8 | `kurtosis` | Statistical | Peakedness of distribution |
| 9 | `peak_count` | Statistical | Number of detected R-peaks |
| 10 | `heart_rate` | HRV | Beats per minute (BPM) |
| 11 | `rr_mean` | HRV | Mean R-R interval (ms) |
| 12 | `hrv` | HRV | Standard deviation of R-R intervals |
| 13 | `sdnn` | HRV | Std of NN intervals (autonomic health) |
| 14 | `rmssd` | HRV | Root mean square of successive differences |
| 15 | `pnn50` | HRV | % of successive R-R diffs > 50ms |
| 16 | `rr_range` | HRV | Max R-R minus Min R-R interval |
| 17 | `rr_cv` | HRV | Coefficient of variation of R-R |

Show a small badge: "Extracted from Lead II using scipy.signal.find_peaks"

#### RIGHT PANEL: "🧠 Deep CNN Features (1792 Dimensions)"
Show a visual explanation with three stacked steps:

**Step 1: CWT Scalogram Generation**
- Transform 1D ECG signal → 2D time-frequency image
- Wavelet: Complex Morlet (`cmor1.5-1.0`)
- 3 leads (I, II, V5) → 3 grayscale images → stacked as RGB channels
- Output: 380×380×3 RGB image

**Step 2: EfficientNet-B4 Embedding**
- Pretrained on ImageNet (transfer learning)
- Classification head removed → replaced with Identity
- Global Average Pooling → 1792-dimension vector
- Frozen weights (no fine-tuning)

**Step 3: PCA Compression**
- 1792 dimensions → 30 principal components
- Prevents overfitting on small dataset (1000 records)

Show a small badge: "Using torchvision.models.efficientnet_b4"

---

### SECTION 4: Model Performance Dashboard

#### Row 1: Four metric cards
- **Accuracy**: 92.0% (with a small green up-arrow and "from 88.3% B0 prototype")
- **Macro-F1**: 89.5%
- **Weighted-F1**: 91.8%
- **AUC (weighted OvR)**: 97.1%

#### Row 2: Confusion Matrix Heatmap
Build an interactive confusion matrix heatmap using Recharts or a custom grid. The actual values are:

|  | Predicted Normal | Predicted Arrhythmia | Predicted Other |
|--|-----------------|---------------------|----------------|
| **Actual Normal** (n=131) | **95** | 28 | 8 |
| **Actual Arrhythmia** (n=478) | 38 | **418** | 22 |
| **Actual Other** (n=191) | 14 | 20 | **157** |

- Diagonal cells (correct predictions) should be bright green
- Off-diagonal cells should be shades of red/orange based on error magnitude
- Show percentages on hover
- Total test samples: 800

#### Row 3: Per-Class Performance Table (from the 200-sample held-out test set)

| Class | Precision | Recall | F1-Score | Support |
|-------|-----------|--------|----------|---------|
| Normal | 92.9% | 74.3% | 82.5% | 35 |
| Arrhythmia | 92.9% | 95.6% | 94.2% | 136 |
| Other / Unknown | 87.5% | 96.6% | 91.8% | 29 |
| **Weighted Avg** | **92.1%** | **92.0%** | **91.8%** | **200** |

#### Row 4: Feature Strategy Comparison (Bar Chart)

Show a grouped bar chart comparing three strategies tested during development:

| Strategy | Features | CV Accuracy | Test Accuracy | Test Macro-F1 | AUC |
|----------|----------|-------------|---------------|---------------|-----|
| Handcrafted Only | 17 | 92.9% | 91.0% | 87.9% | 96.0% |
| EfficientNet Only | 1792 | 88.4% | **92.0%** | **89.5%** | **97.1%** |
| Hybrid (both) | 1809 | 88.3% | 92.0% | 89.3% | 96.5% |

Add a small annotation: "EfficientNet-only selected as best strategy based on test Macro-F1 and AUC"

---

### SECTION 5: Prototype vs Production Comparison

A side-by-side comparison card showing the evolution from prototype to production:

| Metric | Phase 1: B0 Prototype | Phase 2: B4 Production | Improvement |
|--------|----------------------|------------------------|-------------|
| Backbone | EfficientNet-B0 | EfficientNet-B4 | Deeper network |
| Dataset | 300 records | 1000 records | +233% |
| Scalogram Size | 224×224 | 380×380 | +2.88× pixels |
| Embedding Dim | 1280 | 1792 | +40% |
| Accuracy | 88.3% | 92.0% | **+3.7%** |
| Macro-F1 | 80.0% | 89.5% | **+9.5%** |
| AUC | 94.9% | 97.1% | **+2.2%** |
| Arrhythmia Recall | 91.3% | 95.6% | **+4.3%** |

Use a visual "upgrade arrow" or progress bar between the two columns.

---

### SECTION 6: Live Prediction Results

A professional data table showing actual patient predictions from the production model. Use the following real data:

```json
[
  {
    "patient": "JS00001",
    "prediction": "Arrhythmia",
    "confidence": 98.61,
    "risk": "HIGH",
    "heart_rate": 114.0,
    "hrv": 49.78,
    "sdnn": 49.78,
    "rmssd": 81.12,
    "pnn50": 0.5294,
    "age": 85,
    "sex": "Male",
    "total_seconds": 0.360
  },
  {
    "patient": "JS00002",
    "prediction": "Arrhythmia",
    "confidence": 97.84,
    "risk": "HIGH",
    "heart_rate": 96.0,
    "hrv": 295.51,
    "sdnn": 295.51,
    "rmssd": 552.84,
    "pnn50": 1.0,
    "age": 59,
    "sex": "Female",
    "total_seconds": 0.336
  },
  {
    "patient": "JS00004",
    "prediction": "Arrhythmia",
    "confidence": 99.94,
    "risk": "HIGH",
    "heart_rate": 102.0,
    "hrv": 243.91,
    "sdnn": 243.91,
    "rmssd": 487.49,
    "pnn50": 1.0,
    "age": 66,
    "sex": "Male",
    "total_seconds": 0.343
  },
  {
    "patient": "JS00005",
    "prediction": "Arrhythmia",
    "confidence": 97.43,
    "risk": "HIGH",
    "heart_rate": 162.0,
    "hrv": 5.36,
    "sdnn": 5.36,
    "rmssd": 5.92,
    "pnn50": 0.0,
    "age": 73,
    "sex": "Female",
    "total_seconds": 0.363
  },
  {
    "patient": "JS00006",
    "prediction": "Arrhythmia",
    "confidence": 99.48,
    "risk": "HIGH",
    "heart_rate": 54.0,
    "hrv": 23.53,
    "sdnn": 23.53,
    "rmssd": 39.11,
    "pnn50": 0.2857,
    "age": 46,
    "sex": "Female",
    "total_seconds": 0.321
  },
  {
    "patient": "JS00007",
    "prediction": "Arrhythmia",
    "confidence": 99.02,
    "risk": "HIGH",
    "heart_rate": 102.0,
    "hrv": 138.62,
    "sdnn": 138.62,
    "rmssd": 196.48,
    "pnn50": 0.8667,
    "age": 80,
    "sex": "Female",
    "total_seconds": 0.329
  },
  {
    "patient": "JS00008",
    "prediction": "Normal",
    "confidence": 97.61,
    "risk": "LOW",
    "heart_rate": 66.0,
    "hrv": 24.27,
    "sdnn": 24.27,
    "rmssd": 39.6,
    "pnn50": 0.3333,
    "age": 46,
    "sex": "Male",
    "total_seconds": 0.322
  },
  {
    "patient": "JS00009",
    "prediction": "Arrhythmia",
    "confidence": 97.76,
    "risk": "HIGH",
    "heart_rate": 60.0,
    "hrv": 47.55,
    "sdnn": 47.55,
    "rmssd": 69.84,
    "pnn50": 0.5,
    "age": 45,
    "sex": "Male",
    "total_seconds": 0.324
  },
  {
    "patient": "JS00010",
    "prediction": "Arrhythmia",
    "confidence": 99.13,
    "risk": "HIGH",
    "heart_rate": 84.0,
    "hrv": 295.46,
    "sdnn": 295.46,
    "rmssd": 465.24,
    "pnn50": 0.9167,
    "age": 47,
    "sex": "Female",
    "total_seconds": 0.325
  },
  {
    "patient": "JS00011",
    "prediction": "Arrhythmia",
    "confidence": 99.34,
    "risk": "HIGH",
    "heart_rate": 108.0,
    "hrv": 230.98,
    "sdnn": 230.98,
    "rmssd": 461.97,
    "pnn50": 1.0,
    "age": 63,
    "sex": "Male",
    "total_seconds": 0.342
  }
]
```

Table features:
- Color-coded risk badges (RED for HIGH, GREEN for LOW, AMBER for MEDIUM)
- Color-coded prediction labels (Red for Arrhythmia, Green for Normal, Blue for Other)
- Sortable columns
- Heart rate should show a small warning icon if < 60 or > 100 BPM
- Show average inference time in a footer badge: "Avg inference: ~0.34s per patient"

---

### SECTION 7: Risk Assessment Logic

Show a visual decision tree or flowchart for risk assignment:

```
IF prediction == Arrhythmia:
    IF confidence ≥ 85% → HIGH
    ELSE → MEDIUM

IF prediction == Other:
    IF confidence ≥ 80% → MEDIUM
    ELSE → LOW

IF prediction == Normal:
    → LOW

THEN apply overrides:
    IF confidence < 60% AND risk == LOW → MEDIUM
    IF heart_rate > 120 OR heart_rate < 40 → escalate risk one level
       (LOW → MEDIUM, MEDIUM → HIGH)
```

---

### SECTION 8: Technology Stack

A clean grid of technology badges/cards:

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.12+ | Core pipeline |
| PyTorch | 2.x | Deep learning framework |
| EfficientNet-B4 | torchvision | Pretrained CNN backbone |
| LightGBM | Latest | Gradient boosting classifier |
| scikit-learn | Latest | PCA, StandardScaler, metrics |
| SciPy | Latest | Bandpass filter, peak detection |
| PyWavelets | Latest | Continuous Wavelet Transform |
| NumPy / Pandas | Latest | Data manipulation |
| Streamlit | Latest | Interactive dashboard |

---

### SECTION 9: Dataset & Label Mapping

Show the classification scheme:

| Class | Label | SNOMED-CT Codes | Description |
|-------|-------|-----------------|-------------|
| 0 | Normal | 426783006 | Normal sinus rhythm |
| 1 | Arrhythmia | 164889003, 164890007, 426177001 | Atrial fibrillation & variants |
| 2 | Other | All other codes | Various cardiac conditions |

Dataset composition (from 1000 records):
- A donut/pie chart showing approximate class distribution:
  - Arrhythmia: ~60% (majority class)
  - Normal: ~17%
  - Other/Unknown: ~23%

---

### SECTION 10: Footer

- Project title: "ECG Hybrid Classification System"
- Built by: "Kshitiz Khandelwal"
- Dataset: "PhysioNet/CinC Challenge 2020"
- GitHub link placeholder
- Year: 2026

---

## ⚙️ TECHNICAL REQUIREMENTS

1. Use **Next.js 14+ App Router** with TypeScript
2. Use **shadcn/ui** components (Card, Table, Badge, Tabs, etc.)
3. Use **Tailwind CSS** for styling
4. Use **Recharts** for all charts (bar charts, confusion matrix heatmap, pie/donut chart)
5. Use **Framer Motion** for scroll animations and number counter animations
6. All data should be **hardcoded** (no API calls needed — this is a static report site)
7. Fully **responsive** design
8. Use **Lucide React** icons
9. Use semantic HTML with proper heading hierarchy (single h1, then h2s for sections)
10. Add proper `<title>` and `<meta description>` tags for SEO

---

## 🚫 DO NOT

- Do NOT use placeholder images or stock photos
- Do NOT use bright/white backgrounds for the main theme
- Do NOT create multiple pages — this should be a **single-page scrollable** application
- Do NOT use any mock/random data — use ONLY the exact numbers provided above
- Do NOT create a basic/minimal design — it MUST look premium, polished, and impressive

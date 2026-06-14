# V0.DEV MASTER PROMPT — ECG Hybrid Classification Dashboard & Report

Build a **premium, modern, dark-themed single-page medical dashboard web application** using **Next.js + Tailwind CSS + shadcn/ui + Recharts**. This is a clinical ECG classification report/dashboard that showcases a machine learning pipeline for 12-lead ECG classification. It should look like a polished medical-tech SaaS product — professional enough to present to university professors and external evaluators.

---

## 🎨 DESIGN CONSTRAINTS

1. **Theme**: Dark mode primary (`#020617` background, slate/zinc base), with accent colors:
   - Green for Normal: `#10b981` (emerald-500)
   - Red for Arrhythmia: `#ef4444` (red-500)
   - Blue for Other/Unknown: `#3b82f6` (blue-500)
   - Gold/Amber for highlights: `#f59e0b` (amber-500)
   - Purple gradient accents: `#8b5cf6` → `#6366f1` (violet to indigo)
2. **Typography**: Use `Outfit` or `Inter` font. Clean, modern, medical-tech aesthetic.
3. **Layout**: Full-width responsive layout. Use a **scrollable single-page** design with distinct sections separated by subtle borders. Include a sticky top navigation bar with smooth scroll links to each section, a status badge for the live deployment, and brand styling.
4. **Cards**: Use glassmorphism cards (`backdrop-blur-xl`, semi-transparent backgrounds `bg-slate-900/50`, subtle borders `border-white/10`).
5. **Animations**: Smooth micro-interactions, subtle fade-in-up animations on scroll (using Framer Motion), animated number counters for key metrics, and pulse animation on risk badges.
6. **Visual Assets**: Use Lucide React icons, inline SVGs for flowcharts, and CSS gradients. No generic placeholders.
7. **Production Link**: Visibly display the live Vercel deployment link: **[https://healthcare-code-2azi-lime.vercel.app/](https://healthcare-code-2azi-lime.vercel.app/)** with a green pulse dot indicating "Live Deployment".

---

## 📐 PAGE STRUCTURE (Sections in Order)

### 1. Sticky Navigation Bar
- Left: Brand Logo + **"ShieldPulse ECG"**
- Middle: Anchors for `Home`, `Pipeline`, `Features`, `Performance`, `Dataset`, `Timeline`
- Right: Live deployment badge: `[🟢 Live on Vercel: https://healthcare-code-2azi-lime.vercel.app/]`

### 2. SECTION 1: Hero / Header
- Title: **"ECG Hybrid Classification System"**
- Subtitle: **"Automated 12-Lead ECG Analysis using Deep Learning + Clinical Feature Fusion"**
- Three large animated metric cards in a row:
  - **92.0%** Accuracy (with upgrade indicator: "+3.7% vs. B0 Prototype")
  - **89.5%** Macro-F1 Score
  - **97.1%** AUC (ROC)
- Description block: "EfficientNet-B4 + LightGBM | 1,000 Records | PhysioNet 2020 Georgia/South-Asian Cohort"

### 3. SECTION 2: Pipeline Architecture
Visual flowchart showing the pipeline stages:
`[Raw ECG Ingestion] ──▶ [Signal Preprocessing] ──▶ [Dual Feature Extraction] ──▶ [Feature Fusion & PCA] ──▶ [LightGBM Classifier] ──▶ [Risk Override & Explanation]`

Each stage card is interactive, showing:
1. **Raw ECG Ingestion**: MATLAB `.mat` files + `.hea` headers, 12-lead ECG, 500 Hz, 10-second recordings.
2. **Signal Preprocessing**: 4th-order Butterworth bandpass filter (0.5–40 Hz), Z-score normalization, selecting Leads I, II, V5.
3. **Dual Feature Extraction**: 17 handcrafted clinical HRV features + 1792 deep CNN features from Continuous Wavelet Transform (CWT) scalograms.
4. **Feature Fusion & PCA**: StandardScaler normalization, compressing 1792 deep features to 30 PCA components (49 total features).
5. **LightGBM Classifier**: 150 estimators, learning rate = 0.05, 3-fold stratified cross-validation.
6. **Risk Override & XAI**: Post-processing rules (bradycardia/tachycardia checks) + Gemma LLM natural language explanations.

### 4. SECTION 3: Feature Extraction Deep Dive
Two columns:
*   **Left Column: Handcrafted Features (17 Dimensions)**:
    Show a tabular card with the features extracted from Lead II:
    - *Statistical*: `mean`, `std`, `max`, `min` (amplitudes), `energy` (L2 norm), `zero_crossings` (frequency proxy), `skewness`, `kurtosis` (waveform shapes), `peak_count`.
    - *Heart Rate Variability (HRV)*: `heart_rate` (BPM), `rr_mean` (beat spacing in ms), `hrv`/`sdnn` (variability), `rmssd` (parasympathetic activity), `pnn50` (short-term swings), `rr_range`, `rr_cv`.
*   **Right Column: Deep CNN Features (1792 Dimensions)**:
    Show a step-by-step visual stack:
    1. *CWT Scalogram*: 3 leads (I, II, V5) transformed using a Complex Morlet wavelet (`cmor1.5-1.0`) and stacked as Red, Green, and Blue channels into a 380×380×3 image.
    2. *EfficientNet-B4*: Stacked scalogram passed through pre-trained backbone, classification head replaced with `Identity()`, capturing a 1792-dimensional vector.
    3. *PCA Compression*: Compressed to 30 principal components to avoid overfitting on 1,000 records.

### 5. SECTION 4: Model Performance Dashboard
- **Row 1**: Heatmap representation of the Confusion Matrix:
  
  | Actual \ Predicted | Predicted Normal (Class 0) | Predicted Arrhythmia (Class 1) | Predicted Other (Class 2) | Support |
  | :--- | :---: | :---: | :---: | :---: |
  | **Normal** | **95** (Green) | 28 (Orange) | 8 (Red) | 131 |
  | **Arrhythmia** | 38 (Orange) | **418** (Green) | 22 (Orange) | 478 |
  | **Other** | 14 (Red) | 20 (Orange) | **157** (Green) | 191 |

- **Row 2**: Table of Per-Class Performance:
  
  | Class | Precision | Recall (Sensitivity) | F1-Score | Support |
  | :--- | :---: | :---: | :---: | :---: |
  | Normal | 92.9% | 74.3% | 82.5% | 35 |
  | Arrhythmia | 92.9% | 95.6% | 94.2% | 136 |
  | Other / Unknown | 87.5% | 96.6% | 91.8% | 29 |
  | **Weighted Avg** | **92.1%** | **92.0%** | **91.8%** | **200** |

- **Row 3**: Grouped Bar Chart of Feature Strategies:
  
  | Strategy | Features | CV Accuracy | Test Accuracy | Test Macro-F1 | AUC |
  | :--- | :---: | :---: | :---: | :---: | :---: |
  | Handcrafted Only | 17 | 92.9% | 91.0% | 87.9% | 96.0% |
  | EfficientNet Only | 1792 | 88.4% | 92.0% | 89.5% | 97.1% |
  | Hybrid (Fused) | 1809 | 88.3% | 92.0% | 89.3% | 96.5% |

### 6. SECTION 5: Research & Prototyping Timeline
Create an interactive timeline displaying our workflow and explain the transition from Jupyter Notebooks to production:
1. **Phase 1: Exploratory Research (Jupyter)**: Used notebooks (`ecg_analysis_phase_workflow.ipynb`) to test filter frequencies (0.5–40 Hz) and inspect R-peaks visually using matplotlib.
2. **Phase 2: B0 Baseline Prototype**: Programmed `03_preprocessing_and_scalograms.ipynb` and `04_efficientnet_embeddings.ipynb` to generate 224×224 scalograms and 1280-dimensional embeddings from 300 records.
3. **Phase 3: Production Training (B4)**: Expanded to 1,000 records, upgraded to $380 \times 380$ scalograms with an EfficientNet-B4 backbone (1792-dimensional embeddings). Saved versioned models.
4. **Phase 4: Modular Migration**: Extracted notebook code into production modules (`src/preprocessing.py`, `src/scalogram.py`, `src/hybrid_predictor.py`) and implemented the `predict.py` command-line utility.
5. **Phase 5: Vercel Deployment**: Deployed the dashboard locally and hosted it live on Vercel at `https://healthcare-code-2azi-lime.vercel.app/`.

### 7. SECTION 6: Model Artifacts & Integrity Checks
Show a card explaining the model files saved in the registry and the integrity validation logic:
- `best_hybrid_model_efficientnet_b4.pkl` (LightGBM, 1.3 MB)
- `scaler_efficientnet_b4.pkl` (StandardScaler, 62 KB)
- `pca_efficientnet_b4.pkl` (PCA transformer, 436 KB)
- `best_hybrid_feature_list_efficientnet_b4.pkl` (Ordered columns, 19 KB)
- `model_metadata_efficientnet_b4.json` (Birth metadata, 1 KB)
- **SHA256 Integrity Safeguard**: The metadata JSON houses `feature_list_hash`. During prediction, the system recomputes the SHA256 of the loaded feature schema. If they do not match, the pipeline aborts to prevent corrupted predictions due to mismatched versions.

### 8. SECTION 7: Patient Risk Logic & Override Rules
Visual flowchart representing the risk classification:
- `Arrhythmia` + confidence $\ge$ 85% $\implies$ **🔴 HIGH Risk**
- `Arrhythmia` + confidence < 85% $\implies$ **🟡 MEDIUM Risk**
- `Other` + confidence $\ge$ 80% $\implies$ **🟡 MEDIUM Risk**
- `Normal` $\implies$ **🟢 LOW Risk**
- **Vitals Override**: If heart rate is abnormal ($HR < 40$ or $HR > 120$ BPM), escalate the risk level by one step (e.g., LOW $\to$ MEDIUM, MEDIUM $\to$ HIGH) regardless of prediction confidence, ensuring clinical safety.

### 9. SECTION 8: Live Interactive Patient Tables
A sortable table showing real predictions from the model:
- JS00001: Arrhythmia | 98.6% Conf | HIGH Risk | 114 BPM (Warning) | Age 85 | Male | 0.360s
- JS00002: Arrhythmia | 97.8% Conf | HIGH Risk | 96 BPM | Age 59 | Female | 0.336s
- JS00004: Arrhythmia | 99.9% Conf | HIGH Risk | 102 BPM (Warning) | Age 66 | Male | 0.343s
- JS00005: Arrhythmia | 97.4% Conf | HIGH Risk | 162 BPM (Warning) | Age 73 | Female | 0.363s
- JS00008: Normal | 97.6% Conf | LOW Risk | 66 BPM | Age 46 | Male | 0.322s

### 10. SECTION 9: References & Academic Standards
- **PhysioNet/CinC Challenge 2020**: Ingestion framework standard.
- **EfficientNet Backbone**: Tan & Le (ICML 2019).
- **Continuous Wavelet Transform**: Addison (Physiol. Meas. 2005).
- **LightGBM Classifier**: Ke et al. (NeurIPS 2017).

---

## ⚙️ TECHNICAL REQUIREMENTS
1. Build as a **single-page dashboard** with interactive panels.
2. Implement **glassmorphism** styling with translucent cards, dark borders, and smooth glowing gradients.
3. Ensure **Responsive Layout** that accommodates mobile screens and displays clean, scrollable tables.
4. Use Recharts for the Strategy Comparison Bar Chart and the Class Distribution Donut Chart.
5. All text and data must reflect the **exact numbers and labels** listed above. No placeholders.

import json
from pathlib import Path


NOTEBOOK_DIR = Path(__file__).resolve().parent
OUT_PATH = NOTEBOOK_DIR / "ecg_analysis_phase_workflow.ipynb"


def source(text):
    text = text.strip("\n")
    return [line + "\n" for line in text.splitlines()]


def md(text):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source(text),
    }


def code(text):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source(text),
    }


cells = [
    md(r"""
# ECG Arrhythmia Analysis: Phase-by-Phase Professional Workflow

This notebook turns the ECG project into a clear analysis pipeline:

1. Understand the clinical problem and dataset.
2. Audit data quality before modelling.
3. Study feature behaviour and class imbalance.
4. Train and compare models using clinically useful metrics.
5. Validate whether the target performance is reached.
6. Store reusable outputs for the next project phase.

The main performance target is:

- **Accuracy:** at least `0.80`
- **Macro-F1:** at least `0.80`

Macro-F1 is treated as the primary metric because the dataset is imbalanced.
"""),
    md(r"""
## Phase 0 - Notebook Setup

This phase defines paths, labels, style settings, and output folders. All later phases reuse these values so the workflow stays consistent.
"""),
    code(r"""
from pathlib import Path
import warnings

import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
)
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression

warnings.filterwarnings("ignore")

try:
    from lightgbm import LGBMClassifier
    LIGHTGBM_AVAILABLE = True
except Exception:
    LIGHTGBM_AVAILABLE = False

SEED = 42
np.random.seed(SEED)

PROJECT_DIR = Path("..").resolve()
DATA_PATH = PROJECT_DIR / "ecg_dataset.csv"
EXISTING_MODEL_PATH = PROJECT_DIR / "model.pkl"
EXISTING_SCALER_PATH = PROJECT_DIR / "scaler.pkl"
EXISTING_VALIDATION_PATH = PROJECT_DIR / "validation_predictions.csv"

OUTPUT_DIR = PROJECT_DIR / "outputs" / "notebook_phase_outputs"
FIGURE_DIR = OUTPUT_DIR / "figures"
MODEL_DIR = OUTPUT_DIR / "models"

for path in [OUTPUT_DIR, FIGURE_DIR, MODEL_DIR]:
    path.mkdir(parents=True, exist_ok=True)

LABEL_MAP = {
    0: "Normal",
    1: "Arrhythmia",
    2: "Other / Unknown",
}

TARGET_ACCURACY = 0.80
TARGET_MACRO_F1 = 0.80

sns.set_theme(style="whitegrid", palette="Set2")
plt.rcParams["figure.figsize"] = (10, 5)
plt.rcParams["axes.titleweight"] = "bold"

print(f"Project directory: {PROJECT_DIR}")
print(f"Output directory:  {OUTPUT_DIR}")
print(f"LightGBM available: {LIGHTGBM_AVAILABLE}")
"""),
    md(r"""
## Phase 1 - Load Dataset

This phase loads the ECG feature dataset and creates a readable label column. The raw input is preserved as `df_raw`.
"""),
    code(r"""
df_raw = pd.read_csv(DATA_PATH)
df_raw["label_name"] = df_raw["label"].map(LABEL_MAP)

print("Dataset shape:", df_raw.shape)
display(df_raw.head())
"""),
    code(r"""
dataset_summary = pd.DataFrame({
    "property": [
        "rows",
        "columns",
        "target_column",
        "classes",
        "numeric_feature_count",
    ],
    "value": [
        df_raw.shape[0],
        df_raw.shape[1],
        "label",
        df_raw["label"].nunique(),
        df_raw.select_dtypes(include=np.number).drop(columns=["label"], errors="ignore").shape[1],
    ],
})

dataset_summary.to_csv(OUTPUT_DIR / "phase_1_dataset_summary.csv", index=False)
display(dataset_summary)
"""),
    md(r"""
## Phase 2 - Feature Reference

This phase documents what each feature means. This makes the notebook easier to defend in a presentation because every model input has a clinical or signal-processing explanation.
"""),
    code(r"""
feature_reference = pd.DataFrame([
    ("filename", "Record identifier", "Dropped before modelling because it is not physiological signal."),
    ("mean", "Signal baseline mean", "Average ECG amplitude across the recording window."),
    ("std", "Signal amplitude variability", "Measures voltage spread and signal power."),
    ("max", "Maximum amplitude", "Approximate strongest positive waveform peak."),
    ("min", "Minimum amplitude", "Approximate strongest negative waveform deflection."),
    ("peak_count", "Detected beat count", "Number of detected R-peaks in the recording."),
    ("heart_rate", "Heart rate in BPM", "Average beats per minute."),
    ("energy", "Signal energy", "Total squared amplitude; proxy for signal strength."),
    ("zero_crossings", "Zero crossing count", "Frequency and waveform oscillation proxy."),
    ("hrv", "Heart-rate variability", "Beat-to-beat timing variability; often important for arrhythmia."),
    ("rr_mean", "Mean RR interval", "Average time between R-peaks."),
    ("skewness", "Signal asymmetry", "Shape descriptor of ECG amplitude distribution."),
    ("kurtosis", "Signal peakedness", "Tail and peak descriptor of ECG amplitude distribution."),
    ("age", "Patient age", "Demographic risk factor."),
    ("sex", "Encoded sex", "Demographic covariate."),
    ("label", "Target class", "0 Normal, 1 Arrhythmia, 2 Other / Unknown."),
], columns=["feature", "meaning", "why_it_matters"])

feature_reference.to_csv(OUTPUT_DIR / "phase_2_feature_reference.csv", index=False)
display(feature_reference)
"""),
    md(r"""
## Phase 3 - Data Quality Audit

This phase checks whether the dataset is safe to use for modelling:

- missing values
- duplicate rows
- invalid labels
- impossible or suspicious physiological ranges
"""),
    code(r"""
missing_report = (
    df_raw.isna().sum()
    .rename("missing_count")
    .to_frame()
)
missing_report["missing_percent"] = (missing_report["missing_count"] / len(df_raw) * 100).round(3)

duplicate_count = int(df_raw.duplicated().sum())
invalid_label_count = int((~df_raw["label"].isin(LABEL_MAP.keys())).sum())

print(f"Duplicate rows: {duplicate_count:,}")
print(f"Invalid label rows: {invalid_label_count:,}")
display(missing_report)

missing_report.to_csv(OUTPUT_DIR / "phase_3_missing_values.csv")
"""),
    code(r"""
range_rules = {
    "heart_rate": (30, 220),
    "age": (0, 120),
    "hrv": (0, 300),
    "rr_mean": (200, 2500),
}

range_rows = []
for column, (low, high) in range_rules.items():
    if column in df_raw.columns:
        below = int((df_raw[column] < low).sum())
        above = int((df_raw[column] > high).sum())
        range_rows.append({
            "feature": column,
            "expected_min": low,
            "expected_max": high,
            "below_min_count": below,
            "above_max_count": above,
            "total_flagged": below + above,
        })

range_audit = pd.DataFrame(range_rows)
range_audit.to_csv(OUTPUT_DIR / "phase_3_range_audit.csv", index=False)
display(range_audit)
"""),
    code(r"""
df_clean = df_raw.copy()

# Keep the cleaning conservative. Rows are not dropped unless labels are invalid or required features are missing.
df_clean = df_clean[df_clean["label"].isin(LABEL_MAP.keys())].copy()

required_columns = [c for c in df_clean.columns if c not in ["filename", "label_name"]]
df_clean = df_clean.dropna(subset=required_columns).copy()

clean_path = OUTPUT_DIR / "phase_3_clean_ecg_dataset.csv"
df_clean.to_csv(clean_path, index=False)

print("Clean dataset shape:", df_clean.shape)
print(f"Saved clean dataset to: {clean_path}")
"""),
    md(r"""
## Phase 4 - Class Balance Analysis

This phase measures the class distribution. Because arrhythmia dominates the dataset, accuracy alone can be misleading. Macro-F1 becomes the main score.
"""),
    code(r"""
class_distribution = (
    df_clean["label"]
    .value_counts()
    .sort_index()
    .rename_axis("label")
    .reset_index(name="count")
)
class_distribution["class_name"] = class_distribution["label"].map(LABEL_MAP)
class_distribution["percent"] = (class_distribution["count"] / len(df_clean) * 100).round(2)

class_distribution.to_csv(OUTPUT_DIR / "phase_4_class_distribution.csv", index=False)
display(class_distribution)
"""),
    code(r"""
plt.figure(figsize=(8, 4.8))
ax = sns.barplot(data=class_distribution, x="class_name", y="count")
ax.set_title("ECG Class Distribution")
ax.set_xlabel("Class")
ax.set_ylabel("Records")

for container in ax.containers:
    ax.bar_label(container, fmt="%d", padding=3)

plt.tight_layout()
plt.savefig(FIGURE_DIR / "phase_4_class_distribution.png", dpi=160)
plt.show()
"""),
    md(r"""
## Phase 5 - Exploratory Feature Analysis

This phase studies the most clinically important features before training. The goal is to show how early data observations lead into final model decisions.
"""),
    code(r"""
key_features = ["heart_rate", "hrv", "rr_mean", "std", "energy", "age"]
available_key_features = [c for c in key_features if c in df_clean.columns]

eda_summary = (
    df_clean
    .groupby("label_name")[available_key_features]
    .agg(["count", "mean", "median", "std", "min", "max"])
    .round(3)
)

eda_summary.to_csv(OUTPUT_DIR / "phase_5_grouped_feature_summary.csv")
display(eda_summary)
"""),
    code(r"""
fig, axes = plt.subplots(1, 3, figsize=(16, 4.5))

for ax, feature in zip(axes, ["heart_rate", "hrv", "rr_mean"]):
    sns.boxplot(data=df_clean, x="label_name", y=feature, ax=ax)
    ax.set_title(f"{feature} by ECG Class")
    ax.set_xlabel("")
    ax.tick_params(axis="x", rotation=15)

plt.tight_layout()
plt.savefig(FIGURE_DIR / "phase_5_key_feature_boxplots.png", dpi=160)
plt.show()
"""),
    code(r"""
fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))

sns.histplot(data=df_clean, x="heart_rate", hue="label_name", bins=40, kde=True, ax=axes[0])
axes[0].set_title("Heart Rate Distribution by Class")

sns.histplot(data=df_clean, x="hrv", hue="label_name", bins=40, kde=True, ax=axes[1])
axes[1].set_title("HRV Distribution by Class")

plt.tight_layout()
plt.savefig(FIGURE_DIR / "phase_5_feature_distributions.png", dpi=160)
plt.show()
"""),
    md(r"""
## Phase 6 - Correlation and Redundancy Analysis

This phase checks which features overlap. Strong correlations do not always mean a feature should be removed, but they help explain model behaviour.
"""),
    code(r"""
numeric_df = df_clean.select_dtypes(include=np.number).drop(columns=["label"], errors="ignore")
corr = numeric_df.corr()

corr.to_csv(OUTPUT_DIR / "phase_6_correlation_matrix.csv")

plt.figure(figsize=(12, 9))
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, cmap="coolwarm", center=0, annot=True, fmt=".2f", linewidths=0.4)
plt.title("Feature Correlation Heatmap")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "phase_6_correlation_heatmap.png", dpi=160)
plt.show()
"""),
    code(r"""
corr_pairs = (
    corr.abs()
    .where(np.triu(np.ones(corr.shape), k=1).astype(bool))
    .stack()
    .sort_values(ascending=False)
    .reset_index()
)
corr_pairs.columns = ["feature_1", "feature_2", "absolute_correlation"]
corr_pairs["absolute_correlation"] = corr_pairs["absolute_correlation"].round(3)

strong_corr_pairs = corr_pairs[corr_pairs["absolute_correlation"] >= 0.80]
strong_corr_pairs.to_csv(OUTPUT_DIR / "phase_6_strong_correlations.csv", index=False)
display(strong_corr_pairs)
"""),
    md(r"""
## Phase 7 - Modelling Dataset Preparation

This phase creates the modelling table and stores the exact feature list. The same feature list must be used later for prediction.

The notebook uses a stratified modelling sample by default so model comparison remains fast enough for a live presentation. Increase `MODELING_SAMPLE_SIZE` up to the full dataset size if your machine can handle it.
"""),
    code(r"""
DROP_COLS = ["label", "label_name", "filename", "label_encoded"]
FEATURES = [c for c in df_clean.columns if c not in DROP_COLS]
TARGET = "label"

MODELING_SAMPLE_SIZE = min(12000, len(df_clean))

if MODELING_SAMPLE_SIZE < len(df_clean):
    modelling_df, _ = train_test_split(
        df_clean,
        train_size=MODELING_SAMPLE_SIZE,
        random_state=SEED,
        stratify=df_clean[TARGET],
    )
else:
    modelling_df = df_clean.copy()

X = modelling_df[FEATURES].copy()
y = modelling_df[TARGET].copy()

feature_list = pd.DataFrame({"feature": FEATURES})
feature_list.to_csv(OUTPUT_DIR / "phase_7_model_feature_list.csv", index=False)

modelling_df.to_csv(OUTPUT_DIR / "phase_7_modelling_dataset.csv", index=False)

print(f"Modelling rows: {len(modelling_df):,} / {len(df_clean):,}")
print(f"Feature count: {len(FEATURES)}")
print(FEATURES)
"""),
    code(r"""
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=SEED,
    stratify=y,
)

split_summary = pd.DataFrame({
    "split": ["train", "test"],
    "rows": [len(X_train), len(X_test)],
    "percent": [round(len(X_train) / len(X) * 100, 2), round(len(X_test) / len(X) * 100, 2)],
})

split_summary.to_csv(OUTPUT_DIR / "phase_7_train_test_split_summary.csv", index=False)
display(split_summary)
"""),
    md(r"""
## Phase 8 - Model Comparison

This phase compares multiple models using 5-fold stratified cross-validation. The model with the highest macro-F1 becomes the candidate final model.

If LightGBM is installed, it is used because your existing project report already identifies it as the strongest model.
"""),
    code(r"""
models = {
    "Logistic Regression": Pipeline([
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(max_iter=2000, class_weight="balanced", random_state=SEED)),
    ]),
    "Random Forest": RandomForestClassifier(
        n_estimators=350,
        max_depth=None,
        min_samples_leaf=2,
        class_weight="balanced_subsample",
        random_state=SEED,
        n_jobs=-1,
    ),
    "Gradient Boosting": GradientBoostingClassifier(random_state=SEED),
    "Hist Gradient Boosting": HistGradientBoostingClassifier(
        max_iter=250,
        learning_rate=0.06,
        l2_regularization=0.05,
        random_state=SEED,
    ),
}

if LIGHTGBM_AVAILABLE:
    models["LightGBM"] = LGBMClassifier(
        n_estimators=450,
        learning_rate=0.035,
        max_depth=7,
        num_leaves=31,
        subsample=0.90,
        colsample_bytree=0.90,
        class_weight="balanced",
        random_state=SEED,
        n_jobs=-1,
        verbose=-1,
    )

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)

comparison_rows = []
for name, model in models.items():
    scores = cross_val_score(model, X_train, y_train, cv=cv, scoring="f1_macro", n_jobs=-1)
    comparison_rows.append({
        "model": name,
        "cv_macro_f1_mean": scores.mean(),
        "cv_macro_f1_std": scores.std(),
        "fold_scores": ", ".join(f"{s:.4f}" for s in scores),
    })

model_comparison = (
    pd.DataFrame(comparison_rows)
    .sort_values("cv_macro_f1_mean", ascending=False)
    .reset_index(drop=True)
)

model_comparison.to_csv(OUTPUT_DIR / "phase_8_model_comparison.csv", index=False)
display(model_comparison)
"""),
    code(r"""
plt.figure(figsize=(9, 4.8))
ax = sns.barplot(data=model_comparison, x="cv_macro_f1_mean", y="model")
ax.axvline(TARGET_MACRO_F1, color="red", linestyle="--", label="Target macro-F1")
ax.set_title("Cross-Validated Macro-F1 by Model")
ax.set_xlabel("Mean CV Macro-F1")
ax.set_ylabel("")
ax.legend()
plt.tight_layout()
plt.savefig(FIGURE_DIR / "phase_8_model_comparison.png", dpi=160)
plt.show()
"""),
    md(r"""
## Phase 9 - Final Model Training

This phase trains the best model from the comparison table and evaluates it on a held-out test set.
"""),
    code(r"""
best_model_name = model_comparison.loc[0, "model"]
best_model = models[best_model_name]

best_model.fit(X_train, y_train)
y_pred = best_model.predict(X_test)

if hasattr(best_model, "predict_proba"):
    y_proba = best_model.predict_proba(X_test)
    confidence = y_proba.max(axis=1)
else:
    y_proba = None
    confidence = np.repeat(np.nan, len(y_pred))

print(f"Best model: {best_model_name}")
"""),
    code(r"""
final_metrics = pd.DataFrame([{
    "model": best_model_name,
    "accuracy": accuracy_score(y_test, y_pred),
    "macro_f1": f1_score(y_test, y_pred, average="macro"),
    "weighted_f1": f1_score(y_test, y_pred, average="weighted"),
    "macro_precision": precision_score(y_test, y_pred, average="macro", zero_division=0),
    "macro_recall": recall_score(y_test, y_pred, average="macro", zero_division=0),
    "target_accuracy": TARGET_ACCURACY,
    "target_macro_f1": TARGET_MACRO_F1,
}]).round(4)

final_metrics["accuracy_target_met"] = final_metrics["accuracy"] >= TARGET_ACCURACY
final_metrics["macro_f1_target_met"] = final_metrics["macro_f1"] >= TARGET_MACRO_F1

final_metrics.to_csv(OUTPUT_DIR / "phase_9_final_metrics.csv", index=False)
display(final_metrics)
"""),
    code(r"""
report_dict = classification_report(
    y_test,
    y_pred,
    target_names=[LABEL_MAP[i] for i in sorted(y.unique())],
    zero_division=0,
    output_dict=True,
)

classification_report_df = pd.DataFrame(report_dict).T.round(4)
classification_report_df.to_csv(OUTPUT_DIR / "phase_9_classification_report.csv")
display(classification_report_df)
"""),
    code(r"""
cm = confusion_matrix(y_test, y_pred, labels=sorted(y.unique()))
cm_df = pd.DataFrame(
    cm,
    index=[f"Actual {LABEL_MAP[i]}" for i in sorted(y.unique())],
    columns=[f"Predicted {LABEL_MAP[i]}" for i in sorted(y.unique())],
)
cm_df.to_csv(OUTPUT_DIR / "phase_9_confusion_matrix.csv")

disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=[LABEL_MAP[i] for i in sorted(y.unique())])
disp.plot(cmap="Blues", values_format="d")
plt.title("Held-Out Test Confusion Matrix")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "phase_9_confusion_matrix.png", dpi=160)
plt.show()

display(cm_df)
"""),
    md(r"""
## Phase 10 - Performance Target Decision

This phase converts the scores into a clear decision. This is useful for your final presentation because it states whether the project met its performance target.
"""),
    code(r"""
acc = float(final_metrics.loc[0, "accuracy"])
macro_f1 = float(final_metrics.loc[0, "macro_f1"])

if acc >= TARGET_ACCURACY and macro_f1 >= TARGET_MACRO_F1:
    decision = "PASS"
    recommendation = "The model meets the target and can be used for the next phase: explainability and dashboard integration."
else:
    decision = "IMPROVE"
    recommendation = (
        "The target is not fully met. Improve by increasing training data, tuning LightGBM, checking label noise, "
        "and optimizing for macro-F1 instead of accuracy."
    )

target_decision = pd.DataFrame([{
    "decision": decision,
    "accuracy": acc,
    "macro_f1": macro_f1,
    "recommendation": recommendation,
}])

target_decision.to_csv(OUTPUT_DIR / "phase_10_target_decision.csv", index=False)
display(target_decision)
"""),
    md(r"""
## Phase 11 - Feature Importance and Clinical Interpretation

This phase explains why the model predicts what it predicts. Feature importance connects early EDA observations to the final model result.
"""),
    code(r"""
def get_feature_importance(model, feature_names):
    fitted_model = model
    if isinstance(model, Pipeline):
        fitted_model = model.named_steps["model"]

    if hasattr(fitted_model, "feature_importances_"):
        values = fitted_model.feature_importances_
    elif hasattr(fitted_model, "coef_"):
        values = np.abs(fitted_model.coef_).mean(axis=0)
    else:
        return pd.DataFrame(columns=["feature", "importance"])

    return (
        pd.DataFrame({"feature": feature_names, "importance": values})
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )

feature_importance = get_feature_importance(best_model, FEATURES)
feature_importance.to_csv(OUTPUT_DIR / "phase_11_feature_importance.csv", index=False)
display(feature_importance.head(15))
"""),
    code(r"""
if len(feature_importance) > 0:
    plt.figure(figsize=(9, 5.5))
    top_importance = feature_importance.head(12)
    sns.barplot(data=top_importance, x="importance", y="feature")
    plt.title("Top Model Features")
    plt.xlabel("Importance")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "phase_11_feature_importance.png", dpi=160)
    plt.show()
else:
    print("This model does not expose direct feature importance.")
"""),
    code(r"""
clinical_interpretation = pd.DataFrame([
    ("hrv", "High value usually means rhythm irregularity; often important for arrhythmia separation."),
    ("rr_mean", "Captures beat spacing; strongly linked to rhythm timing."),
    ("heart_rate", "Useful vital sign, but average BPM alone cannot fully diagnose arrhythmia."),
    ("peak_count", "Often redundant with heart rate because both measure beat frequency."),
    ("std", "Captures amplitude variability and signal strength."),
    ("energy", "Measures signal power; may reflect waveform amplitude and recording characteristics."),
    ("skewness", "Captures waveform asymmetry."),
    ("kurtosis", "Captures sharp peaks or heavy tails in the waveform."),
], columns=["feature", "clinical_interpretation"])

clinical_interpretation.to_csv(OUTPUT_DIR / "phase_11_clinical_feature_interpretation.csv", index=False)
display(clinical_interpretation)
"""),
    md(r"""
## Phase 12 - Store Final Predictions for Next Phase

This phase creates a reusable prediction table. The next project phase can use this for explainability, dashboard display, or patient-level reporting.
"""),
    code(r"""
test_predictions = X_test.copy()
test_predictions["true_label"] = y_test.values
test_predictions["true_class"] = test_predictions["true_label"].map(LABEL_MAP)
test_predictions["predicted_label"] = y_pred
test_predictions["predicted_class"] = test_predictions["predicted_label"].map(LABEL_MAP)
test_predictions["confidence"] = confidence
test_predictions["correct"] = test_predictions["true_label"] == test_predictions["predicted_label"]

prediction_path = OUTPUT_DIR / "phase_12_test_predictions_for_next_phase.csv"
test_predictions.to_csv(prediction_path, index=False)

display(test_predictions.head(10))
print(f"Saved next-phase prediction table to: {prediction_path}")
"""),
    code(r"""
if y_proba is not None:
    probability_df = pd.DataFrame(
        y_proba,
        columns=[f"prob_{LABEL_MAP[i]}" for i in best_model.classes_],
        index=X_test.index,
    )
    probability_output = pd.concat([
        y_test.rename("true_label"),
        pd.Series(y_pred, index=X_test.index, name="predicted_label"),
        probability_df,
    ], axis=1)
    probability_output.to_csv(OUTPUT_DIR / "phase_12_prediction_probabilities.csv", index=False)
    display(probability_output.head())
else:
    print("Probability output skipped because the selected model does not support predict_proba.")
"""),
    md(r"""
## Phase 13 - Save Model Artefacts

This phase saves the final model, feature list, and metrics. These files make the next phase reproducible.
"""),
    code(r"""
joblib.dump(best_model, MODEL_DIR / "phase_workflow_best_model.pkl")
joblib.dump(FEATURES, MODEL_DIR / "phase_workflow_feature_list.pkl")

run_manifest = pd.DataFrame([{
    "best_model": best_model_name,
    "dataset_rows": len(df_clean),
    "feature_count": len(FEATURES),
    "accuracy": acc,
    "macro_f1": macro_f1,
    "decision": decision,
    "output_dir": str(OUTPUT_DIR),
}])
run_manifest.to_csv(OUTPUT_DIR / "phase_13_run_manifest.csv", index=False)

display(run_manifest)
print(f"Saved model artefacts to: {MODEL_DIR}")
"""),
    md(r"""
## Phase 14 - Final Result Summary

Use this section in your presentation. It links the initial analysis to the final result:

- Data quality audit confirmed the dataset was usable.
- Class imbalance showed why macro-F1 is more important than accuracy.
- EDA showed HRV and RR timing features carry strong clinical signal.
- Correlation analysis explained redundant features such as heart rate and peak count.
- Model comparison selected the strongest model using cross-validated macro-F1.
- Final evaluation checked whether accuracy and macro-F1 crossed the target threshold.
- Prediction and model artefacts were saved for the next project phase.
"""),
    code(r"""
final_presentation_table = pd.DataFrame([
    ("Phase 1", "Loaded ECG dataset", f"{len(df_raw):,} rows available"),
    ("Phase 3", "Cleaned and audited data", f"{len(df_clean):,} rows retained"),
    ("Phase 4", "Measured class imbalance", f"Majority class: {class_distribution.sort_values('count', ascending=False).iloc[0]['class_name']}"),
    ("Phase 8", "Compared models", f"Best CV model: {best_model_name}"),
    ("Phase 9", "Evaluated final model", f"Accuracy={acc:.3f}, Macro-F1={macro_f1:.3f}"),
    ("Phase 10", "Checked target", decision),
    ("Phase 12", "Stored predictions", str(prediction_path)),
])

final_presentation_table.columns = ["phase", "result", "presentation_point"]
final_presentation_table.to_csv(OUTPUT_DIR / "phase_14_final_presentation_summary.csv", index=False)
display(final_presentation_table)
"""),
]


notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "codemirror_mode": {"name": "ipython", "version": 3},
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.10",
        },
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}


OUT_PATH.write_text(json.dumps(notebook, indent=2), encoding="utf-8")
print(f"Created {OUT_PATH}")

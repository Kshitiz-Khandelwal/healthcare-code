"""
ECG Classification - Training Pipeline
=======================================
Models compared:
  1. Random Forest      (baseline tree ensemble)
  2. XGBoost            (main model — best for tabular data)
  3. Logistic Regression (simple linear baseline)

Improvements over original:
  - XGBoost added with proper imbalance handling (scale_pos_weight / sample_weight)
  - Trimmed to 3 focused models (no SVC/KNN/MLP noise)
  - Gemma-ready: saves prediction + confidence for explanation layer
  - metadata.json saved for FL simulation
  - Per-class F1 printed so rare classes are visible
  - RepeatedStratifiedKFold for tighter CV estimates
"""

import pandas as pd
import numpy as np
import joblib
import json
import warnings
warnings.filterwarnings("ignore")

from sklearn.model_selection import (
    train_test_split, StratifiedKFold,
    RepeatedStratifiedKFold, cross_val_score, learning_curve
)
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, classification_report,
    confusion_matrix, f1_score, ConfusionMatrixDisplay
)
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# XGBoost — main upgrade
try:
    from xgboost import XGBClassifier
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False
    print("[WARN] xgboost not found — pip install xgboost")

try:
    from imblearn.over_sampling import SMOTE
    SMOTE_AVAILABLE = True
except ImportError:
    SMOTE_AVAILABLE = False

SEED = 42
np.random.seed(SEED)

# ─────────────────────────────────────────
# USER CONFIG
# ─────────────────────────────────────────
USE_SMOTE = False   # keep OFF unless you have severe imbalance and understand the risk


# ─────────────────────────────────────────
# 1. LOAD & VALIDATE
# ─────────────────────────────────────────
print("\n" + "="*55)
print("  ECG Classification  Training Pipeline")
print("="*55)

df = pd.read_csv("ecg_dataset.csv")
print(f"\n[OK] Loaded dataset: {df.shape[0]} rows x {df.shape[1]} cols")

FEATURES = [
    "mean", "std", "max", "min",
    "peak_count", "heart_rate",
    "energy", "zero_crossings",
    "age", "sex"
]

TARGET = "label_encoded"

missing = [c for c in FEATURES + [TARGET] if c not in df.columns]
if missing:
    raise ValueError(f"Missing columns in CSV: {missing}")

before = len(df)
df = df.dropna(subset=FEATURES + [TARGET])
if len(df) < before:
    print(f"[WARN] Dropped {before - len(df)} rows with NaN values")


# ─────────────────────────────────────────
# 2. CLASS DISTRIBUTION
# ─────────────────────────────────────────
print("\n Class distribution:")
vc = df[TARGET].value_counts().sort_index()
total = len(df)
for cls, cnt in vc.items():
    bar = "█" * int(30 * cnt / total)
    print(f"  Class {cls:>3}: {cnt:>5} samples  {bar}  ({100*cnt/total:.1f}%)")

num_classes = df[TARGET].nunique()
print(f"\n   {num_classes} classes total")

if vc.min() / vc.max() < 0.3:
    print("  [WARN] Class imbalance detected -> using class_weight='balanced' and XGB scale_pos_weight")
    IMBALANCED = True
else:
    IMBALANCED = False

# Filter rare classes (need at least 10 samples for stratified CV)
MIN_SAMPLES = 10
to_keep = vc[vc >= MIN_SAMPLES].index
before_filter = len(df)
df = df[df[TARGET].isin(to_keep)]
if len(df) < before_filter:
    removed = before_filter - len(df)
    print(f"  [INFO] Filtered {removed} samples from classes with < {MIN_SAMPLES} examples")
    num_classes = df[TARGET].nunique()


# ─────────────────────────────────────────
# 3. FEATURES & SPLIT
# ─────────────────────────────────────────
X = df[FEATURES].values
y = df[TARGET].values

# Re-encode labels to 0..N-1 (required by XGBoost)
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
y = le.fit_transform(y)
class_names = [str(c) for c in le.classes_]

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=SEED,
    stratify=y
)
print(f"\n Train/Test split: {len(X_train)} train  |  {len(X_test)} test")


# ─────────────────────────────────────────
# 4. SCALING
# ─────────────────────────────────────────
scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)


# ─────────────────────────────────────────
# 5. OPTIONAL SMOTE
# ─────────────────────────────────────────
if USE_SMOTE and SMOTE_AVAILABLE and IMBALANCED:
    try:
        sm = SMOTE(random_state=SEED, k_neighbors=min(5, vc.min()-1))
        X_train_sc, y_train = sm.fit_resample(X_train_sc, y_train)
        print(f"[OK] SMOTE applied -> training set: {len(X_train_sc)} samples")
    except Exception as e:
        print(f"[WARN] SMOTE failed ({e}), continuing without it")


# ─────────────────────────────────────────
# 6. MODEL DEFINITIONS
# ─────────────────────────────────────────
cw = "balanced" if IMBALANCED else None

# XGBoost: for imbalanced multiclass we use sample_weight instead of scale_pos_weight
# (scale_pos_weight is only for binary; for multiclass use compute_sample_weight)
from sklearn.utils.class_weight import compute_sample_weight

models = {
    "Random Forest": RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        min_samples_leaf=2,
        class_weight=cw,
        random_state=SEED,
        n_jobs=-1
    ),
    "Logistic Regression": LogisticRegression(
        max_iter=1000,
        class_weight=cw,
        C=1.0,
        random_state=SEED,
        n_jobs=-1
    ),
}

if XGB_AVAILABLE:
    models["XGBoost"] = XGBClassifier(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        use_label_encoder=False,
        eval_metric="mlogloss",
        random_state=SEED,
        n_jobs=-1,
        verbosity=0
    )
else:
    print("[WARN] XGBoost skipped — not installed")


# ─────────────────────────────────────────
# 7. CROSS-VALIDATION COMPARISON
#    RepeatedStratifiedKFold = tighter estimates
#    (5 folds x 3 repeats = 15 scores per model)
# ─────────────────────────────────────────
cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=3, random_state=SEED)

print("\n" + "─"*55)
print("  Cross-Validation: 5-Fold × 3 Repeats")
print("─"*55)

cv_results = {}
for name, clf in models.items():
    scores = cross_val_score(
        clf, X_train_sc, y_train,
        cv=cv, scoring="f1_macro", n_jobs=-1
    )
    cv_results[name] = scores
    print(f"  {name:<22}  macro-F1: {scores.mean():.4f} ± {scores.std():.4f}")

# Pick best — bias toward RF only if XGB not available or very close
best_name = max(cv_results, key=lambda k: cv_results[k].mean())
print(f"\n  [BEST] {best_name}  (macro-F1: {cv_results[best_name].mean():.4f})")


# ─────────────────────────────────────────
# 8. TRAIN BEST MODEL ON FULL TRAINING SET
# ─────────────────────────────────────────
best_model = models[best_name]

# XGBoost with imbalanced data: pass sample_weight at fit time
if best_name == "XGBoost" and IMBALANCED:
    sw = compute_sample_weight("balanced", y_train)
    best_model.fit(X_train_sc, y_train, sample_weight=sw)
else:
    best_model.fit(X_train_sc, y_train)

# Train metrics (to check overfitting)
y_train_pred = best_model.predict(X_train_sc)
train_acc = accuracy_score(y_train, y_train_pred)
train_f1  = f1_score(y_train, y_train_pred, average="macro")

# Test metrics
y_pred = best_model.predict(X_test_sc)
test_acc = accuracy_score(y_test, y_pred)
test_f1  = f1_score(y_test, y_pred, average="macro")

# Prediction probabilities (for Gemma explanation layer)
if hasattr(best_model, "predict_proba"):
    y_pred_proba = best_model.predict_proba(X_test_sc)
    y_pred_conf  = y_pred_proba.max(axis=1)
else:
    y_pred_conf = np.ones(len(y_pred))

baseline_acc = max(np.bincount(y_test)) / len(y_test)

print("\n" + "="*55)
print("  Final Evaluation — Held-Out Test Set")
print("="*55)
print(f"\n  Train  accuracy: {train_acc:.4f}   macro-F1: {train_f1:.4f}")
print(f"  Test   accuracy: {test_acc:.4f}   macro-F1: {test_f1:.4f}")
print(f"  Baseline acc   : {baseline_acc:.4f}  (majority class always)")

gap = train_acc - test_acc
if gap > 0.15:
    print(f"\n  [WARN] Overfit gap = {gap:.3f} — try more regularization")
elif test_acc < 0.5:
    print(f"\n  [WARN] Low accuracy — check features and class labels")
else:
    print(f"\n  [OK] Good generalisation (train-test gap = {gap:.3f})")

print("\n Classification Report (per class):")
print(classification_report(y_test, y_pred,
                             target_names=class_names,
                             zero_division=0))

cm = confusion_matrix(y_test, y_pred)
print(" Confusion Matrix:")
print(cm)


# ─────────────────────────────────────────
# 9. FEATURE IMPORTANCE
# ─────────────────────────────────────────
if hasattr(best_model, "feature_importances_"):
    importances = best_model.feature_importances_
    feat_imp = sorted(zip(FEATURES, importances), key=lambda x: x[1], reverse=True)
    print("\n Feature Importances:")
    for feat, imp in feat_imp:
        bar = "█" * int(20 * imp / importances.max())
        print(f"  {feat:<18} {imp:.4f}  {bar}")


# ─────────────────────────────────────────
# 10. SAVE PREDICTIONS (Gemma-ready format)
# ─────────────────────────────────────────
df_test_out = pd.DataFrame(X_test, columns=FEATURES)
df_test_out["true_label"]  = le.inverse_transform(y_test)
df_test_out["pred_label"]  = le.inverse_transform(y_pred)
df_test_out["confidence"]  = y_pred_conf
df_test_out["correct"]     = (y_test == y_pred)
df_test_out.to_csv("validation_predictions.csv", index=False)
print("\n[OK] validation_predictions.csv saved (includes confidence for Gemma layer)")


# ─────────────────────────────────────────
# 11. VISUALISATIONS
# ─────────────────────────────────────────
fig = plt.figure(figsize=(18, 12))
fig.patch.set_facecolor("#0f0f1a")
gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.4)

ACCENT  = "#00e5ff"
ACCENT2 = "#ff4081"
ACCENT3 = "#69ff47"
BG      = "#0f0f1a"
PANEL   = "#1a1a2e"
TEXTC   = "#e0e0e0"

def style_ax(ax, title):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=TEXTC, labelsize=9)
    for sp in ax.spines.values():
        sp.set_color("#333355")
    ax.set_title(title, color=ACCENT, fontsize=11, pad=10, fontweight="bold")

# 11a. CV Score comparison (all 3 models)
ax1 = fig.add_subplot(gs[0, 0])
style_ax(ax1, "CV Macro-F1 by Model")
names  = list(cv_results.keys())
means  = [cv_results[n].mean() for n in names]
stds   = [cv_results[n].std()  for n in names]
colors = [ACCENT if n == best_name else "#334466" for n in names]
bars = ax1.barh(names, means, xerr=stds, color=colors,
                error_kw=dict(ecolor=ACCENT2, capsize=4), height=0.5)
ax1.set_xlim(0, 1)
ax1.set_xlabel("Macro-F1", color=TEXTC)
for bar, val in zip(bars, means):
    ax1.text(val + 0.01, bar.get_y() + bar.get_height()/2,
             f"{val:.3f}", va="center", color=TEXTC, fontsize=9)

# 11b. Confusion Matrix
ax2 = fig.add_subplot(gs[0, 1])
style_ax(ax2, "Confusion Matrix")
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
disp.plot(ax=ax2, colorbar=False, cmap="YlOrRd")
ax2.set_facecolor(PANEL)
ax2.xaxis.label.set_color(TEXTC)
ax2.yaxis.label.set_color(TEXTC)
ax2.tick_params(colors=TEXTC)

# 11c. Feature Importance
ax3 = fig.add_subplot(gs[0, 2])
style_ax(ax3, "Feature Importance")
if hasattr(best_model, "feature_importances_"):
    feats, imps = zip(*feat_imp)
    colors_fi = [ACCENT if i == 0 else "#334477" for i in range(len(feats))]
    ax3.barh(list(feats)[::-1], list(imps)[::-1], color=colors_fi[::-1], height=0.6)
    ax3.set_xlabel("Importance", color=TEXTC)
else:
    ax3.text(0.5, 0.5, "N/A for this model",
             ha="center", va="center", color=TEXTC, transform=ax3.transAxes)

# 11d. Class distribution
ax4 = fig.add_subplot(gs[1, 0])
style_ax(ax4, "Class Distribution")
vc_filtered = df[TARGET].value_counts().sort_index()
cls_labels  = [str(c) for c in vc_filtered.index]
ax4.bar(cls_labels, vc_filtered.values,
        color=[ACCENT if i % 2 == 0 else ACCENT2 for i in range(len(vc_filtered))],
        width=0.6)
ax4.set_xlabel("Class", color=TEXTC)
ax4.set_ylabel("Count",  color=TEXTC)

# 11e. Learning Curve
ax5 = fig.add_subplot(gs[1, 1:])
style_ax(ax5, "Learning Curve (Train vs CV)")
train_sizes, train_scores, val_scores = learning_curve(
    best_model, X_train_sc, y_train,
    cv=3, scoring="f1_macro",
    train_sizes=np.linspace(0.1, 1.0, 8),
    n_jobs=-1
)
ts_mean = train_scores.mean(axis=1)
ts_std  = train_scores.std(axis=1)
vs_mean = val_scores.mean(axis=1)
vs_std  = val_scores.std(axis=1)

ax5.plot(train_sizes, ts_mean, color=ACCENT,  lw=2, label="Train F1")
ax5.fill_between(train_sizes, ts_mean-ts_std, ts_mean+ts_std, alpha=0.2, color=ACCENT)
ax5.plot(train_sizes, vs_mean, color=ACCENT2, lw=2, label="CV F1", linestyle="--")
ax5.fill_between(train_sizes, vs_mean-vs_std, vs_mean+vs_std, alpha=0.2, color=ACCENT2)
ax5.set_xlabel("Training samples", color=TEXTC)
ax5.set_ylabel("Macro-F1",         color=TEXTC)
ax5.legend(facecolor=PANEL, labelcolor=TEXTC)
ax5.set_ylim(0, 1.05)

fig.suptitle(
    f"ECG Classification  |  {best_name}  |  Test Acc {test_acc:.3f}  |  F1 {test_f1:.3f}",
    color=TEXTC, fontsize=14, fontweight="bold", y=0.98
)

plt.savefig("training_results.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("[OK] training_results.png saved")


# ─────────────────────────────────────────
# 12. SAVE ARTEFACTS
# ─────────────────────────────────────────
joblib.dump(best_model, "model.pkl")
joblib.dump(scaler,     "scaler.pkl")
joblib.dump(le,         "label_encoder.pkl")

# metadata.json — needed for FL simulation + Gemma layer
metadata = {
    "model_name":     best_name,
    "features":       FEATURES,
    "num_classes":    int(num_classes),
    "class_names":    class_names,
    "train_samples":  int(len(X_train)),
    "test_acc":       round(float(test_acc), 4),
    "test_f1_macro":  round(float(test_f1), 4),
    "imbalanced":     IMBALANCED,
    "seed":           SEED,
}
with open("metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)

print("\n[OK] Saved: model.pkl | scaler.pkl | label_encoder.pkl | metadata.json")

print("\n" + "="*55)
print("  Pipeline complete — ready for FL simulation")
print("  Next: load validation_predictions.csv into Gemma layer")
print("="*55 + "\n")
"""
ECG Classification - Proper Training Pipeline
==============================================
Phases applied:
  4. LightGBM replaces Random Forest as primary model
  5. Safe data loading: 4000-sample cap + correct column selection
  6. Evaluation: classification_report + confusion_matrix  (preserved)
  7. Model + scaler saved via joblib                        (preserved)
  + Cross-validation, class imbalance handling, feature importance,
    learning curve, and all visualisations from the original pipeline
"""

import pandas as pd
import numpy as np
import joblib
import warnings
warnings.filterwarnings("ignore")

from sklearn.model_selection import (
    train_test_split, StratifiedKFold, cross_val_score, learning_curve
)
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, classification_report,
    confusion_matrix, f1_score, ConfusionMatrixDisplay
)
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression

# PHASE 4 — LightGBM import
from lightgbm import LGBMClassifier

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

try:
    from imblearn.over_sampling import SMOTE
    SMOTE_AVAILABLE = True
except ImportError:
    SMOTE_AVAILABLE = False
    print("  imbalanced-learn not found — skipping SMOTE (pip install imbalanced-learn)")

SEED = 42
np.random.seed(SEED)

USE_SMOTE = False   # keep OFF to avoid unrealistic synthetic patients

# ── 1. LOAD & VALIDATE ────────────────────────────────────────────────────────
print("\n" + "="*55)
print("  ECG Classification — Training Pipeline")
print("="*55)

# PHASE 5 — cap at 4 000 rows to avoid OOM crashes during early runs
df = pd.read_csv("ecg_dataset.csv").sample(n=min(4000, len(pd.read_csv("ecg_dataset.csv"))),
                                            random_state=SEED)
print(f"\n[OK] Loaded dataset: {df.shape[0]} rows × {df.shape[1]} cols")

# PHASE 5 — derive X/y directly from column names (no hard-coded label_encoded)
DROP_COLS = ["label", "filename", "label_encoded"]   # drop any that exist
feature_cols = [c for c in df.columns if c not in DROP_COLS]

# Target: prefer the 3-class 'label' column produced by updated extract.py;
# fall back to 'label_encoded' if the old pipeline was used
if "label" in df.columns:
    TARGET_COL = "label"
elif "label_encoded" in df.columns:
    TARGET_COL = "label_encoded"
else:
    raise ValueError("No target column found. Expected 'label' or 'label_encoded'.")

FEATURES = [c for c in feature_cols if c != TARGET_COL]

print(f"[OK] Features ({len(FEATURES)}): {FEATURES}")
print(f"[OK] Target column: '{TARGET_COL}'")

# Validate columns
missing = [c for c in FEATURES + [TARGET_COL] if c not in df.columns]
if missing:
    raise ValueError(f"Missing columns in CSV: {missing}")

# Drop NaN rows
before = len(df)
df = df.dropna(subset=FEATURES + [TARGET_COL])
if len(df) < before:
    print(f"[WARN] Dropped {before - len(df)} rows with NaN values")

# ── 2. CLASS DISTRIBUTION ─────────────────────────────────────────────────────
print("\n Class distribution:")
vc = df[TARGET_COL].value_counts().sort_index()
total = len(df)
label_names = {0: "Normal", 1: "Arrhythmia", 2: "Other"}

for cls, cnt in vc.items():
    name = label_names.get(cls, str(cls))
    bar  = "█" * int(30 * cnt / total)
    print(f"  Class {cls} ({name:<12}): {cnt:>5} samples  {bar}  ({100*cnt/total:.1f}%)")

num_classes = df[TARGET_COL].nunique()
print(f"\n   {num_classes} classes total")

IMBALANCED = vc.min() / vc.max() < 0.3
if IMBALANCED:
    print("  [WARN] Class imbalance detected → will apply class_weight='balanced'")

# Drop classes with too few samples (stratification guard)
MIN_SAMPLES = 10
to_keep = vc[vc >= MIN_SAMPLES].index
before_filter = len(df)
df = df[df[TARGET_COL].isin(to_keep)]
if len(df) < before_filter:
    print(f"  [INFO] Filtered {before_filter - len(df)} samples from tiny classes")
    num_classes = df[TARGET_COL].nunique()

# ── 3. FEATURES & SPLIT ───────────────────────────────────────────────────────
X = df[FEATURES].values
y = df[TARGET_COL].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=SEED, stratify=y
)
print(f"\n Train/Test split: {len(X_train)} train  |  {len(X_test)} test")

# ── 4. SCALING ────────────────────────────────────────────────────────────────
scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)

# ── 5. OPTIONAL SMOTE ────────────────────────────────────────────────────────
if USE_SMOTE and SMOTE_AVAILABLE and IMBALANCED:
    try:
        sm = SMOTE(random_state=SEED, k_neighbors=min(5, vc.min()-1))
        X_train_sc, y_train = sm.fit_resample(X_train_sc, y_train)
        print(f"[OK] SMOTE applied → training set: {len(X_train_sc)} samples")
    except Exception as e:
        print(f"[WARN] SMOTE failed ({e}), continuing without it")

# ── 6. MODEL COMPARISON ───────────────────────────────────────────────────────
cw = "balanced" if IMBALANCED else None

# PHASE 4 — LightGBM as primary model
models = {
    "LightGBM": LGBMClassifier(          # ← PHASE 4
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05,
        class_weight="balanced",
        random_state=SEED,
        n_jobs=-1,
        verbosity=-1
    ),
    "Gradient Boosting": GradientBoostingClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=4,
        random_state=SEED
    ),
    "Logistic Regression": LogisticRegression(
        max_iter=1000,
        class_weight=cw,
        C=1.0,
        random_state=SEED,
        n_jobs=-1
    ),
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)

print("\n" + "─"*55)
print("  5-Fold Cross-Validation Comparison")
print("─"*55)

cv_results = {}
for name, clf in models.items():
    scores = cross_val_score(clf, X_train_sc, y_train,
                             cv=cv, scoring="f1_macro", n_jobs=-1)
    cv_results[name] = scores
    print(f"  {name:<22}  macro-F1: {scores.mean():.4f} ± {scores.std():.4f}")

# Bias toward LightGBM if within 1% of best
best_name = max(cv_results, key=lambda k: cv_results[k].mean())
lgbm_score = cv_results["LightGBM"].mean()
best_score  = cv_results[best_name].mean()

if best_name != "LightGBM" and (best_score - lgbm_score) < 0.01:
    print(f"\n  [INFO] LightGBM within 1% of {best_name} — biasing toward LightGBM.")
    best_name = "LightGBM"

print(f"\n  [BEST] Best model: {best_name}")

# ── 7. TRAIN BEST MODEL ON FULL TRAIN SET ────────────────────────────────────
best_model = models[best_name]
best_model.fit(X_train_sc, y_train)

y_train_pred = best_model.predict(X_train_sc)
train_acc = accuracy_score(y_train, y_train_pred)
train_f1  = f1_score(y_train, y_train_pred, average="macro")

y_pred   = best_model.predict(X_test_sc)
test_acc = accuracy_score(y_test, y_pred)
test_f1  = f1_score(y_test, y_pred, average="macro")

baseline_acc = max(np.bincount(y_test.astype(int))) / len(y_test)

print("\n" + "="*55)
print("  Final Evaluation on Held-Out Test Set")
print("="*55)
print(f"\n  Train accuracy : {train_acc:.4f}   macro-F1: {train_f1:.4f}")
print(f"  Test  accuracy : {test_acc:.4f}   macro-F1: {test_f1:.4f}")
print(f"\n  [INFO] Baseline Accuracy (majority class): {baseline_acc:.4f}")

gap = train_acc - test_acc
if gap > 0.15:
    print(f"\n  [WARN] Overfit gap = {gap:.3f} — consider more regularisation")
elif test_acc < 0.5:
    print(f"\n  [WARN] Low accuracy — check features and class labels")
else:
    print(f"\n  [OK] Good generalisation (gap = {gap:.3f})")

# PHASE 6 — Classification report + confusion matrix
print("\n Classification Report:")
target_names = [label_names.get(c, str(c)) for c in sorted(np.unique(y_test))]
print(classification_report(y_test, y_pred, target_names=target_names, zero_division=0))

cm = confusion_matrix(y_test, y_pred)
print(" Confusion Matrix:")
print(cm)

# Save predictions for debugging
pd.DataFrame({"true": y_test, "pred": y_pred}).to_csv("validation_predictions.csv", index=False)
print("\n[OK] Predictions saved to validation_predictions.csv")

# ── 8. FEATURE IMPORTANCE ─────────────────────────────────────────────────────
feat_imp = None
if hasattr(best_model, "feature_importances_"):
    importances = best_model.feature_importances_
    feat_imp = sorted(zip(FEATURES, importances), key=lambda x: x[1], reverse=True)
    print("\n Feature Importances:")
    for feat, imp in feat_imp:
        bar = "█" * int(20 * imp / importances.max())
        print(f"  {feat:<18} {imp:.4f}  {bar}")

# ── 9. VISUALISATIONS ─────────────────────────────────────────────────────────
fig = plt.figure(figsize=(18, 12))
fig.patch.set_facecolor("#0f0f1a")
gs_layout = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.4)

ACCENT  = "#00e5ff"
ACCENT2 = "#ff4081"
BG      = "#0f0f1a"
PANEL   = "#1a1a2e"
TEXTC   = "#e0e0e0"

def style_ax(ax, title):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=TEXTC, labelsize=9)
    for sp in ax.spines.values():
        sp.set_color("#333355")
    ax.set_title(title, color=ACCENT, fontsize=11, pad=10, fontweight="bold")

# 9a. CV Score comparison
ax1 = fig.add_subplot(gs_layout[0, 0])
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

# 9b. Confusion Matrix
ax2 = fig.add_subplot(gs_layout[0, 1])
style_ax(ax2, "Confusion Matrix")
disp = ConfusionMatrixDisplay(confusion_matrix=cm,
                               display_labels=target_names)
disp.plot(ax=ax2, colorbar=False, cmap="YlOrRd")
ax2.set_facecolor(PANEL)
ax2.xaxis.label.set_color(TEXTC)
ax2.yaxis.label.set_color(TEXTC)
ax2.tick_params(colors=TEXTC)

# 9c. Feature Importance
ax3 = fig.add_subplot(gs_layout[0, 2])
style_ax(ax3, "Feature Importance")
if feat_imp:
    feats, imps = zip(*feat_imp)
    colors_fi = [ACCENT if i == 0 else "#334477" for i in range(len(feats))]
    ax3.barh(list(feats)[::-1], list(imps)[::-1], color=colors_fi[::-1], height=0.6)
    ax3.set_xlabel("Importance", color=TEXTC)
else:
    ax3.text(0.5, 0.5, "N/A for this model",
             ha="center", va="center", color=TEXTC, transform=ax3.transAxes)

# 9d. Class distribution
ax4 = fig.add_subplot(gs_layout[1, 0])
style_ax(ax4, "Class Distribution")
cls_labels = [label_names.get(c, str(c)) for c in vc.index]
ax4.bar(cls_labels, vc.values,
        color=[ACCENT if i % 2 == 0 else ACCENT2 for i in range(len(vc))],
        width=0.6)
ax4.set_xlabel("Class", color=TEXTC)
ax4.set_ylabel("Count",  color=TEXTC)

# 9e. Learning Curve
ax5 = fig.add_subplot(gs_layout[1, 1:])
style_ax(ax5, "Learning Curve (Train vs CV)")
train_sizes, train_scores, val_scores = learning_curve(
    best_model, X_train_sc, y_train,
    cv=3, scoring="f1_macro",
    train_sizes=np.linspace(0.1, 1.0, 8),
    n_jobs=-1
)
ts_mean = train_scores.mean(axis=1);  ts_std = train_scores.std(axis=1)
vs_mean = val_scores.mean(axis=1);    vs_std = val_scores.std(axis=1)

ax5.plot(train_sizes, ts_mean, color=ACCENT,  lw=2, label="Train F1")
ax5.fill_between(train_sizes, ts_mean-ts_std, ts_mean+ts_std, alpha=0.2, color=ACCENT)
ax5.plot(train_sizes, vs_mean, color=ACCENT2, lw=2, label="CV F1", linestyle="--")
ax5.fill_between(train_sizes, vs_mean-vs_std, vs_mean+vs_std, alpha=0.2, color=ACCENT2)
ax5.set_xlabel("Training samples", color=TEXTC)
ax5.set_ylabel("Macro-F1",         color=TEXTC)
ax5.legend(facecolor=PANEL, labelcolor=TEXTC)
ax5.set_ylim(0, 1.05)

fig.suptitle(
    f"ECG Classification — {best_name} — Test Acc {test_acc:.3f}  F1 {test_f1:.3f}",
    color=TEXTC, fontsize=14, fontweight="bold", y=0.98
)

out_fig = "training_results.png"
plt.savefig(out_fig, dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print(f"\n Visualisation saved → {out_fig}")

# ── 10. SAVE ARTEFACTS (Phase 7 — for FL simulation) ─────────────────────────
joblib.dump(best_model, "model.pkl")
joblib.dump(scaler,     "scaler.pkl")

print("\n Saved: model.pkl  |  scaler.pkl")
print("\n" + "="*55)
print("   Pipeline complete — ready for FL simulation")
print("="*55 + "\n")
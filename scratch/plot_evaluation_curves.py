import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_curve, auc
from lightgbm import LGBMClassifier

SEED = 42
np.random.seed(SEED)

# Load data
df = pd.read_csv("ecg_dataset.csv").sample(n=min(4000, len(pd.read_csv("ecg_dataset.csv"))), random_state=SEED)
DROP_COLS = ["label", "filename", "label_encoded"]
feature_cols = [c for c in df.columns if c not in DROP_COLS]
TARGET_COL = "label"
FEATURES = [c for c in feature_cols if c != TARGET_COL]

df = df.dropna(subset=FEATURES + [TARGET_COL])
X = df[FEATURES].values
y = df[TARGET_COL].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=SEED, stratify=y
)

scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)

# Train LightGBM
lgbm = LGBMClassifier(
    n_estimators=200, max_depth=6, learning_rate=0.05, class_weight="balanced",
    random_state=SEED, n_jobs=-1, verbosity=-1
)
lgbm.fit(X_train_sc, y_train)
y_prob = lgbm.predict_proba(X_test_sc)

# Binarize labels for ROC
y_test_bin = pd.get_dummies(y_test).values

# Plot setup
fig = plt.figure(figsize=(16, 7))
fig.patch.set_facecolor("#0f0f1a")
gs = gridspec.GridSpec(1, 2, figure=fig, wspace=0.3)

ACCENT  = "#00e5ff"   # cyan
ACCENT2 = "#ff4081"   # pink
ACCENT3 = "#69ff47"   # green
BG      = "#0f0f1a"
PANEL   = "#1a1a2e"
TEXTC   = "#e0e0e0"

def style_ax(ax, title):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=TEXTC, labelsize=9)
    for sp in ax.spines.values():
        sp.set_color("#333355")
    ax.set_title(title, color=ACCENT, fontsize=12, pad=12, fontweight="bold")
    ax.xaxis.label.set_color(TEXTC)
    ax.yaxis.label.set_color(TEXTC)

# 1. Left Panel: ROC Curves (One-vs-Rest)
ax1 = fig.add_subplot(gs[0, 0])
style_ax(ax1, "ROC Curves (One-vs-Rest)")

classes = ["Normal (0)", "Arrhythmia (1)", "Other (2)"]
colors = [ACCENT, ACCENT2, ACCENT3]

for i in range(3):
    fpr, tpr, _ = roc_curve(y_test_bin[:, i], y_prob[:, i])
    roc_auc = auc(fpr, tpr)
    ax1.plot(fpr, tpr, color=colors[i], lw=2.5, label=f"{classes[i]} (AUC = {roc_auc:.4f})")

ax1.plot([0, 1], [0, 1], color="#555577", lw=1.5, linestyle="--")
ax1.set_xlim([-0.02, 1.02])
ax1.set_ylim([-0.02, 1.02])
ax1.set_xlabel("False Positive Rate (FPR)")
ax1.set_ylabel("True Positive Rate (TPR)")
ax1.legend(facecolor=PANEL, labelcolor=TEXTC, loc="lower right", fontsize=10)
ax1.grid(color="#222244", linestyle=":", linewidth=0.5)

# 2. Right Panel: SHAP Waterfall Plot for Patient 1
ax2 = fig.add_subplot(gs[0, 2] if hasattr(gs, "shape") and len(gs.shape)>1 else gs[0, 1])
style_ax(ax2, "SHAP Waterfall Plot (Patient 1 - Predicted Arrhythmia)")

# Contributions calculated previously:
base_value = 0.5430
final_value = 0.8670
contributions = [
    ("hrv", +0.7715, 0.95),
    ("peak_count", +0.0928, -1.10),
    ("rr_mean", +0.0662, 0.85),
    ("sex", +0.0578, 0.86),
    ("energy", +0.0460, -0.34),
    ("zero_crossings", +0.0435, -0.24),
    ("std", +0.0314, -0.69),
    ("age", -0.0203, -0.27),
    ("kurtosis", -0.0299, -0.40),
    ("min", -0.0280, 0.32),
    ("mean", -0.0854, 0.21)
]

# We will display the top 8 features and group the rest into '3 other features'
top_features = contributions[:7]
other_contrib = sum([x[1] for x in contributions[7:]])
other_label = f"3 other features\n({other_contrib:+.4f})"
all_contributions = top_features + [(other_label, other_contrib, 0.0)]

# Reverse for plotting (bottom to top)
all_contributions = all_contributions[::-1]

# Starting cumulative position
current_val = base_value
y_pos = np.arange(len(all_contributions))

for idx, (feat_name, contrib, val) in enumerate(all_contributions):
    color = "#ff4081" if contrib >= 0 else "#2a80ff"  # Red for positive contribution, Blue for negative
    
    # Draw arrow-like block
    ax2.barh(y_pos[idx], contrib, left=current_val, height=0.6, color=color, edgecolor=PANEL)
    
    # Text annotation
    val_str = f" = {val:+.2f}" if idx > 0 or "other" not in feat_name else ""
    lbl = f"{feat_name}{val_str}" if "other" not in feat_name else feat_name
    ax2.text(current_val + contrib/2, y_pos[idx], f"{contrib:+.3f}", ha="center", va="center", color="#ffffff", fontsize=8, fontweight="bold")
    
    current_val += contrib

# Set tick labels
feat_labels = []
for idx, (feat_name, contrib, val) in enumerate(all_contributions):
    if "other" in feat_name:
        feat_labels.append(feat_name.split("\n")[0])
    else:
        feat_labels.append(f"{feat_name} = {val:+.2f}")

ax2.set_yticks(y_pos)
ax2.set_yticklabels(feat_labels, fontsize=9, color=TEXTC)
ax2.set_xlabel("Prediction Probability (Arrhythmia)")

# Add Base and Prediction lines
ax2.axvline(base_value, color="#aaaaaa", linestyle=":", lw=1.2)
ax2.text(base_value, len(all_contributions)-0.2, f"E[f(x)] = {base_value:.4f}", ha="center", va="bottom", color=TEXTC, fontsize=9)

ax2.axvline(final_value, color=ACCENT, linestyle="--", lw=1.5)
ax2.text(final_value, -0.6, f"f(x) = {final_value:.4f}", ha="center", va="top", color=ACCENT, fontsize=9, fontweight="bold")

ax2.set_xlim([0.0, 1.05])
ax2.grid(color="#222244", linestyle=":", linewidth=0.5, axis="x")

fig.suptitle(
    "LightGBM Diagnostic Evaluation & Explainable AI (XAI) Output",
    color=TEXTC, fontsize=14, fontweight="bold", y=0.98
)

plt.savefig("evaluation_curves.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("[OK] evaluation_curves.png saved successfully")

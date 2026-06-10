import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score, roc_curve, auc, roc_auc_score
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from lightgbm import LGBMClassifier
from statsmodels.stats.contingency_tables import mcnemar

SEED = 42
np.random.seed(SEED)

# Load data
df = pd.read_csv("ecg_dataset.csv").sample(n=min(4000, len(pd.read_csv("ecg_dataset.csv"))), random_state=SEED)
DROP_COLS = ["label", "filename", "label_encoded"]
feature_cols = [c for c in df.columns if c not in DROP_COLS]
TARGET_COL = "label"
FEATURES = [c for c in feature_cols if c != TARGET_COL]

df = df.dropna(subset=FEATURES + [TARGET_COL])
vc = df[TARGET_COL].value_counts().sort_index()

MIN_SAMPLES = 10
to_keep = vc[vc >= MIN_SAMPLES].index
df = df[df[TARGET_COL].isin(to_keep)]

X = df[FEATURES].values
y = df[TARGET_COL].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=SEED, stratify=y
)

scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)

# Define models
models = {
    "Logistic Regression": LogisticRegression(
        max_iter=1000, class_weight="balanced", C=1.0, random_state=SEED, n_jobs=-1
    ),
    "Gradient Boosting": GradientBoostingClassifier(
        n_estimators=100, learning_rate=0.1, max_depth=4, random_state=SEED
    ),
    "LightGBM": LGBMClassifier(
        n_estimators=200, max_depth=6, learning_rate=0.05, class_weight="balanced",
        random_state=SEED, n_jobs=-1, verbosity=-1
    )
}

# 1. 5-Fold Cross Validation detailed scores
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
cv_scores = {}
print("=== 5-Fold Cross-Validation Macro-F1 Folds ===")
for name, clf in models.items():
    scores = []
    for train_idx, val_idx in cv.split(X_train_sc, y_train):
        X_tr, X_val = X_train_sc[train_idx], X_train_sc[val_idx]
        y_tr, y_val = y_train[train_idx], y_train[val_idx]
        
        clf_fold = clf
        clf_fold.fit(X_tr, y_tr)
        preds = clf_fold.predict(X_val)
        scores.append(f1_score(y_val, preds, average="macro"))
    cv_scores[name] = scores
    print(f"{name}: {[round(s, 4) for s in scores]} (Mean: {np.mean(scores):.4f} ± {np.std(scores):.4f})")

# Train models on full train set
lgbm = models["LightGBM"]
lgbm.fit(X_train_sc, y_train)
y_pred_lgbm = lgbm.predict(X_test_sc)
y_prob_lgbm = lgbm.predict_proba(X_test_sc)

gb = models["Gradient Boosting"]
gb.fit(X_train_sc, y_train)
y_pred_gb = gb.predict(X_test_sc)

# 2. Classification Report for LightGBM
print("\n=== LightGBM Classification Report ===")
report = classification_report(y_test, y_pred_lgbm, target_names=["Normal (0)", "Arrhythmia (1)", "Other (2)"], output_dict=True)
print(pd.DataFrame(report).transpose().to_string())

# 3. McNemar's Test between LightGBM and Gradient Boosting
# Contingency table:
#               GB Correct    GB Incorrect
# LGBM Correct       a             b
# LGBM Incorrect     c             d
correct_lgbm = (y_pred_lgbm == y_test)
correct_gb = (y_pred_gb == y_test)

a = np.sum(correct_lgbm & correct_gb)
b = np.sum(correct_lgbm & ~correct_gb)
c = np.sum(~correct_lgbm & correct_gb)
d = np.sum(~correct_lgbm & ~correct_gb)

contingency = [[a, b], [c, d]]
res = mcnemar(contingency, exact=True)
print("\n=== McNemar's Test between LightGBM & Gradient Boosting ===")
print("Contingency Table:")
print(f"Both correct (a): {a}")
print(f"LGBM correct, GB incorrect (b): {b}")
print(f"LGBM incorrect, GB correct (c): {c}")
print(f"Both incorrect (d): {d}")
print(f"p-value: {res.pvalue:.6f}")

# 4. ROC curves and AUC scores (One-vs-Rest)
print("\n=== ROC AUC Scores (One-vs-Rest) ===")
# binarize target
y_test_bin = pd.get_dummies(y_test).values
for i in range(3):
    auc_score = roc_auc_score(y_test_bin[:, i], y_prob_lgbm[:, i])
    print(f"Class {i} AUC: {auc_score:.4f}")

# 5. Prediction CSV False Positive & False Negative Rates
# For multi-class, let's compute FP and FN per class on the test set.
# False Positive Rate (FPR) = FP / (FP + TN)
# False Negative Rate (FNR) = FN / (TP + FN) = 1 - Recall
cm = confusion_matrix(y_test, y_pred_lgbm)
print("\n=== FP and FN Rates per Class ===")
for i in range(3):
    tp = cm[i, i]
    fn = np.sum(cm[i, :]) - tp
    fp = np.sum(cm[:, i]) - tp
    tn = np.sum(cm) - tp - fn - fp
    
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
    fnr = fn / (tp + fn) if (tp + fn) > 0 else 0
    print(f"Class {i} ({['Normal', 'Arrhythmia', 'Other'][i]}):")
    print(f"  False Positive Rate (FPR): {fpr:.4f} (FP: {fp}, TN: {tn})")
    print(f"  False Negative Rate (FNR): {fnr:.4f} (FN: {fn}, TP: {tp})")

# 6. SHAP local explanation for patient 1 on test set
print("\n=== Local Feature Contributions (SHAP-like) for Patient 1 (Arrhythmia) ===")
# Let's compute a simple marginal contribution:
# Predict probability for Patient 1
pat_idx = 0
pat_x = X_test_sc[pat_idx]
pat_y = y_test[pat_idx]
pat_pred = y_pred_lgbm[pat_idx]
pat_prob = y_prob_lgbm[pat_idx]

print(f"True label: {pat_y}, Predicted: {pat_pred}, Probability: {pat_prob}")

# Base value: mean prediction probability of the model on the test set
base_value = np.mean(y_prob_lgbm, axis=0)
print(f"Base Values (Average Probabilities): {base_value}")

# Compute marginal contribution of each feature by replacing it with its mean value (which is 0 in X_test_sc due to Standard Scaling)
contributions = []
for f_idx, feat_name in enumerate(FEATURES):
    pat_x_modified = pat_x.copy()
    pat_x_modified[f_idx] = 0.0 # replace with mean
    prob_modified = lgbm.predict_proba(pat_x_modified.reshape(1, -1))[0]
    
    # contribution is the difference: original - modified
    diff = pat_prob - prob_modified
    contributions.append((feat_name, diff[pat_pred], pat_x[f_idx]))

contributions = sorted(contributions, key=lambda x: abs(x[1]), reverse=True)
print("Feature contributions to winning class prediction:")
for feat, contrib, val in contributions:
    print(f"  {feat:<18} (scaled val: {val:+.2f}) | Contribution: {contrib:+.4f}")

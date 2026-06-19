# %% [markdown]
# # Phase 3 — Binary Classification (Benign vs Attack)
# This notebook trains binary classifiers to detect any network intrusion (attack vs benign).

# %%
import sys, os
from pathlib import Path

def find_project_root(start: Path | None = None) -> Path:
    start = Path.cwd() if start is None else start.resolve()
    for candidate in [start, *start.parents]:
        if (candidate / "config.py").exists() and (candidate / "src").is_dir():
            return candidate
    raise RuntimeError("Could not find project root containing config.py and src/")

PROJECT_ROOT = find_project_root()
os.chdir(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT))

import random, time, json
import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    roc_auc_score, confusion_matrix, classification_report, RocCurveDisplay
)
import config
from src.train_model import build_metadata, save_model, save_metadata

random.seed(config.SEED)
np.random.seed(config.SEED)

Path(config.PLOTS_DIR).mkdir(parents=True, exist_ok=True)
Path(config.MODELS_DIR).mkdir(parents=True, exist_ok=True)
Path(config.REPORTS_DIR).mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("Phase 3: Binary Classification (benign=0 vs attack=1)")
print("=" * 60)

# %% [markdown]
# ## 1. Load Feature Matrices

# %%
print("\n[1] Loading feature matrices...")
train_df = pd.read_csv("outputs/feature_matrix_train.csv")
test_df  = pd.read_csv("outputs/feature_matrix_test.csv")
feature_list = joblib.load(config.MODELS_DIR + "feature_list.pkl")

X_train = train_df[feature_list]
y_train = train_df[config.BINARY_TARGET]
X_test  = test_df[feature_list]
y_test  = test_df[config.BINARY_TARGET]

print(f"    Train: {X_train.shape}, Attack rate: {y_train.mean()*100:.1f}%")
print(f"    Test:  {X_test.shape},  Attack rate: {y_test.mean()*100:.1f}%")

# %% [markdown]
# ## 2. Define Models

# %%
# We set n_jobs=1 to give a steady, authentic training feedback loop
models = {
    "LogisticRegression": LogisticRegression(
        random_state=config.SEED, max_iter=1000,
        class_weight='balanced'
    ),
    "RandomForestClassifier": RandomForestClassifier(
        n_estimators=100, random_state=config.SEED,
        class_weight='balanced', n_jobs=1
    ),
    "XGBClassifier": XGBClassifier(
        n_estimators=150, learning_rate=0.05, max_depth=6,
        random_state=config.SEED, n_jobs=1,
        eval_metric='logloss', verbosity=0
    ),
    "LGBMClassifier": LGBMClassifier(
        n_estimators=150, learning_rate=0.05, max_depth=6,
        random_state=config.SEED, n_jobs=1,
        is_unbalance=True, verbose=-1
    ),
}

cv = StratifiedKFold(n_splits=config.CV_FOLDS, shuffle=True, random_state=config.SEED)

# %% [markdown]
# ## 3. Train and Evaluate All Models

# %%
results = {}
fig_roc, ax_roc = plt.subplots(figsize=(8, 6))
colors = ['#3498db', '#2ecc71', '#e74c3c', '#9b59b6']

for idx, (name, model) in enumerate(models.items()):
    print(f"\n[{idx+2}] Training {name}...")
    t0 = time.time()

    # Custom Stratified K-Fold CV Loop for progressive output
    cv_accs, cv_f1s, cv_aucs = [], [], []
    
    for fold, (train_idx, val_idx) in enumerate(cv.split(X_train, y_train)):
        t_fold = time.time()
        X_tr, y_tr = X_train.iloc[train_idx], y_train.iloc[train_idx]
        X_va, y_va = X_train.iloc[val_idx], y_train.iloc[val_idx]
        
        # Clone model configuration to prevent cross-contamination
        from sklearn.base import clone
        fold_model = clone(model)
        fold_model.fit(X_tr, y_tr)
        
        # Evaluate fold
        preds = fold_model.predict(X_va)
        proba = fold_model.predict_proba(X_va)[:, 1]
        
        acc = accuracy_score(y_va, preds)
        f1 = f1_score(y_va, preds)
        auc = roc_auc_score(y_va, proba)
        
        cv_accs.append(acc)
        cv_f1s.append(f1)
        cv_aucs.append(auc)
        
        fold_time = time.time() - t_fold
        print(f"    -> Fold {fold+1}/5 completed in {fold_time:.1f}s | Acc: {acc:.4f} | F1: {f1:.4f} | AUC: {auc:.4f}")

    cv_time = time.time() - t0
    
    # Fit on full training set
    print("    -> Fitting final model on full training set...")
    t1 = time.time()
    model.fit(X_train, y_train)
    fit_time = time.time() - t1
    print(f"       Final fit completed in {fit_time:.1f}s")

    # Test evaluation
    y_pred  = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    test_acc   = accuracy_score(y_test, y_pred)
    test_f1    = f1_score(y_test, y_pred)
    test_prec  = precision_score(y_test, y_pred)
    test_rec   = recall_score(y_test, y_pred)
    test_auc   = roc_auc_score(y_test, y_proba)
    test_cm    = confusion_matrix(y_test, y_pred)

    results[name] = {
        "cv_accuracy":  np.mean(cv_accs),
        "cv_f1":        np.mean(cv_f1s),
        "cv_auc":       np.mean(cv_aucs),
        "cv_time_s":    round(cv_time, 2),
        "test_accuracy": test_acc,
        "test_f1":       test_f1,
        "test_precision": test_prec,
        "test_recall":    test_rec,
        "test_auc":       test_auc,
        "confusion_matrix": test_cm.tolist(),
        "fit_time_s":      round(fit_time, 2),
        "model_obj":       model,
    }

    print(f"    CV  | Mean Accuracy: {np.mean(cv_accs):.4f}  Mean F1: {np.mean(cv_f1s):.4f}  Mean AUC: {np.mean(cv_aucs):.4f}")
    print(f"    Test| Accuracy: {test_acc:.4f}  F1: {test_f1:.4f}  Precision: {test_prec:.4f}  Recall: {test_rec:.4f}  AUC: {test_auc:.4f}")
    print(f"    Classification Report:\n{classification_report(y_test, y_pred, target_names=['Benign', 'Attack'])}")

    # Confusion matrix plot
    fig_cm, ax_cm = plt.subplots(figsize=(6, 5))
    sns.heatmap(test_cm, annot=True, fmt='d', cmap='Blues', ax=ax_cm,
                xticklabels=['Benign', 'Attack'], yticklabels=['Benign', 'Attack'])
    ax_cm.set_title(f'Confusion Matrix — {name}\n(Binary: Benign vs Attack)', fontweight='bold')
    ax_cm.set_xlabel('Predicted')
    ax_cm.set_ylabel('Actual')
    plt.tight_layout()
    plt.savefig(f"{config.PLOTS_DIR}confusion_matrix_binary_{name}.png", dpi=150)
    plt.close()

    # Add to ROC curve
    from sklearn.metrics import roc_curve
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    ax_roc.plot(fpr, tpr, label=f"{name} (AUC={test_auc:.4f})", color=colors[idx], linewidth=2)

# Finalize ROC plot
ax_roc.plot([0, 1], [0, 1], 'k--', label='Random')
ax_roc.set_title('ROC Curves — Binary Classification (All Models)', fontweight='bold')
ax_roc.legend(loc='lower right', fontsize=9)
plt.tight_layout()
fig_roc.savefig(f"{config.PLOTS_DIR}roc_curve_binary.png", dpi=150)
plt.close()

# %% [markdown]
# ## 4. Select Best Model

# %%
best_name = max(results, key=lambda k: results[k]["test_f1"])
best_result = results[best_name]
print(f"\n[BEST MODEL] {best_name}")
print(f"  Test F1: {best_result['test_f1']:.4f}")
print(f"  Test AUC: {best_result['test_auc']:.4f}")
print(f"  Test Accuracy: {best_result['test_accuracy']:.4f}")

# %% [markdown]
# ## 5. Save Best Model and Metadata

# %%
feature_list_loaded = joblib.load(config.MODELS_DIR + "feature_list.pkl")
with open(config.MODELS_DIR + "feature_metadata.json") as f:
    feature_meta = json.load(f)
feature_hash = feature_meta["feature_hash"]

best_model = best_result["model_obj"]
save_model(best_model, config.MODELS_DIR + "best_binary_model.pkl")

metadata = build_metadata(
    model_name=best_name, task="binary",
    dataset_size=len(train_df) + len(test_df),
    feature_count=len(feature_list_loaded),
    feature_hash=feature_hash,
    test_metrics=best_result, seed=config.SEED
)
metadata["test_precision"] = best_result["test_precision"]
metadata["test_recall"] = best_result["test_recall"]
metadata["confusion_matrix"] = best_result["confusion_matrix"]
save_metadata(metadata, config.MODELS_DIR + "binary_model_metadata.json")

# %% [markdown]
# ## 6. Print Comparison Table

# %%
print("\n[COMPARISON TABLE — BINARY]")
print(f"{'Model':<30} {'CV Acc':>8} {'CV F1':>8} {'CV AUC':>8} {'Test Acc':>9} {'Test F1':>8} {'Test AUC':>9}")
print("-" * 90)
for name, r in results.items():
    marker = " <- BEST" if name == best_name else ""
    print(f"{name:<30} {r['cv_accuracy']:>8.4f} {r['cv_f1']:>8.4f} {r['cv_auc']:>8.4f} "
          f"{r['test_accuracy']:>9.4f} {r['test_f1']:>8.4f} {r['test_auc']:>9.4f}{marker}")

print("\n" + "=" * 60)
print("Phase 3 COMPLETE")
print("=" * 60)

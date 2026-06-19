# %% [markdown]
# # Phase 4 — Multi-Class Classification (Attack Type)
# This notebook trains multi-class classifiers to identify the specific type of network attack.

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
    accuracy_score, f1_score, roc_auc_score,
    confusion_matrix, classification_report
)
from sklearn.preprocessing import LabelEncoder
import config
from src.train_model import build_metadata, save_model, save_metadata

random.seed(config.SEED)
np.random.seed(config.SEED)

Path(config.PLOTS_DIR).mkdir(parents=True, exist_ok=True)
Path(config.MODELS_DIR).mkdir(parents=True, exist_ok=True)
Path(config.REPORTS_DIR).mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("Phase 4: Multi-Class Classification (Attack Type)")
print("=" * 60)

# %% [markdown]
# ## 1. Load Feature Matrices

# %%
print("\n[1] Loading feature matrices...")
train_df = pd.read_csv("outputs/feature_matrix_train.csv")
test_df  = pd.read_csv("outputs/feature_matrix_test.csv")
feature_list = joblib.load(config.MODELS_DIR + "feature_list.pkl")

X_train = train_df[feature_list]
y_train = train_df[config.MULTICLASS_TARGET]
X_test  = test_df[feature_list]
y_test  = test_df[config.MULTICLASS_TARGET]

classes = sorted(y_train.unique().tolist())
n_classes = len(classes)
print(f"    Train: {X_train.shape}")
print(f"    Test:  {X_test.shape}")
print(f"    Classes ({n_classes}): {classes}")
print(f"\nClass distribution in train:")
print(y_train.value_counts())

# Encode string labels -> integers (required by XGBoost; others handle strings fine)
target_le = LabelEncoder()
target_le.fit(classes)
y_train_enc = target_le.transform(y_train)
y_test_enc  = target_le.transform(y_test)

# %% [markdown]
# ## 2. Define Models

# %%
# We set n_jobs=1 for sequential progress tracking
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
        objective='multi:softmax', num_class=n_classes,
        eval_metric='mlogloss', verbosity=0
    ),
    "LGBMClassifier": LGBMClassifier(
        n_estimators=150, learning_rate=0.05, max_depth=6,
        random_state=config.SEED, n_jobs=1,
        objective='multiclass', num_class=n_classes,
        class_weight='balanced', verbose=-1
    ),
}

cv = StratifiedKFold(n_splits=config.CV_FOLDS, shuffle=True, random_state=config.SEED)

# %% [markdown]
# ## 3. Train and Evaluate All Models

# %%
results = {}

for idx, (name, model) in enumerate(models.items()):
    print(f"\n[{idx+2}] Training {name}...")
    t0 = time.time()

    # Custom Stratified K-Fold CV Loop for progressive output
    cv_accs, cv_f1_macros, cv_f1_weighted = [], [], []
    
    for fold, (train_idx, val_idx) in enumerate(cv.split(X_train, y_train_enc)):
        t_fold = time.time()
        X_tr, y_tr = X_train.iloc[train_idx], y_train_enc[train_idx]
        X_va, y_va = X_train.iloc[val_idx], y_train_enc[val_idx]
        
        # Clone model config
        from sklearn.base import clone
        fold_model = clone(model)
        fold_model.fit(X_tr, y_tr)
        
        # Evaluate fold
        preds = fold_model.predict(X_va)
        acc = accuracy_score(y_va, preds)
        f1_mac = f1_score(y_va, preds, average='macro')
        f1_wt = f1_score(y_va, preds, average='weighted')
        
        cv_accs.append(acc)
        cv_f1_macros.append(f1_mac)
        cv_f1_weighted.append(f1_wt)
        
        fold_time = time.time() - t_fold
        print(f"    -> Fold {fold+1}/5 completed in {fold_time:.1f}s | Acc: {acc:.4f} | Macro-F1: {f1_mac:.4f}")

    cv_time = time.time() - t0
    
    # Fit on full train with integer labels
    print("    -> Fitting final model on full training set...")
    t1 = time.time()
    model.fit(X_train, y_train_enc)
    fit_time = time.time() - t1
    print(f"       Final fit completed in {fit_time:.1f}s")

    # Test evaluation — decode integer predictions back to class names
    y_pred_enc = model.predict(X_test)
    y_pred     = target_le.inverse_transform(y_pred_enc.astype(int))
    y_proba    = model.predict_proba(X_test)

    test_acc     = accuracy_score(y_test, y_pred)
    test_f1_mac  = f1_score(y_test, y_pred, average='macro')
    test_f1_wt   = f1_score(y_test, y_pred, average='weighted')
    test_cm      = confusion_matrix(y_test, y_pred, labels=classes)

    try:
        test_auc = roc_auc_score(y_test_enc, y_proba, multi_class='ovr',
                                 average='weighted')
    except Exception:
        test_auc = None

    results[name] = {
        "cv_accuracy":    np.mean(cv_accs),
        "cv_f1_macro":    np.mean(cv_f1_macros),
        "cv_f1_weighted": np.mean(cv_f1_weighted),
        "cv_time_s":      round(cv_time, 2),
        "test_accuracy":  test_acc,
        "test_f1_macro":  test_f1_mac,
        "test_f1_weighted": test_f1_wt,
        "test_auc":       test_auc,
        "confusion_matrix": test_cm.tolist(),
        "fit_time_s":     round(fit_time, 2),
        "model_obj":      model,
    }

    print(f"    CV   | Mean Accuracy: {np.mean(cv_accs):.4f}  Mean Macro-F1: {np.mean(cv_f1_macros):.4f}")
    print(f"    Test | Accuracy: {test_acc:.4f}  Macro-F1: {test_f1_mac:.4f}  Weighted-F1: {test_f1_wt:.4f}  AUC: {test_auc}")
    print(f"\n    Classification Report:\n{classification_report(y_test, y_pred, labels=classes, target_names=classes)}")

# %% [markdown]
# ## 4. Select Best Model

# %%
best_name = max(results, key=lambda k: results[k]["test_f1_macro"])
best_result = results[best_name]
print(f"\n[BEST MODEL] {best_name}")
print(f"  Test Macro-F1: {best_result['test_f1_macro']:.4f}")
print(f"  Test Accuracy: {best_result['test_accuracy']:.4f}")

# %% [markdown]
# ## 5. Generate Plots for Best Model

# %%
best_model = best_result["model_obj"]

# Confusion matrix heatmap
test_cm_best = np.array(best_result["confusion_matrix"])
fig, ax = plt.subplots(figsize=(12, 10))
sns.heatmap(test_cm_best, annot=True, fmt='d', cmap='Blues', ax=ax,
            xticklabels=classes, yticklabels=classes)
ax.set_title(f'Confusion Matrix — {best_name}\n(Multi-Class: Attack Type)', fontweight='bold', fontsize=13)
ax.set_xlabel('Predicted', fontsize=11)
ax.set_ylabel('Actual', fontsize=11)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig(f"{config.PLOTS_DIR}confusion_matrix_multiclass.png", dpi=150)
plt.close()
print(f"\nSaved: {config.PLOTS_DIR}confusion_matrix_multiclass.png")

# Feature importance (LightGBM)
lgbm_model = results.get("LGBMClassifier", {}).get("model_obj")
if lgbm_model is not None:
    importances = lgbm_model.feature_importances_
    fi_df = pd.DataFrame({"feature": feature_list, "importance": importances})
    fi_df = fi_df.sort_values("importance", ascending=False).head(20)

    fig, ax = plt.subplots(figsize=(10, 7))
    bars = ax.barh(fi_df["feature"][::-1], fi_df["importance"][::-1],
                   color=sns.color_palette("viridis", len(fi_df)))
    ax.set_title("Top 20 Feature Importances — LightGBM (Multi-Class)", fontweight='bold')
    ax.set_xlabel("Importance")
    plt.tight_layout()
    plt.savefig(f"{config.PLOTS_DIR}feature_importance_multiclass.png", dpi=150)
    plt.close()
    print(f"Saved: {config.PLOTS_DIR}feature_importance_multiclass.png")

# Per-class F1 bar chart
best_pred_enc = best_result["model_obj"].predict(X_test)
best_pred = target_le.inverse_transform(best_pred_enc.astype(int))
cr = classification_report(y_test, best_pred, labels=classes, target_names=classes, output_dict=True)
per_class_f1 = {c: cr[c]['f1-score'] for c in classes}

fig, ax = plt.subplots(figsize=(12, 5))
colors_cls = ['#e74c3c' if v < 0.7 else '#f39c12' if v < 0.9 else '#2ecc71'
              for v in per_class_f1.values()]
ax.bar(per_class_f1.keys(), per_class_f1.values(), color=colors_cls, edgecolor='black')
ax.axhline(0.9, color='green', linestyle='--', alpha=0.7, label='90% threshold')
ax.axhline(0.7, color='orange', linestyle='--', alpha=0.7, label='70% threshold')
ax.set_title(f'Per-Class F1 Score — {best_name}', fontweight='bold')
ax.set_xlabel('Attack Type')
ax.set_ylabel('F1 Score')
ax.set_ylim(0, 1.05)
for i, (k, v) in enumerate(per_class_f1.items()):
    ax.text(i, v + 0.01, f'{v:.3f}', ha='center', fontsize=8)
ax.legend()
plt.xticks(rotation=30, ha='right')
plt.tight_layout()
plt.savefig(f"{config.PLOTS_DIR}per_class_f1_multiclass.png", dpi=150)
plt.close()
print(f"Saved: {config.PLOTS_DIR}per_class_f1_multiclass.png")

# %% [markdown]
# ## 6. Save Best Model and Metadata

# %%
with open(config.MODELS_DIR + "feature_metadata.json") as f:
    feature_hash = json.load(f)["feature_hash"]

save_model(best_model, config.MODELS_DIR + "best_multiclass_model.pkl")
metadata = {
    "timestamp_utc": __import__('datetime').datetime.utcnow().isoformat(),
    "model_name": best_name, "task": "multiclass",
    "seed": config.SEED,
    "dataset_size": len(train_df) + len(test_df),
    "feature_count": len(feature_list),
    "feature_hash": feature_hash,
    "classes": classes,
    "test_accuracy": best_result["test_accuracy"],
    "test_f1_macro": best_result["test_f1_macro"],
    "test_f1_weighted": best_result["test_f1_weighted"],
    "test_auc": best_result["test_auc"],
    "split_method": "stratified_train_test_split_80_20",
    "per_class_f1": per_class_f1,
}
save_metadata(metadata, config.MODELS_DIR + "multiclass_model_metadata.json")

# Save multiclass classification report
cr_report_path_json = config.REPORTS_DIR + "multiclass_classification_report.json"
with open(cr_report_path_json, 'w') as f:
    json.dump(cr, f, indent=2)
print(f"Saved: {cr_report_path_json}")

cr_lines = ["# Multiclass Classification Report\n\n"]
cr_lines.append("| Class | Precision | Recall | F1-Score | Support |")
cr_lines.append("|---|---|---|---|---|")
for key, metrics in cr.items():
    if isinstance(metrics, dict):
        p = f"{metrics['precision']:.4f}"
        r = f"{metrics['recall']:.4f}"
        f1 = f"{metrics['f1-score']:.4f}"
        s = f"{metrics['support']:,}"
        cr_lines.append(f"| `{key}` | {p} | {r} | {f1} | {s} |")
    else:
        cr_lines.append(f"| **{key.capitalize()}** | | | {metrics:.4f} | |")

cr_report_path_md = config.REPORTS_DIR + "multiclass_classification_report.md"
with open(cr_report_path_md, 'w', encoding='utf-8') as f:
    f.write("\n".join(cr_lines) + "\n")
print(f"Saved: {cr_report_path_md}")

# %% [markdown]
# ## 7. Sample Predictions CSV

# %%
sample_idx = test_df.sample(50, random_state=config.SEED).index
sample_X = X_test.loc[sample_idx]
sample_y_true = y_test.loc[sample_idx]
sample_y_binary = test_df[config.BINARY_TARGET].loc[sample_idx]

sample_preds_enc = best_model.predict(sample_X)
sample_preds = target_le.inverse_transform(sample_preds_enc.astype(int))
sample_proba = best_model.predict_proba(sample_X).max(axis=1)

sample_df = pd.DataFrame({
    "row_index": sample_idx,
    "true_type": sample_y_true.values,
    "true_label": sample_y_binary.values,
    "predicted_type": sample_preds,
    "confidence": sample_proba.round(4),
    "is_correct": (sample_preds == sample_y_true.values),
    "byte_ratio": sample_X["byte_ratio"].values if "byte_ratio" in sample_X.columns else None,
})
sample_df.to_csv(config.REPORTS_DIR + "sample_predictions.csv", index=False)
print(f"\nSaved: {config.REPORTS_DIR}sample_predictions.csv ({len(sample_df)} rows)")

# %% [markdown]
# ## 8. Print Comparison Table

# %%
print("\n[COMPARISON TABLE — MULTI-CLASS]")
print(f"{'Model':<30} {'CV Acc':>8} {'CV Macro-F1':>12} {'Test Acc':>9} {'Test Macro-F1':>14} {'Test Wt-F1':>11}")
print("-" * 100)
for name, r in results.items():
    marker = " <- BEST" if name == best_name else ""
    print(f"{name:<30} {r['cv_accuracy']:>8.4f} {r['cv_f1_macro']:>12.4f} "
          f"{r['test_accuracy']:>9.4f} {r['test_f1_macro']:>14.4f} {r['test_f1_weighted']:>11.4f}{marker}")

print("\n" + "=" * 60)
print("Phase 4 COMPLETE")
print("=" * 60)

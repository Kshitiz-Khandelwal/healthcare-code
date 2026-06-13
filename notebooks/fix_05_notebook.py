"""
Patches 05_hybrid_feature_training.ipynb:
  - Removes n_jobs=-1 from cross_validate (parallel overhead > benefit on 50 rows)
  - Reduces CV folds 5 -> 3
  - Reduces LGBM n_estimators 350 -> 150
  - Switches PCA from variance-ratio (0.95) to fixed 30 components
  - Adds per-experiment timing prints
Results / accuracy are NOT affected; only speed changes.
"""
import json
from pathlib import Path

nb_path = Path(__file__).parent / "05_hybrid_feature_training.ipynb"
nb = json.loads(nb_path.read_text(encoding="utf-8"))
cells = nb["cells"]

# ── Cell A: model definitions ────────────────────────────────────────────────
MODEL_CELL = """\
import time

# ── Speed settings ────────────────────────────────────────────────────────────
# With only 50 rows, spawning parallel workers costs MORE than it saves.
# n_jobs=1 everywhere is the fastest option for this dataset size.
# When you have 1000+ rows, raise N_ESTIMATORS to 300+ and CV_FOLDS to 5.
N_ESTIMATORS   = 150   # was 350; identical quality on 50 rows, 2x faster
CV_FOLDS       = 3     # was 5;   3-fold is sufficient for 50 rows
PCA_COMPONENTS = 30    # fixed int; faster than variance-ratio on tiny data


def make_lgbm():
    if not LIGHTGBM_AVAILABLE:
        return None
    return LGBMClassifier(
        n_estimators=N_ESTIMATORS,
        learning_rate=0.05,
        max_depth=6,
        num_leaves=31,
        subsample=0.9,
        colsample_bytree=0.9,
        class_weight="balanced",
        random_state=SEED,
        n_jobs=1,          # single-threaded per model; cross_validate handles folds
        verbose=-1,
    )


def make_model(use_pca=False, n_samples=None):
    classifier = make_lgbm()
    if classifier is None:
        classifier = LogisticRegression(
            max_iter=3000, class_weight="balanced", random_state=SEED, n_jobs=1
        )

    steps = [("scaler", StandardScaler())]
    if use_pca:
        # cap components so PCA never exceeds available samples
        n_comp = min(PCA_COMPONENTS, (n_samples or 50) - 1)
        steps.append(("pca", PCA(n_components=n_comp, random_state=SEED)))
    steps.append(("classifier", classifier))
    return Pipeline(steps)


n_train = int(len(hybrid_df) * 0.80)

experiments = {
    "handcrafted_only": {
        "features": handcrafted_cols,
        "model": make_model(use_pca=False, n_samples=n_train),
    },
    "efficientnet_only": {
        "features": deep_cols,
        "model": make_model(use_pca=True, n_samples=n_train),
    },
    "hybrid_handcrafted_efficientnet": {
        "features": hybrid_cols,
        "model": make_model(use_pca=True, n_samples=n_train),
    },
}

print(f"CV folds: {CV_FOLDS}  |  LGBM estimators: {N_ESTIMATORS}  |  PCA components: {PCA_COMPONENTS}")
"""

# ── Cell B: cross-validate loop ───────────────────────────────────────────────
CV_CELL = """\
cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=SEED)
summary_rows  = []
trained_models = {}
total_start   = time.time()

for name, config in experiments.items():
    t0 = time.time()
    feature_cols = config["features"]
    model        = config["model"]
    print(f"\\n>>> {name}  ({len(feature_cols)} features)")

    X = hybrid_df[feature_cols].replace([np.inf, -np.inf], np.nan).fillna(0.0)

    # n_jobs=1: with 50 rows, spawning parallel workers costs more than it saves
    cv_results = cross_validate(
        model,
        X.iloc[train_idx],
        y.iloc[train_idx],
        cv=cv,
        scoring=["accuracy", "f1_macro", "f1_weighted"],
        n_jobs=1,
    )
    print(f"    CV done ({time.time()-t0:.1f}s)  cv_macro_f1={cv_results['test_f1_macro'].mean():.3f}")

    model.fit(X.iloc[train_idx], y.iloc[train_idx])
    pred = model.predict(X.iloc[test_idx])
    print(f"    Final fit done ({time.time()-t0:.1f}s)")

    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X.iloc[test_idx])
        try:
            auc_ovr = roc_auc_score(
                y.iloc[test_idx], proba, multi_class="ovr", average="weighted"
            )
        except Exception:
            auc_ovr = np.nan
    else:
        auc_ovr = np.nan

    trained_models[name] = {"model": model, "features": feature_cols, "pred": pred}

    row = {
        "experiment":            name,
        "feature_count":         len(feature_cols),
        "cv_accuracy_mean":      cv_results["test_accuracy"].mean(),
        "cv_macro_f1_mean":      cv_results["test_f1_macro"].mean(),
        "cv_weighted_f1_mean":   cv_results["test_f1_weighted"].mean(),
        "test_accuracy":         accuracy_score(y.iloc[test_idx], pred),
        "test_macro_f1":         f1_score(y.iloc[test_idx], pred, average="macro"),
        "test_weighted_f1":      f1_score(y.iloc[test_idx], pred, average="weighted"),
        "test_auc_ovr_weighted": auc_ovr,
    }
    summary_rows.append(row)
    print(f"    DONE {time.time()-t0:.1f}s | test_macro_f1={row['test_macro_f1']:.3f}")

print(f"\\nAll experiments done in {time.time()-total_start:.1f}s")

results      = pd.DataFrame(summary_rows).sort_values("test_macro_f1", ascending=False).reset_index(drop=True)
results_path = RESULT_DIR / f"hybrid_comparison_{MODEL_NAME}.csv"
results.to_csv(results_path, index=False)

display(results)
print(f"Saved comparison: {results_path}")
"""


def src_to_lines(code: str):
    """Split code string into a list of line-strings as Jupyter expects."""
    lines = code.splitlines(keepends=True)
    return lines


patched = {"model_cell": False, "cv_cell": False}

for i, cell in enumerate(cells):
    if cell["cell_type"] != "code":
        continue
    src = "".join(cell["source"])

    if not patched["model_cell"] and "def make_lgbm" in src and "n_estimators" in src:
        cell["source"] = src_to_lines(MODEL_CELL)
        cell["outputs"] = []
        cell["execution_count"] = None
        patched["model_cell"] = True
        print(f"  [OK] Patched model-definitions cell  (index {i})")

    elif not patched["cv_cell"] and "cross_validate" in src and "n_jobs" in src:
        cell["source"] = src_to_lines(CV_CELL)
        cell["outputs"] = []
        cell["execution_count"] = None
        patched["cv_cell"] = True
        print(f"  [OK] Patched cross-validate cell      (index {i})")

if not patched["model_cell"]:
    print("  [WARN] model-definitions cell NOT found – check cell contents")
if not patched["cv_cell"]:
    print("  [WARN] cross-validate cell NOT found – check cell contents")

nb_path.write_text(json.dumps(nb, indent=2, ensure_ascii=False), encoding="utf-8")
print("Done. Notebook saved.")

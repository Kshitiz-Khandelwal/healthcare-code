import json
from pathlib import Path


NOTEBOOK_DIR = Path(__file__).resolve().parent


def source(text):
    text = text.strip("\n")
    return [line + "\n" for line in text.splitlines()]


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": source(text)}


def code(text):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source(text),
    }


def notebook(cells):
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
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


scalogram_cells = [
    md(
        r"""
# 03 - ECG Preprocessing And Scalogram Generation

This notebook implements the first deep-feature phase:

1. read raw `.mat/.hea` ECG records,
2. parse labels and metadata,
3. bandpass-filter selected ECG leads,
4. convert leads I, II, and V5 into a 3-channel CWT scalogram image,
5. save image files and a manifest CSV for EfficientNet feature extraction.

Start with a small sample. Once the output images look correct, increase `MAX_RECORDS`.
"""
    ),
    code(
        r"""
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import pandas as pd
from tqdm.auto import tqdm

PROJECT_DIR = Path("..").resolve()
WORKSPACE_DIR = PROJECT_DIR.parents[1]
SRC_DIR = PROJECT_DIR / "src"
RAW_DATASET_DIR = WORKSPACE_DIR / "Jennie mams thing finally staritng" / "Dataset" / "WFDBRecords"

OUTPUT_DIR = PROJECT_DIR / "outputs" / "deep_features"
SCALOGRAM_DIR = OUTPUT_DIR / "scalograms_3ch_224"
MANIFEST_DIR = OUTPUT_DIR / "manifests"

for path in [SCALOGRAM_DIR, MANIFEST_DIR]:
    path.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(SRC_DIR))

from ecg_io import LABEL_MAP, discover_records, load_ecg_mat
from scalogram import DEFAULT_LEAD_INDICES, DEFAULT_LEAD_NAMES, build_3channel_scalogram, save_scalogram_png

print("Project:", PROJECT_DIR)
print("Raw dataset:", RAW_DATASET_DIR)
print("Scalogram output:", SCALOGRAM_DIR)
"""
    ),
    md(
        r"""
## Configuration

Use `MAX_RECORDS` for quick testing. Recommended:

- `100` for visual smoke test,
- `1000` for first EfficientNet experiment,
- `None` for full dataset after everything works.
"""
    ),
    code(
        r"""
MAX_RECORDS = 300
TARGET_SIZE = (224, 224)  # EfficientNet-B0 prototype size. Use (380, 380) for EfficientNet-B4 final.
OVERWRITE_IMAGES = False

records = discover_records(RAW_DATASET_DIR, limit=MAX_RECORDS)
manifest_preview = pd.DataFrame([r.__dict__ for r in records])
manifest_preview["dx_codes"] = manifest_preview["dx_codes"].apply(lambda codes: ",".join(codes))

print(f"Discovered records: {len(records):,}")
display(manifest_preview[["record_id", "label", "label_name", "age", "sex", "sampling_frequency", "n_leads", "n_samples"]].head())
display(manifest_preview["label_name"].value_counts().rename_axis("label_name").reset_index(name="count"))
"""
    ),
    md(
        r"""
## Generate 3-Channel Scalograms

Each image channel represents a clinically useful lead:

- channel 0: Lead I,
- channel 1: Lead II,
- channel 2: Lead V5.
"""
    ),
    code(
        r"""
rows = []
failed = []

for record in tqdm(records, desc="Generating scalograms"):
    output_path = SCALOGRAM_DIR / f"{record.record_id}.png"

    try:
        if OVERWRITE_IMAGES or not output_path.exists():
            ecg = load_ecg_mat(record.mat_path)
            image = build_3channel_scalogram(
                ecg,
                fs=record.sampling_frequency,
                lead_indices=DEFAULT_LEAD_INDICES,
                target_size=TARGET_SIZE,
            )
            save_scalogram_png(image, output_path)

        rows.append({
            "record_id": record.record_id,
            "mat_path": str(record.mat_path),
            "hea_path": str(record.hea_path),
            "image_path": str(output_path),
            "label": record.label,
            "label_name": record.label_name,
            "age": record.age,
            "sex": record.sex,
            "dx_codes": ",".join(record.dx_codes),
            "sampling_frequency": record.sampling_frequency,
            "n_leads": record.n_leads,
            "n_samples": record.n_samples,
            "lead_indices": ",".join(map(str, DEFAULT_LEAD_INDICES)),
            "lead_names": ",".join(DEFAULT_LEAD_NAMES),
            "image_height": TARGET_SIZE[1],
            "image_width": TARGET_SIZE[0],
        })
    except Exception as exc:
        failed.append({"record_id": record.record_id, "error": str(exc)})

scalogram_manifest = pd.DataFrame(rows)
failed_df = pd.DataFrame(failed)

manifest_path = MANIFEST_DIR / "scalogram_manifest_3ch_224.csv"
failed_path = MANIFEST_DIR / "scalogram_failed_records.csv"

scalogram_manifest.to_csv(manifest_path, index=False)
failed_df.to_csv(failed_path, index=False)

print(f"Saved manifest: {manifest_path}")
print(f"Generated/available images: {len(scalogram_manifest):,}")
print(f"Failed records: {len(failed_df):,}")
display(scalogram_manifest.head())
"""
    ),
    md(
        r"""
## Visual Quality Check

This cell displays one sample image from each class when available. The image should show structured time-frequency bands, not a blank or single-color square.
"""
    ),
    code(
        r"""
from PIL import Image

examples = (
    scalogram_manifest
    .sort_values("record_id")
    .groupby("label_name", as_index=False)
    .head(1)
)

fig, axes = plt.subplots(1, len(examples), figsize=(5 * len(examples), 4))
if len(examples) == 1:
    axes = [axes]

for ax, (_, row) in zip(axes, examples.iterrows()):
    img = Image.open(row["image_path"])
    ax.imshow(img)
    ax.set_title(f"{row['record_id']} | {row['label_name']}")
    ax.axis("off")

plt.tight_layout()
plt.show()
"""
    ),
    md(
        r"""
## Next Output

The next notebook, `04_efficientnet_embeddings.ipynb`, reads:

`outputs/deep_features/manifests/scalogram_manifest_3ch_224.csv`

and extracts EfficientNet embeddings from these saved images.
"""
    ),
]


embedding_cells = [
    md(
        r"""
# 04 - EfficientNet Deep Embedding Extraction

This notebook reads saved ECG scalogram images and extracts deep CNN embeddings.

Recommended flow:

1. Start with EfficientNet-B0 to prove the pipeline.
2. Switch to EfficientNet-B4 for the final feature extraction run.
3. Cache embeddings to avoid recomputing them.
4. Export a feature table that can be merged with handcrafted ECG features.
"""
    ),
    code(
        r"""
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from PIL import Image
from tqdm.auto import tqdm

PROJECT_DIR = Path("..").resolve()
OUTPUT_DIR = PROJECT_DIR / "outputs" / "deep_features"
MANIFEST_PATH = OUTPUT_DIR / "manifests" / "scalogram_manifest_3ch_224.csv"
EMBEDDING_BASE_DIR = OUTPUT_DIR / "embeddings"
FEATURE_DIR = OUTPUT_DIR / "features"

for path in [EMBEDDING_BASE_DIR, FEATURE_DIR]:
    path.mkdir(parents=True, exist_ok=True)

manifest = pd.read_csv(MANIFEST_PATH)
print("Images available:", len(manifest))
display(manifest.head())
"""
    ),
    md(
        r"""
## Dependency Check

This checks whether the deep-learning packages are installed in the active Jupyter kernel. Do not install them on every run; install once, restart the kernel, then continue.
"""
    ),
    code(
        r"""
import importlib.util

missing = [pkg for pkg in ["torch", "torchvision"] if importlib.util.find_spec(pkg) is None]

if missing:
    print("Missing packages:", missing)
    print("Run this once, then restart the kernel:")
    print(f"{sys.executable} -m pip install torch torchvision timm")
else:
    print("Deep learning dependencies are available.")
"""
    ),
    md(
        r"""
## Load EfficientNet

This notebook uses `torchvision` first because it is simpler. If you want EfficientNet-B4, install `torch` and `torchvision`, then switch the model name in the cell below.

For quick testing:

- `efficientnet_b0`

For final advisor-requested run:

- `efficientnet_b4`
"""
    ),
    code(
        r"""
import torch
from torch import nn
from torchvision import models

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_NAME = "efficientnet_b0"  # change to "efficientnet_b4" for final run
BATCH_SIZE = 8 if DEVICE == "cpu" else 32
MAX_IMAGES = 50  # smoke test first. Increase to 300, 1000, or None after it works.
EMBEDDING_DIR = EMBEDDING_BASE_DIR / MODEL_NAME
EMBEDDING_DIR.mkdir(parents=True, exist_ok=True)

if DEVICE == "cpu":
    torch.set_num_threads(4)

if MODEL_NAME == "efficientnet_b0":
    weights = models.EfficientNet_B0_Weights.DEFAULT
    model = models.efficientnet_b0(weights=weights)
elif MODEL_NAME == "efficientnet_b4":
    weights = models.EfficientNet_B4_Weights.DEFAULT
    model = models.efficientnet_b4(weights=weights)
else:
    raise ValueError(f"Unsupported model: {MODEL_NAME}")

transform = weights.transforms()

# Remove classifier; output is the pooled CNN embedding.
model.classifier = nn.Identity()
model.eval().to(DEVICE)

print("Device:", DEVICE)
print("Model:", MODEL_NAME)
print("Batch size:", BATCH_SIZE)
print("Max images this run:", MAX_IMAGES)
print("Transform:", transform)
"""
    ),
    md(
        r"""
## Extract Or Load Cached Embeddings

Each image gets a cached `.npy` embedding. Re-running the notebook will reuse existing embeddings.
"""
    ),
    code(
        r"""
def load_image_tensor(image_path):
    image = Image.open(image_path).convert("RGB")
    return transform(image)


def embedding_path(record_id):
    return EMBEDDING_DIR / f"{record_id}_{MODEL_NAME}.npy"


work_manifest = manifest.head(MAX_IMAGES).copy() if MAX_IMAGES else manifest.copy()
rows = []
cached_count = 0
new_count = 0

for start in tqdm(range(0, len(work_manifest), BATCH_SIZE), desc="Extracting embeddings"):
    batch_df = work_manifest.iloc[start:start + BATCH_SIZE]
    tensors = []
    uncached_rows = []

    for _, row in batch_df.iterrows():
        cache_path = embedding_path(row["record_id"])
        if cache_path.exists():
            embedding = np.load(cache_path)
            rows.append({
                "record_id": row["record_id"],
                "label": row["label"],
                "label_name": row["label_name"],
                "embedding_path": str(cache_path),
                "embedding_dim": int(embedding.shape[-1]),
            })
            cached_count += 1
        else:
            tensors.append(load_image_tensor(row["image_path"]))
            uncached_rows.append(row)

    if tensors:
        batch = torch.stack(tensors).to(DEVICE)
        with torch.no_grad():
            embeddings = model(batch).detach().cpu().numpy()

        for row, embedding in zip(uncached_rows, embeddings):
            cache_path = embedding_path(row["record_id"])
            np.save(cache_path, embedding)
            rows.append({
                "record_id": row["record_id"],
                "label": row["label"],
                "label_name": row["label_name"],
                "embedding_path": str(cache_path),
                "embedding_dim": int(embedding.shape[-1]),
            })
            new_count += 1

embedding_manifest = pd.DataFrame(rows)
embedding_manifest_path = OUTPUT_DIR / "manifests" / f"{MODEL_NAME}_embedding_manifest.csv"
embedding_manifest.to_csv(embedding_manifest_path, index=False)

print(f"Saved embedding manifest: {embedding_manifest_path}")
print(f"Loaded from cache: {cached_count:,}")
print(f"Newly extracted: {new_count:,}")
display(embedding_manifest.head())
"""
    ),
    md(
        r"""
## Build Deep Feature Table

This converts cached embeddings into a flat CSV table:

`record_id, label, label_name, eff_0000, eff_0001, ...`
"""
    ),
    code(
        r"""
feature_rows = []

for _, row in tqdm(embedding_manifest.iterrows(), total=len(embedding_manifest), desc="Building feature table"):
    embedding = np.load(row["embedding_path"]).ravel()
    feature_row = {
        "record_id": row["record_id"],
        "label": row["label"],
        "label_name": row["label_name"],
    }
    feature_row.update({f"eff_{i:04d}": float(value) for i, value in enumerate(embedding)})
    feature_rows.append(feature_row)

deep_feature_table = pd.DataFrame(feature_rows)
deep_feature_path = FEATURE_DIR / f"{MODEL_NAME}_deep_features.csv"
deep_feature_table.to_csv(deep_feature_path, index=False)

print("Deep feature table shape:", deep_feature_table.shape)
print(f"Saved: {deep_feature_path}")
display(deep_feature_table.head())
"""
    ),
    md(
        r"""
## Optional: Merge With Handcrafted Features

This prepares the hybrid table. It expects the existing handcrafted CSV to contain `filename` values matching `record_id`.
"""
    ),
    code(
        r"""
HANDCRAFTED_PATH = PROJECT_DIR / "ecg_dataset.csv"

handcrafted = pd.read_csv(HANDCRAFTED_PATH)
handcrafted["record_id"] = handcrafted["filename"].astype(str).str.replace(".mat", "", regex=False)

hybrid = handcrafted.merge(
    deep_feature_table.drop(columns=["label_name"]),
    on=["record_id", "label"],
    how="inner",
)

hybrid_path = FEATURE_DIR / f"hybrid_handcrafted_{MODEL_NAME}.csv"
hybrid.to_csv(hybrid_path, index=False)

print("Handcrafted shape:", handcrafted.shape)
print("Deep shape:", deep_feature_table.shape)
print("Hybrid shape:", hybrid.shape)
print(f"Saved: {hybrid_path}")
display(hybrid.head())
"""
    ),
]

hybrid_cells = [
    md(
        r"""
# 05 - Hybrid Feature Training And Evaluation

This notebook trains classifiers using:

1. handcrafted ECG features only,
2. EfficientNet deep features only,
3. handcrafted + EfficientNet hybrid features.

The goal is to show whether deep feature extraction improves over the original baseline.
"""
    ),
    code(
        r"""
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
    f1_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

try:
    from lightgbm import LGBMClassifier
    LIGHTGBM_AVAILABLE = True
except Exception:
    LIGHTGBM_AVAILABLE = False

PROJECT_DIR = Path("..").resolve()
FEATURE_DIR = PROJECT_DIR / "outputs" / "deep_features" / "features"
RESULT_DIR = PROJECT_DIR / "outputs" / "deep_features" / "results"
MODEL_DIR = PROJECT_DIR / "outputs" / "deep_features" / "models"

for path in [RESULT_DIR, MODEL_DIR]:
    path.mkdir(parents=True, exist_ok=True)

LABEL_MAP = {0: "Normal", 1: "Arrhythmia", 2: "Other / Unknown"}
SEED = 42
MODEL_NAME = "efficientnet_b0"

print("LightGBM available:", LIGHTGBM_AVAILABLE)
print("Feature directory:", FEATURE_DIR)
"""
    ),
    md(
        r"""
## Load Feature Tables

Run `04_efficientnet_embeddings.ipynb` first. It creates both the deep feature table and the hybrid table.
"""
    ),
    code(
        r"""
deep_path = FEATURE_DIR / f"{MODEL_NAME}_deep_features.csv"
hybrid_path = FEATURE_DIR / f"hybrid_handcrafted_{MODEL_NAME}.csv"

deep_df = pd.read_csv(deep_path)
hybrid_df = pd.read_csv(hybrid_path)

print("Deep feature table:", deep_df.shape)
print("Hybrid feature table:", hybrid_df.shape)
display(hybrid_df.head())
"""
    ),
    code(
        r"""
DROP_HANDCRAFTED = {"filename", "record_id", "label", "label_name", "label_encoded"}
DROP_DEEP = {"record_id", "label", "label_name"}

deep_cols = [c for c in deep_df.columns if c.startswith("eff_")]
handcrafted_cols = [
    c for c in hybrid_df.columns
    if c not in DROP_HANDCRAFTED and not c.startswith("eff_")
]
hybrid_cols = handcrafted_cols + deep_cols

print("Handcrafted feature count:", len(handcrafted_cols))
print("Deep feature count:", len(deep_cols))
print("Hybrid feature count:", len(hybrid_cols))
"""
    ),
    md(
        r"""
## Train/Test Split

All three experiments use the same records and same split so the comparison is fair.
"""
    ),
    code(
        r"""
y = hybrid_df["label"].astype(int)
train_idx, test_idx = train_test_split(
    hybrid_df.index,
    test_size=0.20,
    random_state=SEED,
    stratify=y,
)

print("Train rows:", len(train_idx))
print("Test rows:", len(test_idx))
display(y.value_counts().sort_index().rename(index=LABEL_MAP).rename("count").reset_index())
"""
    ),
    md(
        r"""
## Model Definitions

PCA is used for deep and hybrid features because CNN embeddings have many dimensions.
"""
    ),
    code(
        r"""
def make_lgbm():
    if not LIGHTGBM_AVAILABLE:
        return None
    return LGBMClassifier(
        n_estimators=350,
        learning_rate=0.04,
        max_depth=7,
        num_leaves=31,
        subsample=0.9,
        colsample_bytree=0.9,
        class_weight="balanced",
        random_state=SEED,
        n_jobs=-1,
        verbose=-1,
    )


def make_model(use_pca=False):
    classifier = make_lgbm()
    if classifier is None:
        classifier = LogisticRegression(max_iter=3000, class_weight="balanced", random_state=SEED)

    steps = [("scaler", StandardScaler())]
    if use_pca:
        steps.append(("pca", PCA(n_components=0.95, random_state=SEED)))
    steps.append(("classifier", classifier))
    return Pipeline(steps)


experiments = {
    "handcrafted_only": {
        "features": handcrafted_cols,
        "model": make_model(use_pca=False),
    },
    "efficientnet_only": {
        "features": deep_cols,
        "model": make_model(use_pca=True),
    },
    "hybrid_handcrafted_efficientnet": {
        "features": hybrid_cols,
        "model": make_model(use_pca=True),
    },
}
"""
    ),
    md(
        r"""
## Cross-Validation And Held-Out Test Evaluation
"""
    ),
    code(
        r"""
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
summary_rows = []
trained_models = {}

for name, config in experiments.items():
    feature_cols = config["features"]
    model = config["model"]
    X = hybrid_df[feature_cols].replace([np.inf, -np.inf], np.nan).fillna(0.0)

    cv_results = cross_validate(
        model,
        X.iloc[train_idx],
        y.iloc[train_idx],
        cv=cv,
        scoring=["accuracy", "f1_macro", "f1_weighted"],
        n_jobs=-1,
    )

    model.fit(X.iloc[train_idx], y.iloc[train_idx])
    pred = model.predict(X.iloc[test_idx])

    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X.iloc[test_idx])
        try:
            auc_ovr = roc_auc_score(y.iloc[test_idx], proba, multi_class="ovr", average="weighted")
        except Exception:
            auc_ovr = np.nan
    else:
        auc_ovr = np.nan

    trained_models[name] = {
        "model": model,
        "features": feature_cols,
        "pred": pred,
    }

    summary_rows.append({
        "experiment": name,
        "feature_count": len(feature_cols),
        "cv_accuracy_mean": cv_results["test_accuracy"].mean(),
        "cv_macro_f1_mean": cv_results["test_f1_macro"].mean(),
        "cv_weighted_f1_mean": cv_results["test_f1_weighted"].mean(),
        "test_accuracy": accuracy_score(y.iloc[test_idx], pred),
        "test_macro_f1": f1_score(y.iloc[test_idx], pred, average="macro"),
        "test_weighted_f1": f1_score(y.iloc[test_idx], pred, average="weighted"),
        "test_auc_ovr_weighted": auc_ovr,
    })

results = pd.DataFrame(summary_rows).sort_values("test_macro_f1", ascending=False).reset_index(drop=True)
results_path = RESULT_DIR / f"hybrid_comparison_{MODEL_NAME}.csv"
results.to_csv(results_path, index=False)

display(results)
print(f"Saved comparison: {results_path}")
"""
    ),
    code(
        r"""
plt.figure(figsize=(10, 4.8))
plot_df = results.melt(
    id_vars=["experiment"],
    value_vars=["test_accuracy", "test_macro_f1", "test_weighted_f1"],
    var_name="metric",
    value_name="score",
)
sns.barplot(data=plot_df, x="score", y="experiment", hue="metric")
plt.axvline(0.80, color="red", linestyle="--", label="0.80 target")
plt.title("Held-Out Test Performance")
plt.xlim(0, 1)
plt.tight_layout()
plt.savefig(RESULT_DIR / f"hybrid_comparison_{MODEL_NAME}.png", dpi=160)
plt.show()
"""
    ),
    md(
        r"""
## Best Model Details
"""
    ),
    code(
        r"""
best_name = results.iloc[0]["experiment"]
best = trained_models[best_name]
best_pred = best["pred"]

report = classification_report(
    y.iloc[test_idx],
    best_pred,
    target_names=[LABEL_MAP[i] for i in sorted(y.unique())],
    output_dict=True,
    zero_division=0,
)
report_df = pd.DataFrame(report).T
report_path = RESULT_DIR / f"best_model_classification_report_{MODEL_NAME}.csv"
report_df.to_csv(report_path)

cm = confusion_matrix(y.iloc[test_idx], best_pred, labels=sorted(y.unique()))
disp = ConfusionMatrixDisplay(cm, display_labels=[LABEL_MAP[i] for i in sorted(y.unique())])
disp.plot(cmap="Blues", values_format="d")
plt.title(f"Best Model Confusion Matrix: {best_name}")
plt.tight_layout()
plt.savefig(RESULT_DIR / f"best_model_confusion_matrix_{MODEL_NAME}.png", dpi=160)
plt.show()

display(report_df)
print("Best experiment:", best_name)
print(f"Saved report: {report_path}")
"""
    ),
    code(
        r"""
joblib.dump(best["model"], MODEL_DIR / f"best_hybrid_model_{MODEL_NAME}.pkl")
joblib.dump(best["features"], MODEL_DIR / f"best_hybrid_feature_list_{MODEL_NAME}.pkl")

print("Saved best model and feature list.")
"""
    ),
]


outputs = {
    "03_preprocessing_and_scalograms.ipynb": scalogram_cells,
    "04_efficientnet_embeddings.ipynb": embedding_cells,
    "05_hybrid_feature_training.ipynb": hybrid_cells,
}

for filename, cells in outputs.items():
    path = NOTEBOOK_DIR / filename
    path.write_text(json.dumps(notebook(cells), indent=2), encoding="utf-8")
    print(f"Created {path}")

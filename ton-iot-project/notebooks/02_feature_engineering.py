# %% [markdown]
# # Phase 2 — Feature Engineering
# This notebook handles train-test splitting and applies scaling, label encoding, and custom feature extraction.

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

import random
import json
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
import config
from src.data_loader import load_raw_data
from src.feature_engineering import engineer_features, get_feature_hash

random.seed(config.SEED)
np.random.seed(config.SEED)

Path(config.MODELS_DIR).mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("Phase 2: Feature Engineering")
print("=" * 60)

# %% [markdown]
# ## 1. Load Data

# %%
df = load_raw_data()
print(f"\nLoaded shape: {df.shape}")

# %% [markdown]
# ## 2. Separate Targets

# %%
y_binary = df[config.BINARY_TARGET].copy()
y_multi = df[config.MULTICLASS_TARGET].copy()

print(f"\nBinary target distribution:\n{y_binary.value_counts()}")
print(f"\nMulti-class target distribution:\n{y_multi.value_counts()}")

# %% [markdown]
# ## 3. Train/Test Split (Stratified on Attack Type)

# %%
print("\n[3] Splitting into train/test (80/20 stratified on 'type')...")
X_train_raw, X_test_raw, y_binary_train, y_binary_test, y_multi_train, y_multi_test = \
    train_test_split(
        df, y_binary, y_multi,
        test_size=config.TEST_SIZE,
        stratify=y_multi,
        random_state=config.SEED
    )

print(f"    Train size: {len(X_train_raw):,} rows")
print(f"    Test size:  {len(X_test_raw):,} rows")

# Reset indices
X_train_raw = X_train_raw.reset_index(drop=True)
X_test_raw  = X_test_raw.reset_index(drop=True)
y_binary_train = y_binary_train.reset_index(drop=True)
y_binary_test  = y_binary_test.reset_index(drop=True)
y_multi_train  = y_multi_train.reset_index(drop=True)
y_multi_test   = y_multi_test.reset_index(drop=True)

# %% [markdown]
# ## 4. Feature Engineering — Fit on Train

# %%
print("\n[4] Engineering features (fit on train)...")
X_train, label_encoders, scaler = engineer_features(X_train_raw, fit=True)
print(f"    Train feature shape after engineering: {X_train.shape}")
print(f"    Features: {list(X_train.columns)}")

# %% [markdown]
# ## 5. Feature Engineering — Transform Test

# %%
print("\n[5] Transforming test features...")
X_test, _, _ = engineer_features(X_test_raw, fit=False, label_encoders=label_encoders, scaler=scaler)
print(f"    Test feature shape: {X_test.shape}")

# %% [markdown]
# ## 6. Data Integrity Assertions

# %%
print("\n[6] Verifying data integrity...")
assert not X_train.isnull().any().any(), "NaN found in X_train!"
assert not np.isinf(X_train.values).any(), "Inf found in X_train!"
assert not X_test.isnull().any().any(), "NaN found in X_test!"
assert not np.isinf(X_test.values).any(), "Inf found in X_test!"
assert list(X_train.columns) == list(X_test.columns), "Column mismatch between train/test!"
print("    [OK] No NaN values in train or test")
print("    [OK] No Inf values in train or test")
print("    [OK] Train and test columns match")
print(f"    [OK] Feature count: {X_train.shape[1]}")

# %% [markdown]
# ## 7. Save Feature Matrices

# %%
print("\n[7] Saving feature matrices...")

train_binary = X_train.copy()
train_binary[config.BINARY_TARGET] = y_binary_train.values
train_binary[config.MULTICLASS_TARGET] = y_multi_train.values
train_binary.to_csv("outputs/feature_matrix_train.csv", index=False)

test_binary = X_test.copy()
test_binary[config.BINARY_TARGET] = y_binary_test.values
test_binary[config.MULTICLASS_TARGET] = y_multi_test.values
test_binary.to_csv("outputs/feature_matrix_test.csv", index=False)

print(f"    Saved: outputs/feature_matrix_train.csv ({len(train_binary):,} rows)")
print(f"    Saved: outputs/feature_matrix_test.csv ({len(test_binary):,} rows)")

# %% [markdown]
# ## 8. Save Model Artifacts & Metadata

# %%
print("\n[8] Saving model artifacts...")
feature_list = list(X_train.columns)
feature_hash = get_feature_hash(feature_list)

joblib.dump(feature_list,     config.MODELS_DIR + "feature_list.pkl")
joblib.dump(label_encoders,   config.MODELS_DIR + "label_encoders.pkl")
joblib.dump(scaler,           config.MODELS_DIR + "scaler.pkl")

feature_metadata = {
    "feature_count": len(feature_list),
    "feature_list": feature_list,
    "feature_hash": feature_hash,
    "encoding_summary": {
        "log1p_cols": config.LOG_TRANSFORM_COLS,
        "label_encode_cols": config.LABEL_ENCODE_COLS,
        "bool_encode_cols": config.BOOL_COLS,
        "dropped_cols": config.COLS_TO_DROP,
    }
}
with open(config.MODELS_DIR + "feature_metadata.json", 'w') as f:
    json.dump(feature_metadata, f, indent=2)

print(f"    feature_list.pkl   ({len(feature_list)} features)")
print(f"    label_encoders.pkl ({len(label_encoders)} encoders)")
print(f"    scaler.pkl")
print(f"    feature_metadata.json (hash: {feature_hash[:16]}...)")

print("\n" + "=" * 60)
print("Phase 2 COMPLETE — All acceptance checks passed.")
print(f"Final feature count: {len(feature_list)}")
print(f"Feature hash: {feature_hash}")
print("=" * 60)

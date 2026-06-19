"""
src/feature_engineering.py
Full feature engineering pipeline for the TON_IoT dataset.
All design decisions are documented in DECISIONS.md.
"""
import hashlib
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import config


def _encode_bool_col(series: pd.Series) -> pd.Series:
    """Convert T/F/- strings to 1/0 integers."""
    mapping = {'T': 1, 'True': 1, 'true': 1, '1': 1, 1: 1,
               'F': 0, 'False': 0, 'false': 0, '0': 0, 0: 0, '-': 0}
    return series.map(lambda x: mapping.get(x, 0)).astype(int)


def engineer_features(
    df: pd.DataFrame,
    fit: bool = True,
    label_encoders: dict | None = None,
    scaler: StandardScaler | None = None
) -> tuple:
    """
    Full feature engineering pipeline.

    Parameters
    ----------
    df : pd.DataFrame
        Raw dataframe (may include 'label' and 'type' target columns).
    fit : bool
        If True, fit label encoders and scaler on this data (training).
        If False, use provided label_encoders and scaler (inference).
    label_encoders : dict or None
        Pre-fitted dict of LabelEncoder objects (required if fit=False).
    scaler : StandardScaler or None
        Pre-fitted StandardScaler (required if fit=False).

    Returns
    -------
    tuple : (X_engineered: pd.DataFrame, label_encoders: dict, scaler: StandardScaler)
        X_engineered does NOT include target columns.
    """
    df = df.copy()

    # ── 1. Separate targets before engineering ──────────────────────────────
    targets = {}
    for col in [config.BINARY_TARGET, config.MULTICLASS_TARGET]:
        if col in df.columns:
            targets[col] = df.pop(col)

    # ── 2. Drop high-cardinality / non-generalizable columns ────────────────
    cols_present = [c for c in config.COLS_TO_DROP if c in df.columns]
    df.drop(columns=cols_present, inplace=True)

    # ── 3. Replace '-' placeholder with NaN ──────────────────────────────────
    df.replace('-', np.nan, inplace=True)

    # ── 4. Fill numeric columns with 0 (missing = no event) ─────────────────
    for col in config.NUMERIC_FILL_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(float)

    # ── 5. Impute remaining numeric NaN with column median ───────────────────
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        if df[col].isna().any():
            median_val = df[col].median()
            df[col].fillna(median_val, inplace=True)

    # ── 6. log1p transform skewed numeric columns ────────────────────────────
    for col in config.LOG_TRANSFORM_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            df[col] = np.log1p(df[col].clip(lower=0))
            df.rename(columns={col: f"log_{col}"}, inplace=True)

    # ── 7. Boolean-encode T/F/- columns ─────────────────────────────────────
    for col in config.BOOL_COLS:
        if col in df.columns:
            df[col] = _encode_bool_col(df[col])

    # ── 8. Label-encode categorical columns ──────────────────────────────────
    if label_encoders is None:
        label_encoders = {}

    for col in config.LABEL_ENCODE_COLS:
        if col not in df.columns:
            continue
        df[col] = df[col].fillna('unknown').astype(str)
        if fit:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])
            label_encoders[col] = le
        else:
            le = label_encoders[col]
            # Handle unseen labels by mapping to -1
            known = set(le.classes_)
            df[col] = df[col].map(lambda x: le.transform([x])[0] if x in known else -1)
        df.rename(columns={col: f"{col}_enc"}, inplace=True)

    # ── 9. Derive new features ────────────────────────────────────────────────
    if 'src_port' in df.columns:
        df['src_port'] = pd.to_numeric(df['src_port'], errors='coerce').fillna(0).astype(int)
        df['is_well_known_src_port'] = (df['src_port'] < 1024).astype(int)

    if 'dst_port' in df.columns:
        df['dst_port'] = pd.to_numeric(df['dst_port'], errors='coerce').fillna(0).astype(int)
        df['is_well_known_dst_port'] = (df['dst_port'] < 1024).astype(int)

    # byte_ratio: use log-transformed versions if available
    src_b = df.get('log_src_bytes', df.get('src_bytes', pd.Series(0, index=df.index)))
    dst_b = df.get('log_dst_bytes', df.get('dst_bytes', pd.Series(0, index=df.index)))
    df['byte_ratio'] = src_b / (dst_b + 1e-6)

    src_p = df.get('log_src_pkts', df.get('src_pkts', pd.Series(1, index=df.index)))
    df['avg_src_pkt_size'] = src_b / (src_p + 1)

    dst_p = df.get('log_dst_pkts', df.get('dst_pkts', pd.Series(1, index=df.index)))
    df['avg_dst_pkt_size'] = dst_b / (dst_p + 1)

    # ── 10. Drop any remaining object columns ────────────────────────────────
    obj_cols = df.select_dtypes(include=['object']).columns.tolist()
    if obj_cols:
        print(f"[feature_engineering] Dropping remaining object columns: {obj_cols}")
        df.drop(columns=obj_cols, inplace=True)

    # ── 11. Final NaN/Inf guard ───────────────────────────────────────────────
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.fillna(0, inplace=True)

    # ── 12. StandardScaler ────────────────────────────────────────────────────
    feature_cols = df.columns.tolist()
    if fit:
        scaler = StandardScaler()
        df[feature_cols] = scaler.fit_transform(df[feature_cols])
    else:
        df[feature_cols] = scaler.transform(df[feature_cols])

    # ── 13. Verify no NaN/Inf ─────────────────────────────────────────────────
    assert not df.isnull().any().any(), "NaN values remain after feature engineering!"
    assert not np.isinf(df.values).any(), "Inf values remain after feature engineering!"

    return df, label_encoders, scaler


def get_feature_hash(feature_list: list) -> str:
    """Compute SHA-256 hash of the feature list for integrity checking."""
    return hashlib.sha256(str(feature_list).encode()).hexdigest()

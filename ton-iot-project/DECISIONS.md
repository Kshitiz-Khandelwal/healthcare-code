# Design Decisions

## D-001: Use LightGBM as the Final/Primary Model

**Decision**: LightGBM is the primary production candidate for both binary and multi-class tasks.

**Rationale**:
- 211,044 rows × ~33 features is a large tabular dataset. LightGBM trains in seconds with `n_jobs=1`.
- Native support for class imbalance via `is_unbalance=True` (binary) and `class_weight` (multi-class).
- `feature_importances_` enables SHAP explainability with minimal overhead.
- Same model used in the healthcare ECG project, enabling consistent tooling across projects.

---

## D-002: Use Macro-F1 as Primary Metric for Multi-Class

**Decision**: The primary selection metric for the multi-class model is held-out **Macro-F1**, not accuracy.

**Rationale**:
- The dataset is class-imbalanced (scanning and backdoor attacks are far more common than MITM or XSS).
- Accuracy rewards the model for correctly classifying the majority classes while potentially missing rare attack types.
- In an IDS context, missing a ransomware or MITM attack is unacceptably dangerous even if the system catches 99% of DDoS attacks.
- Macro-F1 weights all classes equally, forcing the model to perform reasonably on rare attack types.

---

## D-003: Use F1 (Attack Class) as Primary Metric for Binary Task

**Decision**: Binary task primary metric is held-out **F1-score** for the attack class (label=1), not accuracy.

**Rationale**:
- If the dataset skews benign, accuracy could be misleadingly high even with a model that never predicts attack.
- False negatives (missed attacks) are more dangerous than false positives (benign traffic flagged as attack) in IDS.

---

## D-004: Drop Raw IP Addresses

**Decision**: `src_ip` and `dst_ip` are dropped before modeling.

**Rationale**:
- This dataset uses lab-specific private IP ranges (192.168.x.x). A model learning these specific IPs would fail immediately on any other network.
- Port numbers are retained because they reflect service protocols (generalizable).

---

## D-005: Drop High-Cardinality String Columns

**Decision**: `dns_query`, `ssl_subject`, `ssl_issuer`, `ssl_cipher`, `http_uri`, `http_user_agent`, `weird_addl` are dropped.

**Rationale**:
- Label-encoding thousands of unique DNS queries or HTTP URIs creates meaningless integer codes.
- The useful signal from HTTP/DNS activity is already partially captured by `service`, `dns_rcode`, `http_status_code`, and the DNS/SSL boolean flags.
- Advanced encoding (frequency encoding, target encoding) could recover some signal but adds complexity beyond this project's scope.

---

## D-006: Stratified 80/20 Split

**Decision**: Stratified train-test split (80/20, `random_state=42`) on both binary and multi-class tasks.

**Rationale**:
- Stratification ensures all attack types are represented in both train and test sets, including rare classes.
- 80/20 matches the healthcare ECG project split for consistency.
- The test set must not be touched during feature engineering (scaler, label encoders fit on train only).

---

## D-007: n_jobs=1 for All Models

**Decision**: All model training uses `n_jobs=1`.

**Rationale**:
- Prevents race conditions and unpredictable multiprocessing behavior in Jupyter notebooks.
- Matches the healthcare ECG project guardrail.
- LightGBM is fast enough on this dataset with a single thread.

---

## D-008: Feature Hash Integrity Check

**Decision**: A SHA-256 hash of the feature list (column names in order) is saved in all metadata JSON files.

**Rationale**:
- Prevents accidental inference with a model trained on a different feature set.
- Critical guard against column reordering bugs after feature engineering changes.
- Same approach as the healthcare project's `model_metadata_efficientnet_b4.json`.

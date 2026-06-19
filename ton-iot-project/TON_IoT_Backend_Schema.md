# TON_IoT Network Intrusion Detection — Backend Schema & Registry

> **Project**: TON_IoT Network Intrusion Detection Pipeline  
> **Author**: Kshitiz Khandelwal

---

## 1. Feature Matrix Schema

All rows in `outputs/feature_matrix_train.csv` and `outputs/feature_matrix_test.csv` adhere to this schema:

| Column | DType | Source | Notes |
|---|---|---|---|
| `src_port` | int64 | Raw | 0–65535 |
| `dst_port` | int64 | Raw | 0–65535 |
| `log_duration` | float64 | Derived | `log1p(duration)` |
| `log_src_bytes` | float64 | Derived | `log1p(src_bytes)` |
| `log_dst_bytes` | float64 | Derived | `log1p(dst_bytes)` |
| `log_missed_bytes` | float64 | Derived | `log1p(missed_bytes)` |
| `log_src_pkts` | float64 | Derived | `log1p(src_pkts)` |
| `log_src_ip_bytes` | float64 | Derived | `log1p(src_ip_bytes)` |
| `log_dst_pkts` | float64 | Derived | `log1p(dst_pkts)` |
| `log_dst_ip_bytes` | float64 | Derived | `log1p(dst_ip_bytes)` |
| `dns_qclass` | int64 | Raw | Filled 0 for missing |
| `dns_qtype` | int64 | Raw | Filled 0 for missing |
| `dns_rcode` | int64 | Raw | Filled 0 for missing |
| `dns_AA` | int64 | Encoded | T→1, F/−→0 |
| `dns_RD` | int64 | Encoded | T→1, F/−→0 |
| `dns_RA` | int64 | Encoded | T→1, F/−→0 |
| `dns_rejected` | int64 | Encoded | T→1, F/−→0 |
| `ssl_resumed` | int64 | Encoded | T→1, F/−→0 |
| `ssl_established` | int64 | Encoded | T→1, F/−→0 |
| `http_trans_depth` | int64 | Raw | Filled 0 for missing |
| `http_request_body_len` | int64 | Raw | Filled 0 for missing |
| `http_response_body_len` | int64 | Raw | Filled 0 for missing |
| `http_status_code` | int64 | Raw | Filled 0 for missing |
| `weird_notice` | int64 | Encoded | T→1, F/−→0 |
| `proto_enc` | int64 | LabelEncoded | `proto` → integer |
| `service_enc` | int64 | LabelEncoded | `service` → integer |
| `conn_state_enc` | int64 | LabelEncoded | `conn_state` → integer |
| `weird_name_enc` | int64 | LabelEncoded | `weird_name` → integer |
| `is_well_known_src_port` | int64 | Derived | `int(src_port < 1024)` |
| `is_well_known_dst_port` | int64 | Derived | `int(dst_port < 1024)` |
| `byte_ratio` | float64 | Derived | `src_bytes / (dst_bytes + 1)` |
| `avg_src_pkt_size` | float64 | Derived | `src_bytes / (src_pkts + 1)` |
| `avg_dst_pkt_size` | float64 | Derived | `dst_bytes / (dst_pkts + 1)` |
| `label` | int64 | Target (binary) | `label` column (0=benign, 1=attack) |
| `type` | string | Target (multi) | `type` column (attack name) |

---

## 2. Model Artifact Registry

All model artifacts are stored in `outputs/models/`:

| Artifact | Purpose | Contains |
|---|---|---|
| `feature_list.pkl` | Exact column order for model input | Python list of feature names in training order |
| `label_encoders.pkl` | Categorical encoders for inference | Dict: `{"proto": LabelEncoder, "service": LabelEncoder, ...}` |
| `scaler.pkl` | StandardScaler fitted on training data | sklearn StandardScaler object |
| `feature_metadata.json` | Feature schema integrity | `{"feature_count": N, "feature_hash": "sha256...", "encoding_summary": {...}}` |
| `best_binary_model.pkl` | Final binary RandomForest classifier | Scikit-learn RandomForestClassifier binary |
| `binary_model_metadata.json` | Binary model provenance | `{"timestamp": ..., "seed": 42, "model_name": "RandomForestClassifier", "test_f1": 0.9993, "test_auc": 1.0000, "feature_hash": ...}` |
| `best_multiclass_model.pkl` | Final multi-class RandomForest classifier | Scikit-learn RandomForestClassifier binary |
| `multiclass_model_metadata.json` | Multi-class model provenance | `{"timestamp": ..., "seed": 42, "model_name": "RandomForestClassifier", "test_f1_macro": 0.9658, "classes": [...], "feature_hash": ...}` |

**Hash integrity rule**: `feature_hash` in `*_metadata.json` must match `hashlib.sha256(str(feature_list).encode()).hexdigest()` — verify at load time before any inference.

---

## 3. Prediction Output Schema

`outputs/reports/sample_predictions.csv` contains:

| Column | Type | Description |
|---|---|---|
| `row_index` | int | Row index from the test set |
| `true_type` | string | Ground truth attack type |
| `true_label` | int | Ground truth binary label (0 or 1) |
| `predicted_type` | string | Multi-class model predicted attack type |
| `confidence` | float | Max class probability for multi-class prediction |
| `is_correct` | bool | Whether multi-class prediction matches `true_type` |
| `byte_ratio` | float | Traffic asymmetry ratio |

---

## 4. `validate_all.py` Script Checklists

`scripts/validate_all.py` checks the following files:

* `outputs/models/feature_list.pkl`
* `outputs/models/label_encoders.pkl`
* `outputs/models/scaler.pkl`
* `outputs/models/feature_metadata.json`
* `outputs/models/best_binary_model.pkl`
* `outputs/models/binary_model_metadata.json`
* `outputs/models/best_multiclass_model.pkl`
* `outputs/models/multiclass_model_metadata.json`
* `outputs/reports/data_audit.md`
* `outputs/reports/TON_IoT_Final_Report.md`
* `outputs/reports/sample_predictions.csv`
* `outputs/plots/label_distribution.png`
* `outputs/plots/type_distribution.png`
* `outputs/plots/correlation_heatmap.png`
* `outputs/plots/confusion_matrix_binary_LogisticRegression.png`
* `outputs/plots/confusion_matrix_binary_RandomForestClassifier.png`
* `outputs/plots/confusion_matrix_binary_XGBClassifier.png`
* `outputs/plots/confusion_matrix_binary_LGBMClassifier.png`
* `outputs/plots/roc_curve_binary.png`
* `outputs/plots/confusion_matrix_multiclass.png`
* `outputs/plots/feature_importance_multiclass.png`
* `outputs/plots/per_class_f1_multiclass.png`
* `outputs/plots/model_comparison_binary.png`

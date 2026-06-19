"""
TON_IoT Network Intrusion Detection — Central Configuration
All configuration values live here. Never hardcode values in notebooks or scripts.
"""

import random
import numpy as np

# ─────────────────────────────────────────────────────────────
# REPRODUCIBILITY
# ─────────────────────────────────────────────────────────────
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# ─────────────────────────────────────────────────────────────
# DATA PATHS
# ─────────────────────────────────────────────────────────────
DATA_PATH = r"C:\Users\Admin\Desktop\Kshitiz\thon iot dataset\train_test_network.csv"

# Set to None to use the full dataset; set to an integer (e.g., 50000)
# for faster smoke-test iterations during development.
MAX_ROWS = None

# ─────────────────────────────────────────────────────────────
# SPLIT CONFIGURATION
# ─────────────────────────────────────────────────────────────
TEST_SIZE = 0.20         # 80/20 stratified train-test split
CV_FOLDS  = 5            # Number of stratified k-fold CV folds

# ─────────────────────────────────────────────────────────────
# TARGET COLUMNS
# ─────────────────────────────────────────────────────────────
BINARY_TARGET     = "label"   # 0 = benign, 1 = attack
MULTICLASS_TARGET = "type"    # attack type name (string)

# ─────────────────────────────────────────────────────────────
# OUTPUT PATHS
# ─────────────────────────────────────────────────────────────
OUTPUT_DIR  = "outputs/"
MODELS_DIR  = "outputs/models/"
PLOTS_DIR   = "outputs/plots/"
REPORTS_DIR = "outputs/reports/"

# ─────────────────────────────────────────────────────────────
# MODEL NAMES (for artifact versioning)
# ─────────────────────────────────────────────────────────────
BINARY_MODEL_NAME     = "best_binary_model"
MULTICLASS_MODEL_NAME = "best_multiclass_model"

# ─────────────────────────────────────────────────────────────
# FEATURE ENGINEERING SETTINGS
# ─────────────────────────────────────────────────────────────
# Columns to drop before modeling (high-cardinality strings, raw IPs)
COLS_TO_DROP = [
    "src_ip", "dst_ip",
    "dns_query",
    "ssl_subject", "ssl_issuer", "ssl_cipher",
    "http_uri", "http_user_agent",
    "weird_addl",
    "ssl_version",
    "http_method", "http_version",
    "http_orig_mime_types", "http_resp_mime_types",
]

# Numeric columns to apply log1p transformation
LOG_TRANSFORM_COLS = [
    "duration", "src_bytes", "dst_bytes", "missed_bytes",
    "src_pkts", "src_ip_bytes", "dst_pkts", "dst_ip_bytes",
]

# Categorical columns to label-encode
LABEL_ENCODE_COLS = [
    "proto", "service", "conn_state", "weird_name",
]

# Boolean-like columns (T/F/- → 1/0)
BOOL_COLS = [
    "dns_AA", "dns_RD", "dns_RA", "dns_rejected",
    "ssl_resumed", "ssl_established", "weird_notice",
]

# Numeric columns to fill missing values with median
NUMERIC_FILL_COLS = [
    "dns_qclass", "dns_qtype", "dns_rcode",
    "http_trans_depth", "http_request_body_len",
    "http_response_body_len", "http_status_code",
]

# ─────────────────────────────────────────────────────────────
# LIGHTGBM DEFAULT PARAMS
# ─────────────────────────────────────────────────────────────
LGBM_PARAMS = {
    "n_estimators":  150,
    "learning_rate": 0.05,
    "max_depth":     6,
    "random_state":  SEED,
    "n_jobs":        1,
    "verbose":      -1,
}

# ─────────────────────────────────────────────────────────────
# XGBOOST DEFAULT PARAMS
# ─────────────────────────────────────────────────────────────
XGB_PARAMS = {
    "n_estimators":  150,
    "learning_rate": 0.05,
    "max_depth":     6,
    "random_state":  SEED,
    "n_jobs":        1,
    "eval_metric":   "logloss",
}

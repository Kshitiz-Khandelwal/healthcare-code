# %% [markdown]
# # Phase 5 — Model Comparison & Final Report Generation
# This notebook loads metadata from previous runs, compares binary classification models, and generates the final comprehensive report markdown file.

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

import json
import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import config

Path(config.PLOTS_DIR).mkdir(parents=True, exist_ok=True)
Path(config.REPORTS_DIR).mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("Phase 5: Model Comparison & Final Report Generation")
print("=" * 60)

# %% [markdown]
# ## 1. Load All Metadata

# %%
print("\n[1] Loading model metadata...")

with open(config.MODELS_DIR + "binary_model_metadata.json") as f:
    binary_meta = json.load(f)
with open(config.MODELS_DIR + "multiclass_model_metadata.json") as f:
    multi_meta = json.load(f)
with open(config.MODELS_DIR + "feature_metadata.json") as f:
    feature_meta = json.load(f)

feature_list = joblib.load(config.MODELS_DIR + "feature_list.pkl")

print(f"    Binary best model: {binary_meta['model_name']}")
print(f"      Test F1: {binary_meta['test_f1']:.4f}  AUC: {binary_meta['test_auc']:.4f}")
print(f"    Multi-class best model: {multi_meta['model_name']}")
print(f"      Test Macro-F1: {multi_meta['test_f1_macro']:.4f}  Accuracy: {multi_meta['test_accuracy']:.4f}")

classes = multi_meta["classes"]
per_class_f1 = multi_meta.get("per_class_f1", {})

# %% [markdown]
# ## 2. Model Comparison Table (Binary)

# %%
print("\n[2] Building comparison tables...")

# We have individual model logs in the run outputs - build from known results
# (These were printed in Phases 3 & 4, we reconstruct for the report)
binary_comparison = {
    "LogisticRegression":    {"cv_acc": 0.9890, "cv_f1": 0.9928, "cv_auc": 0.9955,
                              "test_acc": 0.9888, "test_f1": 0.9927, "test_auc": 0.9958},
    "RandomForestClassifier": {"cv_acc": 0.9988, "cv_f1": 0.9992, "cv_auc": 0.9999,
                               "test_acc": 0.9989, "test_f1": 0.9993, "test_auc": 1.0000},
    "XGBClassifier":         {"cv_acc": 0.9984, "cv_f1": 0.9990, "cv_auc": 1.0000,
                              "test_acc": 0.9984, "test_f1": 0.9990, "test_auc": 0.9999},
    "LGBMClassifier":        {"cv_acc": 0.9978, "cv_f1": 0.9986, "cv_auc": 1.0000,
                              "test_acc": 0.9974, "test_f1": 0.9983, "test_auc": 1.0000},
}

binary_best = binary_meta["model_name"]

# %% [markdown]
# ## 3. Model Comparison Charts

# %%
print("\n[3] Generating model comparison chart...")
models_names = list(binary_comparison.keys())
model_labels = ["LogReg", "RandomForest", "XGBoost", "LightGBM"]
test_f1s = [binary_comparison[m]["test_f1"] for m in models_names]
test_aucs = [binary_comparison[m]["test_auc"] for m in models_names]

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
colors_bar = ['#3498db', '#2ecc71', '#e74c3c', '#9b59b6']

# F1 chart
bars = axes[0].bar(model_labels, test_f1s, color=colors_bar, edgecolor='black')
axes[0].set_title('Binary Classification — Test F1 Score\n(Attack class)', fontweight='bold')
axes[0].set_ylabel('F1 Score')
axes[0].set_ylim(0.97, 1.01)
for bar, val in zip(bars, test_f1s):
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.0005,
                 f'{val:.4f}', ha='center', fontsize=9, fontweight='bold')

# AUC chart
bars2 = axes[1].bar(model_labels, test_aucs, color=colors_bar, edgecolor='black')
axes[1].set_title('Binary Classification — Test ROC-AUC', fontweight='bold')
axes[1].set_ylabel('AUC')
axes[1].set_ylim(0.99, 1.002)
for bar, val in zip(bars2, test_aucs):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.0001,
                 f'{val:.4f}', ha='center', fontsize=9, fontweight='bold')

plt.suptitle('Model Comparison — Binary Classification (TON_IoT)', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(f"{config.PLOTS_DIR}model_comparison_binary.png", dpi=150, bbox_inches='tight')
plt.close()
print(f"    Saved: {config.PLOTS_DIR}model_comparison_binary.png")

# %% [markdown]
# ## 4. Check Multi-Class Results

# %%
print("\n[4] Checking multi-class results...")
if per_class_f1:
    print("    Per-class F1 scores:")
    for cls, f1 in sorted(per_class_f1.items()):
        print(f"      {cls:<15}: {f1:.4f}")

# %% [markdown]
# ## 5. Generate Comprehensive Final Report

# %%
print("\n[5] Generating TON_IoT_Final_Report.md...")

report_lines = [
    "# TON_IoT Network Intrusion Detection — Final Comprehensive Report\n\n",
    f"> **Author**: Kshitiz Khandelwal  \n",
    f"> **Dataset**: TON_IoT Network Dataset (UNSW Canberra)  \n",
    f"> **Source**: https://research.unsw.edu.au/projects/toniot-datasets  \n",
    f"> **Binary Best Model**: {binary_meta['model_name']}  \n",
    f"> **Multi-Class Best Model**: {multi_meta['model_name']}  \n",
    f"> **Binary Test F1 (Attack)**: {binary_meta['test_f1']:.4f}  \n",
    f"> **Binary Test AUC**: {binary_meta['test_auc']:.4f}  \n",
    f"> **Multi-Class Test Macro-F1**: {multi_meta['test_f1_macro']:.4f}  \n",
    f"> **Multi-Class Test Accuracy**: {multi_meta['test_accuracy']:.4f}  \n",
    f"> **Training Timestamp**: {multi_meta['timestamp_utc']}  \n",
    f"> **Random Seed**: {multi_meta['seed']}  \n\n",
    "---\n\n",

    "## Table of Contents\n\n",
    "1. [Executive Summary](#1-executive-summary)\n",
    "2. [Problem Statement](#2-problem-statement)\n",
    "3. [Dataset Description](#3-dataset-description)\n",
    "4. [End-to-End System Architecture](#4-end-to-end-system-architecture)\n",
    "5. [Feature Engineering](#5-feature-engineering)\n",
    "6. [Binary Classification Results](#6-binary-classification-results)\n",
    "7. [Multi-Class Classification Results](#7-multi-class-classification-results)\n",
    "8. [Model Comparison](#8-model-comparison)\n",
    "9. [Feature Importance](#9-feature-importance)\n",
    "10. [Attack Type Analysis](#10-attack-type-analysis)\n",
    "11. [Model Artifacts and Reproducibility](#11-model-artifacts-and-reproducibility)\n",
    "12. [Limitations and Responsible Use](#12-limitations-and-responsible-use)\n",
    "13. [Conclusion](#13-conclusion)\n",
    "14. [References](#14-references)\n\n",
    "---\n\n",

    "## 1. Executive Summary\n\n",
    "This project implements an end-to-end machine learning pipeline for network intrusion detection ",
    "using the TON_IoT dataset — 211,043 IoT/IIoT network flow records with 44 raw features. ",
    "The pipeline engineers 33 meaningful features, trains and compares four classifiers on both binary ",
    "(benign vs. attack) and multi-class (attack type) tasks, and delivers a visual dashboard deployed to Vercel.\n\n",
    "| Task | Best Model | Test Accuracy | Test F1/Macro-F1 | Test AUC |\n",
    "|---|---|---:|---:|---:|\n",
    f"| Binary (benign vs attack) | {binary_meta['model_name']} | {binary_meta['test_accuracy']:.4f} | {binary_meta['test_f1']:.4f} | {binary_meta['test_auc']:.4f} |\n",
    f"| Multi-Class (attack type) | {multi_meta['model_name']} | {multi_meta['test_accuracy']:.4f} | {multi_meta['test_f1_macro']:.4f} | {multi_meta.get('test_auc', 'N/A')} |\n\n",
    "---\n\n",

    "## 2. Problem Statement\n\n",
    "IoT and IIoT environments introduce millions of low-power, network-connected devices into smart homes, ",
    "factories, and infrastructure. These devices are attractive targets for attackers: they often lack ",
    "built-in security controls, run embedded firmware, and communicate over standard protocols.\n\n",
    "The goal of this project is to automatically classify network traffic flows from IoT environments as:\n\n",
    "1. **Benign** or **malicious** (binary classification).\n",
    "2. The specific **attack type** (multi-class classification).\n\n",
    "---\n\n",

    "## 3. Dataset Description\n\n",
    "### 3.1 Source\n\n",
    "| Property | Value |\n",
    "|---|---|\n",
    "| Dataset | TON_IoT Network Dataset |\n",
    "| Developed by | UNSW Canberra Cyber Range Lab |\n",
    "| License | CC BY 4.0 |\n",
    "| File | `train_test_network.csv` |\n",
    "| Total rows | 211,043 |\n",
    "| Total columns | 44 |\n",
    "| Capture tools | Argus, Bro (Zeek) |\n\n",
    "### 3.2 Binary Label Distribution\n\n",
    "| Label | Count | Percentage |\n",
    "|---|---:|---:|\n",
    "| Benign (0) | 50,000 | 23.7% |\n",
    "| Attack (1) | 161,043 | 76.3% |\n\n",
    "### 3.3 Attack Type Distribution\n\n",
    "| Attack Type | Count | Percentage |\n",
    "|---|---:|---:|\n",
    "| normal | 50,000 | 23.7% |\n",
    "| backdoor | 20,000 | 9.5% |\n",
    "| ddos | 20,000 | 9.5% |\n",
    "| dos | 20,000 | 9.5% |\n",
    "| injection | 20,000 | 9.5% |\n",
    "| password | 20,000 | 9.5% |\n",
    "| ransomware | 20,000 | 9.5% |\n",
    "| scanning | 20,000 | 9.5% |\n",
    "| xss | 20,000 | 9.5% |\n",
    "| mitm | 1,043 | 0.5% |\n\n",
    "---\n\n",

    "## 4. End-to-End System Architecture\n\n",
    "```text\n",
    "train_test_network.csv (211,043 rows x 44 cols)\n",
    "         |\n",
    "         v\n",
    "Phase 1: Data Exploration\n",
    "         |\n",
    "         v\n",
    "Phase 2: Feature Engineering\n",
    "  Drop: src_ip, dst_ip, high-cardinality strings\n",
    "  Encode: proto, service, conn_state, weird_name\n",
    "  Transform: log1p on all byte/packet/duration cols\n",
    "  Derive: byte_ratio, avg_pkt_size, is_well_known_port\n",
    "  33 engineered features\n",
    "         |\n",
    "         +------------------+\n",
    "         |                  |\n",
    "         v                  v\n",
    "Phase 3: Binary       Phase 4: Multi-Class\n",
    "(label: 0/1)          (type: 10 attack types)\n",
    "4 Models Compared     4 Models Compared\n",
    "Primary: F1           Primary: Macro-F1\n",
    "         |                  |\n",
    "         +------------------+\n",
    "                 |\n",
    "                 v\n",
    "Phase 5: Comparison + Final Report\n",
    "                 |\n",
    "                 v\n",
    "Phase 6: Next.js Dashboard -> Vercel\n",
    "```\n\n",
    "---\n\n",

    "## 5. Feature Engineering\n\n",
    "### 5.1 Columns Dropped\n\n",
    "| Column | Reason |\n",
    "|---|---|\n",
    "| `src_ip`, `dst_ip` | Lab-specific IPs, not generalizable |\n",
    "| `dns_query`, `http_uri` | Extreme cardinality (hundreds of unique values) |\n",
    "| `ssl_subject`, `ssl_issuer`, `ssl_cipher` | >99% missing, extreme cardinality |\n",
    "| `http_user_agent`, `http_method`, `http_version` | >99% missing |\n",
    "| `weird_addl`, `ssl_version`, `http_orig_mime_types`, `http_resp_mime_types` | >99% missing, complex encoding |\n\n",
    "### 5.2 Feature Transformations\n\n",
    "| Feature | Transformation | Rationale |\n",
    "|---|---|---|\n",
    "| `duration`, `src_bytes`, `dst_bytes`, etc. | `log1p` | Extreme right-skew from attack traffic |\n",
    "| `proto`, `service`, `conn_state`, `weird_name` | LabelEncoder | Low-cardinality categoricals |\n",
    "| `dns_AA`, `dns_RD`, `ssl_resumed`, etc. | T→1, F/−→0 | Boolean flags |\n\n",
    "### 5.3 Derived Features\n\n",
    "| Feature | Formula | Security Relevance |\n",
    "|---|---|---|\n",
    "| `byte_ratio` | `src_bytes / (dst_bytes + 1)` | DDoS floods (high src), exfiltration (high dst) |\n",
    "| `avg_src_pkt_size` | `src_bytes / (src_pkts + 1)` | Small = SYN flood, large = data transfer |\n",
    "| `avg_dst_pkt_size` | `dst_bytes / (dst_pkts + 1)` | Response packet size pattern |\n",
    "| `is_well_known_src_port` | `int(src_port < 1024)` | Privileged source port usage |\n",
    "| `is_well_known_dst_port` | `int(dst_port < 1024)` | Common attack target ports |\n\n",
    f"**Final feature count: {feature_meta['feature_count']}**\n\n",
    f"Feature hash (integrity): `{feature_meta['feature_hash']}`\n\n",
    "---\n\n",

    "## 6. Binary Classification Results\n\n",
    f"### 6.1 Best Model: {binary_meta['model_name']}\n\n",
    "| Metric | Value |\n",
    "|---|---:|\n",
    f"| Test Accuracy | {binary_meta['test_accuracy']:.4f} |\n",
    f"| Test F1 (Attack class) | {binary_meta['test_f1']:.4f} |\n",
    f"| Test ROC-AUC | {binary_meta['test_auc']:.4f} |\n\n",
    "### 6.2 All Models Comparison\n\n",
    "| Model | CV Acc | CV F1 | CV AUC | Test Acc | Test F1 | Test AUC |\n",
    "|---|---:|---:|---:|---:|---:|---:|\n",
]

best_binary_name = binary_meta["model_name"]
for m, r in binary_comparison.items():
    marker = " ← **BEST**" if m == best_binary_name else ""
    report_lines.append(
        f"| {m}{marker} | {r['cv_acc']:.4f} | {r['cv_f1']:.4f} | {r['cv_auc']:.4f} | "
        f"{r['test_acc']:.4f} | {r['test_f1']:.4f} | {r['test_auc']:.4f} |\n"
    )

report_lines += [
    "\n---\n\n",
    "## 7. Multi-Class Classification Results\n\n",
    f"### 7.1 Best Model: {multi_meta['model_name']}\n\n",
    "| Metric | Value |\n",
    "|---|---:|\n",
    f"| Test Accuracy | {multi_meta['test_accuracy']:.4f} |\n",
    f"| Test Macro-F1 | {multi_meta['test_f1_macro']:.4f} |\n",
    f"| Test Weighted-F1 | {multi_meta['test_f1_weighted']:.4f} |\n\n",
]

if per_class_f1:
    report_lines.append("### 7.2 Per-Class F1 Scores\n\n")
    report_lines.append("| Attack Type | F1 Score | Assessment |\n")
    report_lines.append("|---|---:|---|\n")
    for cls, f1 in sorted(per_class_f1.items()):
        assessment = "Excellent" if f1 >= 0.95 else "Good" if f1 >= 0.85 else "Fair" if f1 >= 0.70 else "Needs Improvement"
        report_lines.append(f"| {cls} | {f1:.4f} | {assessment} |\n")
    report_lines.append("\n")

report_lines += [
    "---\n\n",
    "## 8. Model Comparison\n\n",
    "The best binary model is **RandomForestClassifier** with near-perfect Test F1=0.9993 and AUC=1.0000. ",
    "This exceptional result is consistent with the TON_IoT dataset being collected in a controlled lab environment ",
    "where attack patterns are distinct from normal traffic.\n\n",
    "### Binary vs Multi-Class Performance\n\n",
    "| Task | Best Model | Metric | Value |\n",
    "|---|---|---|---:|\n",
    f"| Binary | {binary_meta['model_name']} | Test F1 (attack) | {binary_meta['test_f1']:.4f} |\n",
    f"| Binary | {binary_meta['model_name']} | Test AUC | {binary_meta['test_auc']:.4f} |\n",
    f"| Multi-Class | {multi_meta['model_name']} | Test Macro-F1 | {multi_meta['test_f1_macro']:.4f} |\n",
    f"| Multi-Class | {multi_meta['model_name']} | Test Accuracy | {multi_meta['test_accuracy']:.4f} |\n\n",
    "---\n\n",

    "## 9. Feature Importance\n\n",
    "Feature importance analysis from the LightGBM multi-class model (see `outputs/plots/feature_importance_multiclass.png`) ",
    "reveals the most predictive network flow features for attack type classification.\n\n",
    "Key observations:\n",
    "- **`conn_state_enc`** (connection state) is typically the top feature — connection states like `S0` (SYN only), `REJ` (rejected), and `OTH` are highly diagnostic\n",
    "- **`log_duration`** distinguishes long-lived backdoor/C2 sessions from short scanning or DoS bursts\n",
    "- **`byte_ratio`** captures traffic asymmetry: DDoS floods have high `src_bytes`, exfiltration has high `dst_bytes`\n",
    "- **`proto_enc`** (protocol) differentiates UDP floods (DDoS) from TCP-based attacks\n",
    "- **`log_src_bytes`**, **`log_dst_bytes`** are important volume indicators\n\n",
    "---\n\n",

    "## 10. Attack Type Analysis\n\n",
    "| Attack | Description | Key Network Indicators |\n",
    "|---|---|---|\n",
    "| `backdoor` | Remote C2 channel | Long duration, balanced bytes, TCP |\n",
    "| `ddos` | Distributed flood | High src_pkts, REJ/S0 conn_state, UDP |\n",
    "| `dos` | Single-source flood | High src_bytes, short duration, S0 state |\n",
    "| `injection` | SQL/command injection | HTTP traffic, small payload, SF state |\n",
    "| `mitm` | Man-in-the-middle | ARP manipulation, unusual dst_ip patterns |\n",
    "| `password` | Brute-force | Many short connections, same dst_port |\n",
    "| `ransomware` | File encryption | High dst_bytes (file reads), TCP |\n",
    "| `scanning` | Port/network scan | Many REJ connections, varied dst_port |\n",
    "| `xss` | Cross-site scripting | HTTP GET/POST with specific URIs |\n\n",
    "**Note on MITM class**: MITM has only 1,043 samples (0.5% of data) versus 20,000 for other attack types. ",
    "This extreme imbalance makes MITM the most challenging class. Class weighting helps but external validation is recommended.\n\n",
    "---\n\n",

    "## 11. Model Artifacts and Reproducibility\n\n",
    "All artifacts are stored in `outputs/models/`:\n\n",
    "| Artifact | Purpose |\n",
    "|---|---|\n",
    "| `feature_list.pkl` | Exact ordered feature column list |\n",
    "| `label_encoders.pkl` | Dict of fitted LabelEncoder objects |\n",
    "| `scaler.pkl` | Fitted StandardScaler |\n",
    "| `feature_metadata.json` | Feature count, encoding summary, SHA-256 hash |\n",
    "| `best_binary_model.pkl` | Final binary RandomForestClassifier |\n",
    "| `binary_model_metadata.json` | Binary model provenance + metrics |\n",
    "| `best_multiclass_model.pkl` | Final multi-class LightGBM/RF classifier |\n",
    "| `multiclass_model_metadata.json` | Multi-class provenance + metrics + per-class F1 |\n\n",
    f"Feature hash: `{feature_meta['feature_hash']}`\n\n",
    "---\n\n",

    "## 12. Limitations and Responsible Use\n\n",
    "| Limitation | Explanation |\n",
    "|---|---|\n",
    "| Simulated environment | Data from a controlled lab, not a production network |\n",
    "| Fixed IP ranges | Lab-specific 192.168.x.x addresses; model may not generalize to other topologies |\n",
    "| MITM class imbalance | Only 1,043 MITM samples — performance on this class may be unreliable |\n",
    "| No temporal modeling | Flows treated as independent; temporal attack sequences not captured |\n",
    "| Research prototype | Not a replacement for commercial IDS/IPS systems |\n\n",
    "---\n\n",

    "## 13. Conclusion\n\n",
    "The TON_IoT Network Intrusion Detection pipeline successfully demonstrates a complete applied machine learning workflow ",
    "for IoT network security. Starting from raw 44-column network flow records, the pipeline engineers 33 meaningful features, ",
    "compares four classifiers on binary and multi-class tasks, and selects the best model for each:\n\n",
    "- **Binary task**: {binary_meta['model_name']} achieves {binary_meta['test_f1']:.4f} F1 and {binary_meta['test_auc']:.4f} AUC\n",
    "- **Multi-class task**: {multi_meta['model_name']} achieves {multi_meta['test_f1_macro']:.4f} Macro-F1 across all 10 attack types\n\n",
    "The system is best presented as a **research/academic prototype** for IoT intrusion detection. ",
    "It demonstrates strong classification performance on the TON_IoT benchmark but requires validation ",
    "on real-world production network data before operational deployment.\n\n",
    "---\n\n",

    "## 14. References\n\n",
    "1. Moustafa, N. (2021). TON_IoT datasets. UNSW Canberra. https://research.unsw.edu.au/projects/toniot-datasets\n",
    "2. Ke, G., et al. (2017). LightGBM: A highly efficient gradient boosting decision tree. NeurIPS 2017.\n",
    "3. Breiman, L. (2001). Random Forests. Machine Learning, 45(1), 5-32.\n",
    "4. Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. KDD 2016.\n",
    "5. Pedregosa, F., et al. (2011). Scikit-learn: Machine Learning in Python. JMLR 12, 2825-2830.\n",
    "6. Lundberg, S., & Lee, S.-I. (2017). A unified approach to interpreting model predictions. NeurIPS 2017.\n",
]

report_path = config.REPORTS_DIR + "TON_IoT_Final_Report.md"
with open(report_path, 'w', encoding='utf-8') as f:
    f.writelines(report_lines)
print(f"    Saved: {report_path}")

print("\n" + "=" * 60)
print("Phase 5 COMPLETE")
print("=" * 60)

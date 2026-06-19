# TON_IoT Network Intrusion Detection — Final Comprehensive Report

> **Author**: Kshitiz Khandelwal  
> **Dataset**: TON_IoT Network Dataset (UNSW Canberra)  
> **Source**: https://research.unsw.edu.au/projects/toniot-datasets  
> **Binary Best Model**: RandomForestClassifier  
> **Multi-Class Best Model**: RandomForestClassifier  
> **Binary Test F1 (Attack)**: 0.9993  
> **Binary Test AUC**: 1.0000  
> **Multi-Class Test Macro-F1**: 0.9658  
> **Multi-Class Test Accuracy**: 0.9888  
> **Training Timestamp**: 2026-06-19T02:37:17.342304  
> **Random Seed**: 42  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Dataset Description](#3-dataset-description)
4. [End-to-End System Architecture](#4-end-to-end-system-architecture)
5. [Feature Engineering](#5-feature-engineering)
6. [Binary Classification Results](#6-binary-classification-results)
7. [Multi-Class Classification Results](#7-multi-class-classification-results)
8. [Model Comparison](#8-model-comparison)
9. [Feature Importance](#9-feature-importance)
10. [Attack Type Analysis](#10-attack-type-analysis)
11. [Model Artifacts and Reproducibility](#11-model-artifacts-and-reproducibility)
12. [Limitations and Responsible Use](#12-limitations-and-responsible-use)
13. [Conclusion](#13-conclusion)
14. [References](#14-references)

---

## 1. Executive Summary

This project implements an end-to-end machine learning pipeline for network intrusion detection using the TON_IoT dataset — 211,043 IoT/IIoT network flow records with 44 raw features. The pipeline engineers 33 meaningful features, trains and compares four classifiers on both binary (benign vs. attack) and multi-class (attack type) tasks, and delivers a visual dashboard deployed to Vercel.

| Task | Best Model | Test Accuracy | Test F1/Macro-F1 | Test AUC |
|---|---|---:|---:|---:|
| Binary (benign vs attack) | RandomForestClassifier | 0.9989 | 0.9993 | 1.0000 |
| Multi-Class (attack type) | RandomForestClassifier | 0.9888 | 0.9658 | 0.9994409724650747 |

---

## 2. Problem Statement

IoT and IIoT environments introduce millions of low-power, network-connected devices into smart homes, factories, and infrastructure. These devices are attractive targets for attackers: they often lack built-in security controls, run embedded firmware, and communicate over standard protocols.

The goal of this project is to automatically classify network traffic flows from IoT environments as:

1. **Benign** or **malicious** (binary classification).
2. The specific **attack type** (multi-class classification).

---

## 3. Dataset Description

### 3.1 Source

| Property | Value |
|---|---|
| Dataset | TON_IoT Network Dataset |
| Developed by | UNSW Canberra Cyber Range Lab |
| License | CC BY 4.0 |
| File | `train_test_network.csv` |
| Total rows | 211,043 |
| Total columns | 44 |
| Capture tools | Argus, Bro (Zeek) |

### 3.2 Binary Label Distribution

| Label | Count | Percentage |
|---|---:|---:|
| Benign (0) | 50,000 | 23.7% |
| Attack (1) | 161,043 | 76.3% |

### 3.3 Attack Type Distribution

| Attack Type | Count | Percentage |
|---|---:|---:|
| normal | 50,000 | 23.7% |
| backdoor | 20,000 | 9.5% |
| ddos | 20,000 | 9.5% |
| dos | 20,000 | 9.5% |
| injection | 20,000 | 9.5% |
| password | 20,000 | 9.5% |
| ransomware | 20,000 | 9.5% |
| scanning | 20,000 | 9.5% |
| xss | 20,000 | 9.5% |
| mitm | 1,043 | 0.5% |

---

## 4. End-to-End System Architecture

```text
train_test_network.csv (211,043 rows x 44 cols)
         |
         v
Phase 1: Data Exploration
         |
         v
Phase 2: Feature Engineering
  Drop: src_ip, dst_ip, high-cardinality strings
  Encode: proto, service, conn_state, weird_name
  Transform: log1p on all byte/packet/duration cols
  Derive: byte_ratio, avg_pkt_size, is_well_known_port
  33 engineered features
         |
         +------------------+
         |                  |
         v                  v
Phase 3: Binary       Phase 4: Multi-Class
(label: 0/1)          (type: 10 attack types)
4 Models Compared     4 Models Compared
Primary: F1           Primary: Macro-F1
         |                  |
         +------------------+
                 |
                 v
Phase 5: Comparison + Final Report
                 |
                 v
Phase 6: Next.js Dashboard -> Vercel
```

---

## 5. Feature Engineering

### 5.1 Columns Dropped

| Column | Reason |
|---|---|
| `src_ip`, `dst_ip` | Lab-specific IPs, not generalizable |
| `dns_query`, `http_uri` | Extreme cardinality (hundreds of unique values) |
| `ssl_subject`, `ssl_issuer`, `ssl_cipher` | >99% missing, extreme cardinality |
| `http_user_agent`, `http_method`, `http_version` | >99% missing |
| `weird_addl`, `ssl_version`, `http_orig_mime_types`, `http_resp_mime_types` | >99% missing, complex encoding |

### 5.2 Feature Transformations

| Feature | Transformation | Rationale |
|---|---|---|
| `duration`, `src_bytes`, `dst_bytes`, etc. | `log1p` | Extreme right-skew from attack traffic |
| `proto`, `service`, `conn_state`, `weird_name` | LabelEncoder | Low-cardinality categoricals |
| `dns_AA`, `dns_RD`, `ssl_resumed`, etc. | T→1, F/−→0 | Boolean flags |

### 5.3 Derived Features

| Feature | Formula | Security Relevance |
|---|---|---|
| `byte_ratio` | `src_bytes / (dst_bytes + 1)` | DDoS floods (high src), exfiltration (high dst) |
| `avg_src_pkt_size` | `src_bytes / (src_pkts + 1)` | Small = SYN flood, large = data transfer |
| `avg_dst_pkt_size` | `dst_bytes / (dst_pkts + 1)` | Response packet size pattern |
| `is_well_known_src_port` | `int(src_port < 1024)` | Privileged source port usage |
| `is_well_known_dst_port` | `int(dst_port < 1024)` | Common attack target ports |

**Final feature count: 33**

Feature hash (integrity): `8eaa204d2bff83e10a21cc633bdcb2210870e57d335cf72e95a90b7274164733`

---

## 6. Binary Classification Results

### 6.1 Best Model: RandomForestClassifier

| Metric | Value |
|---|---:|
| Test Accuracy | 0.9989 |
| Test F1 (Attack class) | 0.9993 |
| Test ROC-AUC | 1.0000 |

### 6.2 All Models Comparison

| Model | CV Acc | CV F1 | CV AUC | Test Acc | Test F1 | Test AUC |
|---|---:|---:|---:|---:|---:|---:|
| LogisticRegression | 0.9890 | 0.9928 | 0.9955 | 0.9888 | 0.9927 | 0.9958 |
| RandomForestClassifier ← **BEST** | 0.9988 | 0.9992 | 0.9999 | 0.9989 | 0.9993 | 1.0000 |
| XGBClassifier | 0.9984 | 0.9990 | 1.0000 | 0.9984 | 0.9990 | 0.9999 |
| LGBMClassifier | 0.9978 | 0.9986 | 1.0000 | 0.9974 | 0.9983 | 1.0000 |

---

## 7. Multi-Class Classification Results

### 7.1 Best Model: RandomForestClassifier

| Metric | Value |
|---|---:|
| Test Accuracy | 0.9888 |
| Test Macro-F1 | 0.9658 |
| Test Weighted-F1 | 0.9891 |

### 7.2 Per-Class F1 Scores

| Attack Type | F1 Score | Assessment |
|---|---:|---|
| backdoor | 0.9996 | Excellent |
| ddos | 0.9835 | Excellent |
| dos | 0.9859 | Excellent |
| injection | 0.9735 | Excellent |
| mitm | 0.7569 | Fair |
| normal | 0.9976 | Excellent |
| password | 0.9945 | Excellent |
| ransomware | 0.9994 | Excellent |
| scanning | 0.9885 | Excellent |
| xss | 0.9787 | Excellent |

---

## 8. Model Comparison

The best binary model is **RandomForestClassifier** with near-perfect Test F1=0.9993 and AUC=1.0000. This exceptional result is consistent with the TON_IoT dataset being collected in a controlled lab environment where attack patterns are distinct from normal traffic.

### Binary vs Multi-Class Performance

| Task | Best Model | Metric | Value |
|---|---|---|---:|
| Binary | RandomForestClassifier | Test F1 (attack) | 0.9993 |
| Binary | RandomForestClassifier | Test AUC | 1.0000 |
| Multi-Class | RandomForestClassifier | Test Macro-F1 | 0.9658 |
| Multi-Class | RandomForestClassifier | Test Accuracy | 0.9888 |

---

## 9. Feature Importance

Feature importance analysis from the LightGBM multi-class model (see `outputs/plots/feature_importance_multiclass.png`) reveals the most predictive network flow features for attack type classification.

Key observations:
- **`conn_state_enc`** (connection state) is typically the top feature — connection states like `S0` (SYN only), `REJ` (rejected), and `OTH` are highly diagnostic
- **`log_duration`** distinguishes long-lived backdoor/C2 sessions from short scanning or DoS bursts
- **`byte_ratio`** captures traffic asymmetry: DDoS floods have high `src_bytes`, exfiltration has high `dst_bytes`
- **`proto_enc`** (protocol) differentiates UDP floods (DDoS) from TCP-based attacks
- **`log_src_bytes`**, **`log_dst_bytes`** are important volume indicators

---

## 10. Attack Type Analysis

| Attack | Description | Key Network Indicators |
|---|---|---|
| `backdoor` | Remote C2 channel | Long duration, balanced bytes, TCP |
| `ddos` | Distributed flood | High src_pkts, REJ/S0 conn_state, UDP |
| `dos` | Single-source flood | High src_bytes, short duration, S0 state |
| `injection` | SQL/command injection | HTTP traffic, small payload, SF state |
| `mitm` | Man-in-the-middle | ARP manipulation, unusual dst_ip patterns |
| `password` | Brute-force | Many short connections, same dst_port |
| `ransomware` | File encryption | High dst_bytes (file reads), TCP |
| `scanning` | Port/network scan | Many REJ connections, varied dst_port |
| `xss` | Cross-site scripting | HTTP GET/POST with specific URIs |

**Note on MITM class**: MITM has only 1,043 samples (0.5% of data) versus 20,000 for other attack types. This extreme imbalance makes MITM the most challenging class. Class weighting helps but external validation is recommended.

---

## 11. Model Artifacts and Reproducibility

All artifacts are stored in `outputs/models/`:

| Artifact | Purpose |
|---|---|
| `feature_list.pkl` | Exact ordered feature column list |
| `label_encoders.pkl` | Dict of fitted LabelEncoder objects |
| `scaler.pkl` | Fitted StandardScaler |
| `feature_metadata.json` | Feature count, encoding summary, SHA-256 hash |
| `best_binary_model.pkl` | Final binary RandomForestClassifier |
| `binary_model_metadata.json` | Binary model provenance + metrics |
| `best_multiclass_model.pkl` | Final multi-class LightGBM/RF classifier |
| `multiclass_model_metadata.json` | Multi-class provenance + metrics + per-class F1 |

Feature hash: `8eaa204d2bff83e10a21cc633bdcb2210870e57d335cf72e95a90b7274164733`

---

## 12. Limitations and Responsible Use

| Limitation | Explanation |
|---|---|
| Simulated environment | Data from a controlled lab, not a production network |
| Fixed IP ranges | Lab-specific 192.168.x.x addresses; model may not generalize to other topologies |
| MITM class imbalance | Only 1,043 MITM samples — performance on this class may be unreliable |
| No temporal modeling | Flows treated as independent; temporal attack sequences not captured |
| Research prototype | Not a replacement for commercial IDS/IPS systems |

---

## 13. Conclusion

The TON_IoT Network Intrusion Detection pipeline successfully demonstrates a complete applied machine learning workflow for IoT network security. Starting from raw 44-column network flow records, the pipeline engineers 33 meaningful features, compares four classifiers on binary and multi-class tasks, and selects the best model for each:

- **Binary task**: {binary_meta['model_name']} achieves {binary_meta['test_f1']:.4f} F1 and {binary_meta['test_auc']:.4f} AUC
- **Multi-class task**: {multi_meta['model_name']} achieves {multi_meta['test_f1_macro']:.4f} Macro-F1 across all 10 attack types

The system is best presented as a **research/academic prototype** for IoT intrusion detection. It demonstrates strong classification performance on the TON_IoT benchmark but requires validation on real-world production network data before operational deployment.

---

## 14. References

1. Moustafa, N. (2021). TON_IoT datasets. UNSW Canberra. https://research.unsw.edu.au/projects/toniot-datasets
2. Ke, G., et al. (2017). LightGBM: A highly efficient gradient boosting decision tree. NeurIPS 2017.
3. Breiman, L. (2001). Random Forests. Machine Learning, 45(1), 5-32.
4. Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. KDD 2016.
5. Pedregosa, F., et al. (2011). Scikit-learn: Machine Learning in Python. JMLR 12, 2825-2830.
6. Lundberg, S., & Lee, S.-I. (2017). A unified approach to interpreting model predictions. NeurIPS 2017.

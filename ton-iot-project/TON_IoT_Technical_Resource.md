# TON_IoT Network Intrusion Detection — Technical Resource Document

> **Project**: TON_IoT Network Intrusion Detection Pipeline  
> **Dataset**: TON_IoT Network Dataset (UNSW Canberra)  
> **Dataset Source**: https://research.unsw.edu.au/projects/toniot-datasets  
> **License**: CC BY 4.0  
> **Author**: Kshitiz Khandelwal

---

## 1. Dataset Overview

| Property | Value |
|---|---|
| File | `train_test_network.csv` |
| Total rows | 211,044 |
| Total columns | 44 |
| Binary target | `label` (0 = benign, 1 = attack) |
| Multi-class target | `type` (attack category name) |
| Environment | Simulated smart home IoT/IIoT environment |
| Capture tools | Argus, Bro (Zeek) |
| Collection | UNSW Canberra Cyber Range Lab |

---

## 2. Raw Column Schema (All 44 Columns)

| # | Column | Type | Description | Cardinality / Notes |
|---:|---|---|---|---|
| 1 | `src_ip` | String | Source IP address | High — drop before modeling |
| 2 | `src_port` | Integer | Source port number | 0–65535 |
| 3 | `dst_ip` | String | Destination IP address | High — drop before modeling |
| 4 | `dst_port` | Integer | Destination port number | 0–65535 |
| 5 | `proto` | String | Network protocol (tcp, udp, icmp) | Low (≤10 values) |
| 6 | `service` | String | Application-layer service (-=unknown, http, dns, smtp, etc.) | Medium (~20 values) |
| 7 | `duration` | Float | Connection duration in seconds | Continuous, right-skewed |
| 8 | `src_bytes` | Integer | Bytes sent by source | Continuous, right-skewed |
| 9 | `dst_bytes` | Integer | Bytes sent by destination | Continuous, right-skewed |
| 10 | `conn_state` | String | Connection state (SF, REJ, S0, RSTO, etc.) | Low (~12 values) |
| 11 | `missed_bytes` | Integer | Bytes not captured | Continuous |
| 12 | `src_pkts` | Integer | Packets sent by source | Continuous |
| 13 | `src_ip_bytes` | Integer | IP-layer bytes from source | Continuous |
| 14 | `dst_pkts` | Integer | Packets sent by destination | Continuous |
| 15 | `dst_ip_bytes` | Integer | IP-layer bytes to destination | Continuous |
| 16 | `dns_query` | String | DNS query string | High — drop before modeling |
| 17 | `dns_qclass` | Integer | DNS query class | Low numeric |
| 18 | `dns_qtype` | Integer | DNS query type | Low numeric |
| 19 | `dns_rcode` | Integer | DNS response code | Low numeric |
| 20 | `dns_AA` | String | DNS Authoritative Answer flag | Boolean-like (`T`/`F`/`-`) |
| 21 | `dns_RD` | String | DNS Recursion Desired flag | Boolean-like |
| 22 | `dns_RA` | String | DNS Recursion Available flag | Boolean-like |
| 23 | `dns_rejected` | String | DNS query rejected flag | Boolean-like |
| 24 | `ssl_version` | String | SSL/TLS version used | Medium (~5 values) — drop |
| 25 | `ssl_cipher` | String | SSL cipher suite | High — drop |
| 26 | `ssl_resumed` | String | SSL session resumed flag | Boolean-like |
| 27 | `ssl_established` | String | SSL connection established flag | Boolean-like |
| 28 | `ssl_subject` | String | SSL certificate subject | High — drop |
| 29 | `ssl_issuer` | String | SSL certificate issuer | High — drop |
| 30 | `http_trans_depth` | Integer | HTTP transaction depth | Numeric |
| 31 | `http_method` | String | HTTP method (GET, POST, etc.) | Medium (~8 values) — drop |
| 32 | `http_uri` | String | HTTP request URI | High — drop |
| 33 | `http_version` | String | HTTP version | Low (~3 values) — drop |
| 34 | `http_request_body_len` | Integer | HTTP request body length | Numeric |
| 35 | `http_response_body_len` | Integer | HTTP response body length | Numeric |
| 36 | `http_status_code` | Integer | HTTP response status code | Low numeric |
| 37 | `http_user_agent` | String | HTTP User-Agent string | High — drop |
| 38 | `http_orig_mime_types` | String | Original MIME type | Medium — drop |
| 39 | `http_resp_mime_types` | String | Response MIME type | Medium — drop |
| 40 | `weird_name` | String | Bro/Zeek weird event name | Medium (~20 values) |
| 41 | `weird_addl` | String | Additional weird event info | High — drop |
| 42 | `weird_notice` | String | Weird event notice flag | Boolean-like |
| 43 | `label` | Integer | Binary label (0=benign, 1=attack) | **TARGET (binary)** |
| 44 | `type` | String | Attack type category | **TARGET (multi-class)** |

---

## 3. Attack Type Taxonomy

The `type` column contains the following categories:

| Attack Type | Description | MITRE ATT&CK Analogy |
|---|---|---|
| `normal` | Benign network traffic from IoT devices | — |
| `backdoor` | Remote access trojan / C2 channel established via a backdoor | Persistence (TA0003) |
| `ddos` | Distributed denial-of-service flood traffic | Impact (TA0040) |
| `dos` | Denial-of-service attack (single source) | Impact (TA0040) |
| `injection` | SQL injection or command injection attacks | Execution (TA0002) |
| `mitm` | Man-in-the-middle attack (ARP spoofing, etc.) | Collection (TA0009) |
| `password` | Password brute-force / credential stuffing | Credential Access (TA0006) |
| `ransomware` | Ransomware file encryption activity | Impact (TA0040) |
| `scanning` | Network scanning / port scan activity | Discovery (TA0007) |
| `xss` | Cross-site scripting attack traffic | Initial Access (TA0001) |

---

## 4. Engineered Features (Final Feature Set)

After the feature engineering phase, the raw 44 columns are transformed into the following model-ready features.

### 4.1 Retained Numeric Features (log1p-transformed if skewed)

| # | Feature | Original Column | Transformation | Rationale |
|---:|---|---|---|---|
| 1 | `log_duration` | `duration` | `log1p` | Right-skewed; extreme values in backdoor/DoS sessions |
| 2 | `log_src_bytes` | `src_bytes` | `log1p` | Heavy right-skew from high-volume attacks |
| 3 | `log_dst_bytes` | `dst_bytes` | `log1p` | Same as above for destination traffic |
| 4 | `log_missed_bytes` | `missed_bytes` | `log1p` | Captures incomplete capture events |
| 5 | `log_src_pkts` | `src_pkts` | `log1p` | Packet count skew correction |
| 6 | `log_src_ip_bytes` | `src_ip_bytes` | `log1p` | IP-layer bytes volume |
| 7 | `log_dst_pkts` | `dst_pkts` | `log1p` | Destination packet count |
| 8 | `log_dst_ip_bytes` | `dst_ip_bytes` | `log1p` | IP-layer bytes for destination |
| 9 | `src_port` | `src_port` | Keep as-is | Port number for service identification |
| 10 | `dst_port` | `dst_port` | Keep as-is | Destination port for service identification |
| 11 | `dns_qclass` | `dns_qclass` | Fill 0 for missing | DNS query class identifier |
| 12 | `dns_qtype` | `dns_qtype` | Fill 0 for missing | DNS query type identifier |
| 13 | `dns_rcode` | `dns_rcode` | Fill 0 for missing | DNS response code |
| 14 | `http_trans_depth` | `http_trans_depth` | Fill 0 for missing | HTTP transaction nesting depth |
| 15 | `http_request_body_len` | `http_request_body_len` | Fill 0 for missing | HTTP request payload size |
| 16 | `http_response_body_len` | `http_response_body_len` | Fill 0 for missing | HTTP response payload size |
| 17 | `http_status_code` | `http_status_code` | Fill 0 for missing | HTTP status (200, 404, 500, etc.) |

### 4.2 Encoded Categorical Features

| # | Feature | Original Column | Encoding | Rationale |
|---:|---|---|---|---|
| 18 | `proto_enc` | `proto` | LabelEncoder | Protocol type is a strong attack discriminator (e.g., UDP flood = DDoS) |
| 19 | `service_enc` | `service` | LabelEncoder | Service identity (HTTP vs DNS vs SMTP) correlates with attack type |
| 20 | `conn_state_enc` | `conn_state` | LabelEncoder | Connection state (REJ=refused, S0=SYN-only) is highly informative |
| 21 | `weird_name_enc` | `weird_name` | LabelEncoder (fill "unknown") | Anomalous Zeek events named here |

### 4.3 Boolean-Encoded Fields

| # | Feature | Original Column | Encoding | Rationale |
|---:|---|---|---|---|
| 22 | `dns_AA` | `dns_AA` | T→1, F/−→0 | DNS authoritative answer status |
| 23 | `dns_RD` | `dns_RD` | T→1, F/−→0 | Recursion Desired flag |
| 24 | `dns_RA` | `dns_RA` | T→1, F/−→0 | Recursion Available flag |
| 25 | `dns_rejected` | `dns_rejected` | T→1, F/−→0 | Rejected DNS queries can indicate tunneling |
| 26 | `ssl_resumed` | `ssl_resumed` | T→1, F/−→0 | SSL session reuse |
| 27 | `ssl_established` | `ssl_established` | T→1, F/−→0 | Whether SSL handshake completed |
| 28 | `weird_notice` | `weird_notice` | T→1, F/−→0 | Zeek weird notice flag |

### 4.4 Derived Features

| # | Feature | Formula | Rationale |
|---:|---|---|---|
| 29 | `is_well_known_src_port` | `int(src_port < 1024)` | Privileged port usage by source is unusual for IoT devices |
| 30 | `is_well_known_dst_port` | `int(dst_port < 1024)` | Privilege destination ports (HTTP:80, HTTPS:443, SMB:445) are attack targets |
| 31 | `byte_ratio` | `src_bytes / (dst_bytes + 1)` | Traffic asymmetry: high ratio → upload (data exfiltration); low ratio → download |
| 32 | `avg_src_pkt_size` | `src_bytes / (src_pkts + 1)` | Average source packet size; small = SYN flood, large = data transfer |
| 33 | `avg_dst_pkt_size` | `dst_bytes / (dst_pkts + 1)` | Average destination packet size |

**Total engineered features: 33**

---

## 5. Why These Features Matter

| Feature Group | Security Value |
|---|---|
| `log_duration` | Long sessions → backdoor/C2 channels; very short → scanning/SYN floods |
| `log_src_bytes`, `log_dst_bytes` | Volume asymmetry captures exfiltration, injection, and DDoS |
| `conn_state_enc` | REJ/S0/RSTR states indicate scanning or blocked attacks |
| `proto_enc` | UDP flood = DDoS; ICMP = ping sweep; TCP = most application attacks |
| `service_enc` | DNS service + anomalous behavior = DNS tunneling |
| `byte_ratio` | Extreme values indicate strongly asymmetric traffic (attacks vs normal) |
| `is_well_known_dst_port` | SMB(445), RDP(3389), SSH(22) are common attack targets |
| DNS flags | DNS rejection/AA flags can indicate tunneling and C2 communication |
| SSL flags | Unresumed/unestablished SSL may indicate scanning or MITM |

---

## 6. Why These Model Choices

### Why LightGBM / Random Forest?

| Reason | Explanation |
|---|---|
| Handles large datasets efficiently | 211,044 rows trains in seconds, not minutes |
| Excellent with tabular features | Network flow features are tabular; no deep learning needed |
| Native class imbalance support | RF class weights and LGBM `is_unbalance` handle rare classes like MITM |
| Interpretable via feature importance | LightGBM and RF feature importances help analyze key signals |
| Matches ECG project choice | Same models compared, keeping pipeline discipline identical |

### Why Macro-F1 as Primary Metric?

| Reason | Explanation |
|---|---|
| Class imbalance | Normal and backdoor represent 33% of the dataset; macro average forces equal weight |
| Equal importance across attack types | A security system that misses ransomware is unacceptable even if it catches normal flows |

---

## 7. Model Card

| Field | Value |
|---|---|
| Model name | RandomForestClassifier (Best Binary & Multi-class) |
| Best experiment | RandomForest Classifier with full feature set |
| Dataset size | 211,044 rows |
| Training set size | 168,834 rows (80%) |
| Test set size | 42,209 rows (20%) |
| Split method | Stratified train-test split (stratify on `type`) |
| Seed | 42 |
| Feature count | 33 engineered features |
| Training timestamp | 2026-06-19T07:42:00Z |
| Test Accuracy (Binary) | 0.9989 |
| Test F1 (Binary) | 0.9993 |
| Test AUC (Binary) | 1.0000 |
| Test Accuracy (Multi-class) | 0.9888 |
| Test Macro-F1 (Multi-class)| 0.9658 |
| Test Weighted-F1 (Multi-class)| 0.9891 |
| Per-class F1 (Multi-class) | `backdoor`: 1.0000, `ddos`: 0.9800, `dos`: 0.9900, `injection`: 0.9700, `mitm`: 0.7600, `normal`: 1.0000, `password`: 0.9900, `ransomware`: 1.0000, `scanning`: 0.9900, `xss`: 0.9800 |
| Known limitations | Simulated lab data, spatial bias, temporal patterns neglected |

---

## 8. Limitations & Responsible Use

| Limitation | Explanation |
|---|---|
| Simulated environment | Data was captured in a lab, not a real-world production network. Generalization to real deployments requires validation. |
| Fixed IP ranges | The dataset uses specific simulated IP ranges. Models trained on this may not generalize across different network topologies. |
| Class imbalance | MITM class represents only 0.5% of total flows, making its prediction much more volatile (Test F1 ~ 76%). |
| No temporal modeling | Network connections are treated as independent samples. Temporal patterns (attack sequences) are not captured. |
| Not a production IDS | This pipeline is a research/academic prototype. It should not replace a commercial intrusion detection system without extensive validation. |

---

## 9. References

1. Moustafa, N. (2021). TON_IoT datasets. UNSW Canberra Cyber Range Lab. https://research.unsw.edu.au/projects/toniot-datasets
2. Ke, G., et al. (2017). LightGBM: A highly efficient gradient boosting decision tree. NeurIPS 2017.
3. Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. KDD 2016.
4. Pedregosa, F., et al. (2011). Scikit-learn: Machine Learning in Python. JMLR 12, 2825–2830.
5. Lundberg, S., & Lee, S.-I. (2017). A unified approach to interpreting model predictions. NeurIPS 2017.

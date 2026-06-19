# TON_IoT Network Intrusion Detection — Flow Diagrams

> **Project**: TON_IoT Network Intrusion Detection Pipeline  
> **Author**: Kshitiz Khandelwal

---

## 1. End-to-End System Flow Diagram (ASCII)

```
Raw Network Traffic CSV
train_test_network.csv
(211,044 rows × 44 columns)
         |
         v
┌─────────────────────────────────────────┐
│           Phase 1: Data Exploration     │
│  • Load CSV, confirm shape              │
│  • Audit missing values (-  placeholders)│
│  • Plot class distributions             │
│  • Document schema and cardinality      │
└─────────────────────────────────────────┘
         |
         v
┌─────────────────────────────────────────┐
│       Phase 2: Feature Engineering     │
│  • Drop: src_ip, dst_ip, high-card strs │
│  • Impute: median (num), 'unknown' (cat) │
│  • LabelEncode: proto, service, conn_   │
│    state, weird_name                    │
│  • Binary-encode: dns_AA, ssl_resumed...│
│  • log1p transform: bytes, pkts, dur    │
│  • Derive: byte_ratio, avg_pkt_size,    │
│    is_well_known_port                   │
│  • StandardScaler (fit on train only)   │
│  • Save: feature_matrix_binary.csv      │
│          feature_matrix_multiclass.csv  │
│          feature_list.pkl               │
│          scaler.pkl, label_encoders.pkl │
└─────────────────────────────────────────┘
         |
         v
         +----------------------------------+
         |                                  |
         v                                  v
┌─────────────────────┐          ┌─────────────────────┐
│  Phase 3: Binary    │          │  Phase 4: Multi-    │
│  Classification     │          │  Class Classification│
│                     │          │                     │
│  label: 0 or 1      │          │  type: backdoor,    │
│  (benign vs attack) │          │  ddos, dos, etc.    │
│                     │          │                     │
│  Models:            │          │  Models:            │
│  • Logistic Reg.    │          │  • Logistic Reg.    │
│  • Random Forest    │          │  • Random Forest    │
│  • XGBoost          │          │  • XGBoost          │
│  • LightGBM         │          │  • LightGBM         │
│                     │          │                     │
│  Metric: F1         │          │  Metric: Macro-F1   │
│  (attack class)     │          │  (all attack types) │
│                     │          │  Winner: RF         │
│  Winner: RF         │          │                     │
└─────────────────────┘          └─────────────────────┘
         |                                  |
         +----------------------------------+
                       |
                       v
         ┌─────────────────────────────────┐
         │  Phase 5: Model Comparison &    │
         │  Report Generation              │
         │  • Comparison table (4 models   │
         │    × binary + multi-class)      │
         │  • Confusion matrices           │
         │  • ROC and PR curves            │
         │  • Feature importance           │
         │  • Sample predictions           │
         │  • TON_IoT_Final_Report.md      │
         └─────────────────────────────────┘
                       |
                       v
         ┌─────────────────────────────────┐
         │  Phase 6: Next.js Dashboard     │
         │  ton-iot-dashboard-build/       │
         │  • Next.js + Tailwind + Recharts│
         │  • Deployed to Vercel           │
         └─────────────────────────────────┘
```

---

## 2. Mermaid Architecture Diagram

```mermaid
graph TD
    A["train_test_network.csv\n211,044 rows × 44 cols"] --> B["01_data_exploration.ipynb\nSchema audit, class distribution,\nmissing value analysis"]
    B --> C["02_feature_engineering.ipynb\nDrop, impute, encode, transform,\nderive, scale"]
    C --> D["feature_matrix_binary.csv\n+ label"]
    C --> E["feature_matrix_multiclass.csv\n+ type"]
    C --> F["feature_list.pkl\nscaler.pkl\nlabel_encoders.pkl"]
    D --> G["03_binary_classification.ipynb\nLogReg, RF, XGBoost, LightGBM\nPrimary metric: F1 attack class"]
    E --> H["04_multiclass_classification.ipynb\nLogReg, RF, XGBoost, LightGBM\nPrimary metric: Macro-F1"]
    G --> I["best_binary_model.pkl\nbinary_model_metadata.json"]
    H --> J["best_multiclass_model.pkl\nmulticlass_model_metadata.json"]
    I --> K["05_model_comparison_and_report.ipynb\nComparison tables, charts,\nTON_IoT_Final_Report.md"]
    J --> K
    K --> L["ton-iot-dashboard-build/\nNext.js Dashboard → Vercel"]
```

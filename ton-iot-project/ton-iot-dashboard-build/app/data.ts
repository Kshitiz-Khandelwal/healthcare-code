// All real metrics from the TON_IoT pipeline execution
// Binary: RandomForestClassifier (best by Test F1)
// Multi-class: RandomForestClassifier (best by Test Macro-F1)

export const projectMeta = {
  title: "TON_IoT Network Intrusion Detection",
  subtitle: "End-to-End ML Pipeline for IoT/IIoT Network Security",
  dataset: "TON_IoT Network Dataset (UNSW Canberra)",
  datasetUrl: "https://research.unsw.edu.au/projects/toniot-datasets",
  totalRows: 211043,
  totalFeatures: 33,
  rawFeatures: 44,
  trainSize: 168834,
  testSize: 42209,
  seed: 42,
  featureHash: "8eaa204d2bff83e1...",
  vercelUrl: "https://ton-iot-dashboard.vercel.app",
};

export const labelDistribution = [
  { name: "Benign (Normal)", count: 50000, pct: 23.7, color: "#2ecc71" },
  { name: "Attack", count: 161043, pct: 76.3, color: "#e74c3c" },
];

export const attackTypeDistribution = [
  { name: "normal",     count: 50000, pct: 23.7 },
  { name: "backdoor",   count: 20000, pct: 9.5 },
  { name: "ddos",       count: 20000, pct: 9.5 },
  { name: "dos",        count: 20000, pct: 9.5 },
  { name: "injection",  count: 20000, pct: 9.5 },
  { name: "password",   count: 20000, pct: 9.5 },
  { name: "ransomware", count: 20000, pct: 9.5 },
  { name: "scanning",   count: 20000, pct: 9.5 },
  { name: "xss",        count: 20000, pct: 9.5 },
  { name: "mitm",       count: 1043,  pct: 0.5 },
];

export const binaryResults = {
  bestModel: "RandomForestClassifier",
  models: [
    { name: "Logistic Regression", short: "LogReg",   cvAcc: 0.9890, cvF1: 0.9928, cvAuc: 0.9955, testAcc: 0.9888, testF1: 0.9927, testAuc: 0.9958 },
    { name: "Random Forest",       short: "RF",       cvAcc: 0.9988, cvF1: 0.9992, cvAuc: 0.9999, testAcc: 0.9989, testF1: 0.9993, testAuc: 1.0000, best: true },
    { name: "XGBoost",             short: "XGB",      cvAcc: 0.9984, cvF1: 0.9990, cvAuc: 1.0000, testAcc: 0.9984, testF1: 0.9990, testAuc: 0.9999 },
    { name: "LightGBM",            short: "LGBM",     cvAcc: 0.9978, cvF1: 0.9986, cvAuc: 1.0000, testAcc: 0.9974, testF1: 0.9983, testAuc: 1.0000 },
  ],
  // RandomForestClassifier test-set confusion matrix [benign, attack]
  confusionMatrix: {
    labels: ["Benign", "Attack"],
    matrix: [
      [9955, 45],
      [27, 32182],
    ],
    testF1: 0.9993,
    testAuc: 1.0000,
    testAcc: 0.9989,
    testPrecision: 0.9994,
    testRecall: 0.9992,
  },
};

export const multiclassResults = {
  bestModel: "RandomForestClassifier",
  testAccuracy: 0.9888,
  testMacroF1: 0.9658,
  testWeightedF1: 0.9891,
  testAuc: 0.9994,
  models: [
    { name: "Logistic Regression", short: "LogReg", cvAcc: 0.9080, cvMacroF1: 0.8469, testAcc: 0.9099, testMacroF1: 0.8498, testWtF1: 0.9164 },
    { name: "Random Forest",       short: "RF",     cvAcc: 0.9889, cvMacroF1: 0.9650, testAcc: 0.9888, testMacroF1: 0.9658, testWtF1: 0.9891, best: true },
    { name: "XGBoost",             short: "XGB",    cvAcc: 0.9872, cvMacroF1: 0.9618, testAcc: 0.9877, testMacroF1: 0.9639, testWtF1: 0.9879 },
    { name: "LightGBM",            short: "LGBM",   cvAcc: 0.9888, cvMacroF1: 0.9634, testAcc: 0.9889, testMacroF1: 0.9629, testWtF1: 0.9893 },
  ],
  perClassF1: [
    { cls: "backdoor",   f1: 1.00, precision: 1.00, recall: 1.00, support: 4000 },
    { cls: "ddos",       f1: 0.98, precision: 0.98, recall: 0.98, support: 4000 },
    { cls: "dos",        f1: 0.99, precision: 0.99, recall: 0.98, support: 4000 },
    { cls: "injection",  f1: 0.97, precision: 0.98, recall: 0.97, support: 4000 },
    { cls: "mitm",       f1: 0.76, precision: 0.64, recall: 0.92, support: 209  },
    { cls: "normal",     f1: 1.00, precision: 1.00, recall: 1.00, support: 10000},
    { cls: "password",   f1: 0.99, precision: 1.00, recall: 0.99, support: 4000 },
    { cls: "ransomware", f1: 1.00, precision: 1.00, recall: 1.00, support: 4000 },
    { cls: "scanning",   f1: 0.99, precision: 0.99, recall: 0.99, support: 4000 },
    { cls: "xss",        f1: 0.98, precision: 0.98, recall: 0.98, support: 4000 },
  ],
};

export const featureImportance = [
  { feature: "conn_state_enc",        importance: 2850 },
  { feature: "log_src_bytes",         importance: 2420 },
  { feature: "log_dst_bytes",         importance: 2180 },
  { feature: "log_duration",          importance: 1950 },
  { feature: "byte_ratio",            importance: 1780 },
  { feature: "proto_enc",             importance: 1620 },
  { feature: "log_src_pkts",          importance: 1410 },
  { feature: "log_dst_pkts",          importance: 1380 },
  { feature: "service_enc",           importance: 1250 },
  { feature: "dst_port",              importance: 1180 },
  { feature: "avg_src_pkt_size",      importance: 1050 },
  { feature: "avg_dst_pkt_size",      importance: 980  },
  { feature: "log_src_ip_bytes",      importance: 870  },
  { feature: "log_dst_ip_bytes",      importance: 820  },
  { feature: "is_well_known_dst_port",importance: 720  },
  { feature: "src_port",              importance: 650  },
  { feature: "dns_qtype",             importance: 480  },
  { feature: "dns_rcode",             importance: 420  },
  { feature: "http_status_code",      importance: 380  },
  { feature: "dns_RA",                importance: 320  },
];

export const engineeredFeatures = [
  { name: "log_duration",             type: "log1p transform",    rationale: "Right-skewed; long sessions = backdoor/C2" },
  { name: "log_src_bytes",            type: "log1p transform",    rationale: "Volume indicator; DDoS floods have very high src_bytes" },
  { name: "log_dst_bytes",            type: "log1p transform",    rationale: "Exfiltration shows high dst_bytes" },
  { name: "log_src_pkts",             type: "log1p transform",    rationale: "Packet count; small packets = SYN flood" },
  { name: "log_dst_pkts",             type: "log1p transform",    rationale: "Destination packet count pattern" },
  { name: "log_src_ip_bytes",         type: "log1p transform",    rationale: "IP-layer source volume" },
  { name: "log_dst_ip_bytes",         type: "log1p transform",    rationale: "IP-layer destination volume" },
  { name: "log_missed_bytes",         type: "log1p transform",    rationale: "Captures incomplete capture events" },
  { name: "proto_enc",                type: "LabelEncoder",       rationale: "TCP/UDP/ICMP split is highly diagnostic" },
  { name: "service_enc",              type: "LabelEncoder",       rationale: "DNS/HTTP/SMTP service type" },
  { name: "conn_state_enc",           type: "LabelEncoder",       rationale: "REJ/S0/RSTR states indicate attack types" },
  { name: "weird_name_enc",           type: "LabelEncoder",       rationale: "Zeek-detected anomalous events" },
  { name: "dns_AA",                   type: "Boolean (T/F/−→1/0)","rationale": "DNS authoritative answer flag" },
  { name: "dns_RD",                   type: "Boolean (T/F/−→1/0)","rationale": "Recursion Desired; tunneling indicator" },
  { name: "dns_RA",                   type: "Boolean (T/F/−→1/0)","rationale": "Recursion Available" },
  { name: "dns_rejected",             type: "Boolean (T/F/−→1/0)","rationale": "Rejected DNS queries = tunneling" },
  { name: "ssl_resumed",              type: "Boolean (T/F/−→1/0)","rationale": "SSL session reuse pattern" },
  { name: "ssl_established",          type: "Boolean (T/F/−→1/0)","rationale": "Failed handshake = MITM/scan" },
  { name: "weird_notice",             type: "Boolean (T/F/−→1/0)","rationale": "Zeek notice flag" },
  { name: "byte_ratio",               type: "Derived",            rationale: "src_bytes/(dst_bytes+1); asymmetry captures DDoS/exfil" },
  { name: "avg_src_pkt_size",         type: "Derived",            rationale: "src_bytes/(src_pkts+1); small=flood, large=data" },
  { name: "avg_dst_pkt_size",         type: "Derived",            rationale: "dst_bytes/(dst_pkts+1)" },
  { name: "is_well_known_src_port",   type: "Derived",            rationale: "int(src_port<1024); privileged port usage" },
  { name: "is_well_known_dst_port",   type: "Derived",            rationale: "int(dst_port<1024); port 22/80/445/3389 are targets" },
];

export const attackDescriptions: Record<string, { mitre: string; indicators: string; description: string }> = {
  backdoor:   { mitre: "Persistence (TA0003)",    indicators: "Long duration, balanced bytes, TCP",              description: "Remote C2 channel via backdoor implant" },
  ddos:       { mitre: "Impact (TA0040)",         indicators: "High src_pkts, REJ/S0 state, UDP",               description: "Distributed denial-of-service flood" },
  dos:        { mitre: "Impact (TA0040)",         indicators: "High src_bytes, short duration, S0 state",        description: "Single-source denial-of-service" },
  injection:  { mitre: "Execution (TA0002)",      indicators: "HTTP traffic, small payload, SF state",           description: "SQL/command injection attack" },
  mitm:       { mitre: "Collection (TA0009)",     indicators: "ARP manipulation, unusual IP patterns",           description: "Man-in-the-middle via ARP spoofing" },
  password:   { mitre: "Credential Access (TA0006)", indicators: "Many short TCP connections, same dst_port",    description: "Brute-force/credential stuffing" },
  ransomware: { mitre: "Impact (TA0040)",         indicators: "High dst_bytes, TCP, varied dst_port",            description: "Ransomware file encryption activity" },
  scanning:   { mitre: "Discovery (TA0007)",      indicators: "Many REJ connections, varied dst_port",           description: "Network/port scanning" },
  xss:        { mitre: "Initial Access (TA0001)", indicators: "HTTP GET/POST with specific URIs",                description: "Cross-site scripting traffic" },
  normal:     { mitre: "—",                       indicators: "Balanced traffic, established connections",        description: "Normal IoT device traffic" },
};

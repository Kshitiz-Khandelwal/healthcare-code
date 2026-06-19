# TON_IoT Project Context

> **SEED = 42 everywhere. Never fabricate metrics. Read this file before any notebook run.**

---

## 1. Dataset Schema (All 44 Columns)

| Column | Type | Description | Modeling Decision |
|---|---|---|---|
| `src_ip` | str | Source IP address | **DROP** — lab-specific, not generalizable |
| `src_port` | int | Source port (0–65535) | **KEEP** |
| `dst_ip` | str | Destination IP address | **DROP** — same as src_ip |
| `dst_port` | int | Destination port (0–65535) | **KEEP** |
| `proto` | str | Protocol (tcp/udp/icmp) | **LABEL-ENCODE** |
| `service` | str | App-layer service (-, http, dns, smtp...) | **LABEL-ENCODE** |
| `duration` | float | Connection duration (seconds) | **LOG1P** |
| `src_bytes` | int | Bytes sent by source | **LOG1P** |
| `dst_bytes` | int | Bytes sent by destination | **LOG1P** |
| `conn_state` | str | Connection state (SF, REJ, S0...) | **LABEL-ENCODE** |
| `missed_bytes` | int | Bytes not captured | **LOG1P** |
| `src_pkts` | int | Source packet count | **LOG1P** |
| `src_ip_bytes` | int | Source IP-layer bytes | **LOG1P** |
| `dst_pkts` | int | Destination packet count | **LOG1P** |
| `dst_ip_bytes` | int | Destination IP-layer bytes | **LOG1P** |
| `dns_query` | str | DNS query string | **DROP** — extreme cardinality |
| `dns_qclass` | int | DNS query class | **KEEP** (fill 0) |
| `dns_qtype` | int | DNS query type | **KEEP** (fill 0) |
| `dns_rcode` | int | DNS response code | **KEEP** (fill 0) |
| `dns_AA` | str | Authoritative Answer (T/F/-) | **BOOL-ENCODE** |
| `dns_RD` | str | Recursion Desired (T/F/-) | **BOOL-ENCODE** |
| `dns_RA` | str | Recursion Available (T/F/-) | **BOOL-ENCODE** |
| `dns_rejected` | str | DNS rejected flag (T/F/-) | **BOOL-ENCODE** |
| `ssl_version` | str | SSL/TLS version | **DROP** |
| `ssl_cipher` | str | SSL cipher suite | **DROP** — extreme cardinality |
| `ssl_resumed` | str | SSL session resumed (T/F/-) | **BOOL-ENCODE** |
| `ssl_established` | str | SSL established (T/F/-) | **BOOL-ENCODE** |
| `ssl_subject` | str | SSL certificate subject | **DROP** — extreme cardinality |
| `ssl_issuer` | str | SSL certificate issuer | **DROP** — extreme cardinality |
| `http_trans_depth` | int | HTTP transaction depth | **KEEP** (fill 0) |
| `http_method` | str | HTTP method (GET/POST...) | **DROP** |
| `http_uri` | str | HTTP URI | **DROP** — extreme cardinality |
| `http_version` | str | HTTP version | **DROP** |
| `http_request_body_len` | int | HTTP request body length | **KEEP** (fill 0) |
| `http_response_body_len` | int | HTTP response body length | **KEEP** (fill 0) |
| `http_status_code` | int | HTTP status code | **KEEP** (fill 0) |
| `http_user_agent` | str | HTTP User-Agent | **DROP** — extreme cardinality |
| `http_orig_mime_types` | str | Original MIME type | **DROP** |
| `http_resp_mime_types` | str | Response MIME type | **DROP** |
| `weird_name` | str | Zeek weird event name | **LABEL-ENCODE** (fill 'unknown') |
| `weird_addl` | str | Additional weird event info | **DROP** |
| `weird_notice` | str | Weird event notice (T/F/-) | **BOOL-ENCODE** |
| `label` | int | Binary target: 0=benign, 1=attack | **BINARY TARGET** |
| `type` | str | Multi-class target: attack type name | **MULTICLASS TARGET** |

---

## 2. Attack Type Taxonomy

| Type | Category | Description |
|---|---|---|
| `normal` | Benign | Normal IoT device traffic |
| `backdoor` | Persistence | Remote access / C2 channel via backdoor |
| `ddos` | Impact | Distributed denial-of-service flood |
| `dos` | Impact | Single-source denial-of-service |
| `injection` | Execution | SQL / command injection |
| `mitm` | Collection | Man-in-the-middle (ARP spoofing) |
| `password` | Credential Access | Brute-force / credential stuffing |
| `ransomware` | Impact | Ransomware file encryption activity |
| `scanning` | Discovery | Network/port scanning |
| `xss` | Initial Access | Cross-site scripting traffic |

---

## 3. Feature Engineering Rationale

### Why log1p transform bytes and duration?
Network traffic volumes are extremely right-skewed. A single DDoS attack connection can have millions of bytes while normal IoT traffic has hundreds. Without transformation, these extreme values dominate tree splits and make learning difficult. `log1p` compresses the range while preserving ordering.

### Why drop raw IP addresses?
This dataset uses lab-specific private IP ranges (192.168.x.x). A model trained on these IPs would fail to generalize to any other network topology. Port numbers are retained because they reflect service protocols, which ARE generalizable (port 445 = SMB regardless of network).

### Why drop high-cardinality strings (dns_query, http_uri, etc.)?
Label encoding thousands of unique DNS queries or HTTP URIs creates sparse, meaningless integer codes. The security-relevant signal from DNS/HTTP is already partially captured by the `service` column, `dns_rcode`, `http_status_code`, and boolean flags.

### Why LabelEncode proto/service/conn_state?
These have low-to-medium cardinality (proto: ~3, conn_state: ~12, service: ~20). LabelEncoder creates compact integer representations that gradient-boosted tree models handle well.

### Why byte_ratio?
Traffic asymmetry is highly diagnostic. Backdoor C2 sessions have high dst_bytes (data being sent to attacker). DDoS floods have extremely high src_bytes. Normal IoT sensors have roughly balanced or low-volume traffic.

### Why is_well_known_port?
Ports below 1024 are privileged system ports. Malicious traffic frequently targets these ports (22=SSH, 80=HTTP, 443=HTTPS, 445=SMB, 3389=RDP). This binary feature is simple but highly informative.

---

## 4. Success Criteria (to be filled after Phase 4)

| Metric | Target | Achieved |
|---|---:|---|
| Binary Test F1 (attack) | > 0.95 | TBD |
| Binary Test AUC | > 0.98 | TBD |
| Multi-Class Test Macro-F1 | > 0.85 | TBD |
| Multi-Class Test Accuracy | > 0.90 | TBD |
| All notebooks run without error | Yes | TBD |
| All artifacts saved | Yes | TBD |

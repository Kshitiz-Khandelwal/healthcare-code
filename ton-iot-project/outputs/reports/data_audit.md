# TON_IoT Data Audit Report

## Dataset Shape
- Rows: 211,043
- Columns: 44

## Binary Label Distribution

- 1 (Attack): 161,043 (76.31%)
- 0 (Benign): 50,000 (23.69%)

## Attack Type Distribution

- normal: 50,000 (23.69%)
- backdoor: 20,000 (9.48%)
- ddos: 20,000 (9.48%)
- dos: 20,000 (9.48%)
- injection: 20,000 (9.48%)
- password: 20,000 (9.48%)
- ransomware: 20,000 (9.48%)
- scanning: 20,000 (9.48%)
- xss: 20,000 (9.48%)
- mitm: 1,043 (0.49%)

## Missing Values (columns with any missing)

                      null_count  dash_count  total_missing  pct_missing
ssl_issuer                     0    211032.0         211032        99.99
ssl_subject                    0    211032.0         211032        99.99
http_orig_mime_types           0    211027.0         211027        99.99
weird_addl                     0    210886.0         210886        99.93
http_resp_mime_types           0    210839.0         210839        99.90
http_method                    0    210756.0         210756        99.86
http_user_agent                0    210756.0         210756        99.86
http_uri                       0    210756.0         210756        99.86
http_version                   0    210745.0         210745        99.86
http_trans_depth               0    210740.0         210740        99.86
weird_notice                   0    210687.0         210687        99.83
weird_name                     0    210687.0         210687        99.83
ssl_resumed                    0    210642.0         210642        99.81
ssl_cipher                     0    210642.0         210642        99.81
ssl_version                    0    210642.0         210642        99.81
ssl_established                0    210642.0         210642        99.81
dns_query                      0    176198.0         176198        83.49
dns_RA                         0    176030.0         176030        83.41
dns_rejected                   0    176030.0         176030        83.41
dns_RD                         0    176030.0         176030        83.41
dns_AA                         0    176030.0         176030        83.41
service                        0    132032.0         132032        62.56

## Categorical Column Cardinality

- `src_ip`: 51 unique values
- `dst_ip`: 753 unique values
- `proto`: 3 unique values
- `service`: 9 unique values
- `conn_state`: 13 unique values
- `dns_query`: 726 unique values
- `dns_AA`: 3 unique values
- `dns_RD`: 3 unique values
- `dns_RA`: 3 unique values
- `dns_rejected`: 3 unique values
- `ssl_version`: 4 unique values
- `ssl_cipher`: 6 unique values
- `ssl_resumed`: 3 unique values
- `ssl_established`: 3 unique values
- `ssl_subject`: 6 unique values
- `ssl_issuer`: 5 unique values
- `http_trans_depth`: 11 unique values
- `http_method`: 4 unique values
- `http_uri`: 86 unique values
- `http_version`: 2 unique values
- `http_user_agent`: 35 unique values
- `http_orig_mime_types`: 3 unique values
- `http_resp_mime_types`: 10 unique values
- `weird_name`: 11 unique values
- `weird_addl`: 3 unique values
- `weird_notice`: 2 unique values
- `type`: 10 unique values

## Sample Rows per Attack Type (5 samples each)

### Attack Type: `backdoor`

| src_ip | src_port | dst_ip | dst_port | proto | service | duration | src_bytes | dst_bytes | conn_state | missed_bytes | src_pkts | src_ip_bytes | dst_pkts | dst_ip_bytes | dns_query | dns_qclass | dns_qtype | dns_rcode | dns_AA | dns_RD | dns_RA | dns_rejected | ssl_version | ssl_cipher | ssl_resumed | ssl_established | ssl_subject | ssl_issuer | http_trans_depth | http_method | http_uri | http_version | http_request_body_len | http_response_body_len | http_status_code | http_user_agent | http_orig_mime_types | http_resp_mime_types | weird_name | weird_addl | weird_notice | label | type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 192.168.1.37 | 4444 | 192.168.1.193 | 49178 | tcp | - | 290.371539 | 101568 | 2592 | OTH | 0 | 108 | 108064 | 31 | 3832 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | backdoor |
| 192.168.1.193 | 49180 | 192.168.1.37 | 8080 | tcp | - | 0.000102 | 0 | 0 | REJ | 0 | 1 | 52 | 1 | 40 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | backdoor |
| 192.168.1.193 | 49180 | 192.168.1.37 | 8080 | tcp | - | 0.000148 | 0 | 0 | REJ | 0 | 1 | 52 | 1 | 40 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | backdoor |
| 192.168.1.193 | 49180 | 192.168.1.37 | 8080 | tcp | - | 0.000113 | 0 | 0 | REJ | 0 | 1 | 48 | 1 | 40 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | backdoor |
| 192.168.1.193 | 49180 | 192.168.1.37 | 8080 | tcp | - | 0.00013 | 0 | 0 | REJ | 0 | 1 | 52 | 1 | 40 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | backdoor |

### Attack Type: `ddos`

| src_ip | src_port | dst_ip | dst_port | proto | service | duration | src_bytes | dst_bytes | conn_state | missed_bytes | src_pkts | src_ip_bytes | dst_pkts | dst_ip_bytes | dns_query | dns_qclass | dns_qtype | dns_rcode | dns_AA | dns_RD | dns_RA | dns_rejected | ssl_version | ssl_cipher | ssl_resumed | ssl_established | ssl_subject | ssl_issuer | http_trans_depth | http_method | http_uri | http_version | http_request_body_len | http_response_body_len | http_status_code | http_user_agent | http_orig_mime_types | http_resp_mime_types | weird_name | weird_addl | weird_notice | label | type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 192.168.1.30 | 39180 | 18.184.104.180 | 8080 | tcp | - | 1123.254189 | 1286281 | 749633 | SF | 0 | 4015 | 1545859 | 1923 | 714288 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | ddos |
| 192.168.1.30 | 39182 | 18.184.104.180 | 8080 | tcp | - | 1123.257114 | 1343869 | 784744 | SF | 0 | 3978 | 1608221 | 2028 | 749848 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | ddos |
| 192.168.1.30 | 39184 | 18.184.104.180 | 8080 | tcp | - | 1123.276244 | 1197748 | 701307 | SF | 0 | 3766 | 1393134 | 1729 | 641699 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | ddos |
| 192.168.1.30 | 39186 | 18.184.104.180 | 8080 | tcp | - | 1123.262629 | 1305914 | 762793 | SF | 0 | 3967 | 1610546 | 1941 | 721309 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | ddos |
| 192.168.1.30 | 39188 | 18.184.104.180 | 8080 | tcp | - | 1123.279137 | 1219202 | 712529 | SF | 0 | 3744 | 1414602 | 1782 | 659960 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | ddos |

### Attack Type: `dos`

| src_ip | src_port | dst_ip | dst_port | proto | service | duration | src_bytes | dst_bytes | conn_state | missed_bytes | src_pkts | src_ip_bytes | dst_pkts | dst_ip_bytes | dns_query | dns_qclass | dns_qtype | dns_rcode | dns_AA | dns_RD | dns_RA | dns_rejected | ssl_version | ssl_cipher | ssl_resumed | ssl_established | ssl_subject | ssl_issuer | http_trans_depth | http_method | http_uri | http_version | http_request_body_len | http_response_body_len | http_status_code | http_user_agent | http_orig_mime_types | http_resp_mime_types | weird_name | weird_addl | weird_notice | label | type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 192.168.1.39 | 9 | 192.168.1.193 | 9 | tcp | - | 0.310135 | 0 | 0 | S0 | 0 | 85 | 3400 | 0 | 0 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | dos |
| 192.168.1.39 | 9 | 192.168.1.152 | 9 | tcp | - | 0.402129 | 0 | 0 | S0 | 0 | 100 | 4000 | 0 | 0 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | dos |
| 192.168.1.39 | 9 | 192.168.1.184 | 9 | tcp | - | 0.300084 | 0 | 0 | S0 | 0 | 100 | 4000 | 0 | 0 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | dos |
| 192.168.1.39 | 9 | 192.168.1.195 | 9 | tcp | - | 0.317941 | 0 | 0 | S0 | 0 | 100 | 4000 | 0 | 0 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | dos |
| 192.168.1.31 | 33451 | 192.168.1.1 | 53 | udp | dns | 0.002717 | 37 | 53 | SF | 0 | 1 | 65 | 1 | 81 | testphp.vulnweb.com | 1 | 1 | 0 | F | T | T | F | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | dos |

### Attack Type: `injection`

| src_ip | src_port | dst_ip | dst_port | proto | service | duration | src_bytes | dst_bytes | conn_state | missed_bytes | src_pkts | src_ip_bytes | dst_pkts | dst_ip_bytes | dns_query | dns_qclass | dns_qtype | dns_rcode | dns_AA | dns_RD | dns_RA | dns_rejected | ssl_version | ssl_cipher | ssl_resumed | ssl_established | ssl_subject | ssl_issuer | http_trans_depth | http_method | http_uri | http_version | http_request_body_len | http_response_body_len | http_status_code | http_user_agent | http_orig_mime_types | http_resp_mime_types | weird_name | weird_addl | weird_notice | label | type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 192.168.1.31 | 34684 | 101.119.11.17 | 80 | tcp | - | 172.941797 | 865 | 1152 | SF | 0 | 25 | 2164 | 21 | 2244 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | injection |
| 192.168.1.31 | 38524 | 192.168.1.1 | 53 | udp | dns | 0.00562 | 44 | 44 | SF | 0 | 2 | 100 | 2 | 100 | wpad | 1 | 1 | 0 | F | T | F | T | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | injection |
| 192.168.1.31 | 42075 | 192.168.1.1 | 53 | udp | dns | 0.00313 | 52 | 52 | SF | 0 | 2 | 108 | 2 | 108 | wpad.hub | 1 | 1 | 3 | F | T | F | T | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | injection |
| 192.168.1.31 | 43803 | 192.168.1.1 | 53 | udp | dns | 0.007465 | 44 | 44 | SF | 0 | 2 | 100 | 2 | 100 | wpad | 1 | 1 | 0 | F | T | F | T | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | injection |
| 192.168.1.31 | 45736 | 192.168.1.1 | 53 | udp | dns | 0.005039 | 44 | 44 | SF | 0 | 2 | 100 | 2 | 100 | wpad | 1 | 1 | 0 | F | T | F | T | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | injection |

### Attack Type: `mitm`

| src_ip | src_port | dst_ip | dst_port | proto | service | duration | src_bytes | dst_bytes | conn_state | missed_bytes | src_pkts | src_ip_bytes | dst_pkts | dst_ip_bytes | dns_query | dns_qclass | dns_qtype | dns_rcode | dns_AA | dns_RD | dns_RA | dns_rejected | ssl_version | ssl_cipher | ssl_resumed | ssl_established | ssl_subject | ssl_issuer | http_trans_depth | http_method | http_uri | http_version | http_request_body_len | http_response_body_len | http_status_code | http_user_agent | http_orig_mime_types | http_resp_mime_types | weird_name | weird_addl | weird_notice | label | type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 192.168.1.31 | 41054 | 151.101.24.64 | 443 | tcp | - | 22.872314 | 32 | 31 | SF | 0 | 8 | 411 | 6 | 343 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | mitm |
| 192.168.1.31 | 56692 | 151.101.24.134 | 443 | tcp | - | 23.609308 | 32 | 31 | SF | 0 | 7 | 371 | 5 | 291 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | mitm |
| 192.168.1.31 | 37546 | 192.229.237.25 | 443 | tcp | - | 3.401791 | 32 | 31 | SF | 0 | 6 | 307 | 4 | 239 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | mitm |
| 192.168.1.31 | 39080 | 54.230.245.173 | 443 | tcp | - | 69.788831 | 629 | 552 | SF | 0 | 28 | 2085 | 14 | 1280 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | mitm |
| 192.168.1.31 | 40058 | 13.211.225.170 | 443 | tcp | - | 68.758765 | 629 | 552 | SF | 0 | 28 | 2085 | 14 | 1280 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | mitm |

### Attack Type: `normal`

| src_ip | src_port | dst_ip | dst_port | proto | service | duration | src_bytes | dst_bytes | conn_state | missed_bytes | src_pkts | src_ip_bytes | dst_pkts | dst_ip_bytes | dns_query | dns_qclass | dns_qtype | dns_rcode | dns_AA | dns_RD | dns_RA | dns_rejected | ssl_version | ssl_cipher | ssl_resumed | ssl_established | ssl_subject | ssl_issuer | http_trans_depth | http_method | http_uri | http_version | http_request_body_len | http_response_body_len | http_status_code | http_user_agent | http_orig_mime_types | http_resp_mime_types | weird_name | weird_addl | weird_notice | label | type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 192.168.1.79 | 47260 | 192.168.1.255 | 15600 | udp | - | 0.0 | 0 | 0 | S0 | 0 | 1 | 63 | 0 | 0 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 0 | normal |
| 192.168.1.152 | 1880 | 192.168.1.152 | 51782 | tcp | - | 0.0 | 0 | 0 | OTH | 0 | 0 | 0 | 0 | 0 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | bad_TCP_checksum | - | F | 0 | normal |
| 192.168.1.152 | 34296 | 192.168.1.152 | 10502 | tcp | - | 0.0 | 0 | 0 | OTH | 0 | 0 | 0 | 0 | 0 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 0 | normal |
| 192.168.1.152 | 46608 | 192.168.1.190 | 53 | udp | dns | 0.000549 | 0 | 298 | SHR | 0 | 0 | 0 | 2 | 354 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | bad_UDP_checksum | - | F | 0 | normal |
| 192.168.1.152 | 1880 | 192.168.1.152 | 51782 | tcp | - | 0.0 | 0 | 0 | OTH | 0 | 0 | 0 | 0 | 0 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 0 | normal |

### Attack Type: `password`

| src_ip | src_port | dst_ip | dst_port | proto | service | duration | src_bytes | dst_bytes | conn_state | missed_bytes | src_pkts | src_ip_bytes | dst_pkts | dst_ip_bytes | dns_query | dns_qclass | dns_qtype | dns_rcode | dns_AA | dns_RD | dns_RA | dns_rejected | ssl_version | ssl_cipher | ssl_resumed | ssl_established | ssl_subject | ssl_issuer | http_trans_depth | http_method | http_uri | http_version | http_request_body_len | http_response_body_len | http_status_code | http_user_agent | http_orig_mime_types | http_resp_mime_types | weird_name | weird_addl | weird_notice | label | type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 192.168.1.31 | 33966 | 101.119.11.17 | 80 | tcp | http | 118.154006 | 576 | 768 | SF | 0 | 19 | 1572 | 16 | 1608 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | password |
| 192.168.1.31 | 36490 | 192.168.1.1 | 53 | udp | dns | 0.015741 | 84 | 424 | SF | 0 | 2 | 140 | 2 | 480 | detectportal.firefox.com | 1 | 1 | 0 | F | T | T | F | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | password |
| 192.168.1.31 | 37814 | 192.168.1.195 | 80 | tcp | http | 7.761997 | 446 | 205 | SF | 0 | 5 | 666 | 4 | 377 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | password |
| 192.168.1.31 | 43331 | 192.168.1.1 | 53 | udp | dns | 0.015047 | 42 | 200 | SF | 0 | 1 | 70 | 1 | 228 | detectportal.firefox.com | 1 | 1 | 0 | F | T | T | F | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | password |
| 192.168.1.31 | 45049 | 192.168.1.1 | 53 | udp | dns | 3.173759 | 64 | 253 | SF | 0 | 2 | 120 | 2 | 309 | www.dvwa.co.uk | 1 | 1 | 0 | F | T | T | F | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | password |

### Attack Type: `ransomware`

| src_ip | src_port | dst_ip | dst_port | proto | service | duration | src_bytes | dst_bytes | conn_state | missed_bytes | src_pkts | src_ip_bytes | dst_pkts | dst_ip_bytes | dns_query | dns_qclass | dns_qtype | dns_rcode | dns_AA | dns_RD | dns_RA | dns_rejected | ssl_version | ssl_cipher | ssl_resumed | ssl_established | ssl_subject | ssl_issuer | http_trans_depth | http_method | http_uri | http_version | http_request_body_len | http_response_body_len | http_status_code | http_user_agent | http_orig_mime_types | http_resp_mime_types | weird_name | weird_addl | weird_notice | label | type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 192.168.1.33 | 37242 | 34.230.157.88 | 443 | tcp | - | 0.0 | 0 | 0 | OTH | 0 | 0 | 0 | 1 | 103 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | ransomware |
| 192.168.1.33 | 37242 | 34.230.157.88 | 443 | tcp | - | 0.0 | 0 | 0 | OTH | 0 | 0 | 0 | 1 | 52 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | ransomware |
| 192.168.1.33 | 37242 | 34.230.157.88 | 443 | tcp | - | 0.0 | 0 | 0 | OTH | 0 | 1 | 118 | 0 | 0 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | ransomware |
| 192.168.1.33 | 37242 | 34.230.157.88 | 443 | tcp | - | 0.0 | 0 | 0 | OTH | 0 | 1 | 376 | 0 | 0 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | ransomware |
| 192.168.1.37 | 42438 | 34.230.157.88 | 443 | tcp | - | 0.0 | 0 | 0 | OTH | 0 | 0 | 0 | 1 | 103 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | ransomware |

### Attack Type: `scanning`

| src_ip | src_port | dst_ip | dst_port | proto | service | duration | src_bytes | dst_bytes | conn_state | missed_bytes | src_pkts | src_ip_bytes | dst_pkts | dst_ip_bytes | dns_query | dns_qclass | dns_qtype | dns_rcode | dns_AA | dns_RD | dns_RA | dns_rejected | ssl_version | ssl_cipher | ssl_resumed | ssl_established | ssl_subject | ssl_issuer | http_trans_depth | http_method | http_uri | http_version | http_request_body_len | http_response_body_len | http_status_code | http_user_agent | http_orig_mime_types | http_resp_mime_types | weird_name | weird_addl | weird_notice | label | type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 192.168.1.30 | 42908 | 192.168.1.103 | 2046 | tcp | - | 0.0 | 0 | 0 | S0 | 0 | 1 | 44 | 0 | 0 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | scanning |
| 192.168.1.30 | 42908 | 192.168.1.250 | 7435 | tcp | - | 0.0 | 0 | 0 | S0 | 0 | 1 | 44 | 0 | 0 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | scanning |
| 192.168.1.30 | 42908 | 192.168.1.46 | 1641 | tcp | - | 0.0 | 0 | 0 | S0 | 0 | 1 | 44 | 0 | 0 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | scanning |
| 192.168.1.30 | 42909 | 192.168.1.103 | 2046 | tcp | - | 0.0 | 0 | 0 | S0 | 0 | 1 | 44 | 0 | 0 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | scanning |
| 192.168.1.30 | 42909 | 192.168.1.46 | 2004 | tcp | - | 0.0 | 0 | 0 | S0 | 0 | 1 | 44 | 0 | 0 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | scanning |

### Attack Type: `xss`

| src_ip | src_port | dst_ip | dst_port | proto | service | duration | src_bytes | dst_bytes | conn_state | missed_bytes | src_pkts | src_ip_bytes | dst_pkts | dst_ip_bytes | dns_query | dns_qclass | dns_qtype | dns_rcode | dns_AA | dns_RD | dns_RA | dns_rejected | ssl_version | ssl_cipher | ssl_resumed | ssl_established | ssl_subject | ssl_issuer | http_trans_depth | http_method | http_uri | http_version | http_request_body_len | http_response_body_len | http_status_code | http_user_agent | http_orig_mime_types | http_resp_mime_types | weird_name | weird_addl | weird_notice | label | type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 192.168.1.32 | 33108 | 176.28.50.165 | 80 | tcp | - | 0.0 | 0 | 0 | S0 | 0 | 1 | 60 | 0 | 0 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | xss |
| 192.168.1.32 | 33114 | 176.28.50.165 | 80 | tcp | - | 0.0 | 0 | 0 | S0 | 0 | 1 | 60 | 0 | 0 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | xss |
| 192.168.1.32 | 33118 | 176.28.50.165 | 80 | tcp | - | 0.0 | 0 | 0 | S0 | 0 | 1 | 60 | 0 | 0 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | xss |
| 192.168.1.32 | 33122 | 176.28.50.165 | 80 | tcp | - | 0.0 | 0 | 0 | S0 | 0 | 1 | 60 | 0 | 0 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | xss |
| 192.168.1.32 | 33140 | 176.28.50.165 | 80 | tcp | - | 0.0 | 0 | 0 | S0 | 0 | 1 | 60 | 0 | 0 | - | 0 | 0 | 0 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 | 0 | 0 | - | - | - | - | - | - | 1 | xss |


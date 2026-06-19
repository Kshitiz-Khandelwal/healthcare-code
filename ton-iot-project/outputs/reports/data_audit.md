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

# Read-Only Lexical What-If Simulations

Uses the same 216 candidates per query, original stable traversal/tie order, saved dense scores, and current formulas. No source code, database, embeddings, Qdrant, RRF, reranker, prompt, or threshold changes.

Only parsed-keyword stopwords are removed. The existing parser already omits three-letter SAP; no new tokens are introduced. Exact phrase bonuses remain unchanged. The lexical-only +0.4 bonus remains in both simulations.

## Query 1: What is SAP_Redacted_pdfa-v1.pdf about?

Current keywords: ['what', 'sap_redacted_pdfa', 'about']. Candidates: 216.

### Baseline

Keywords: ['what', 'sap_redacted_pdfa', 'about']. Top-10 cutoff: 0.413136010. Best SAP rank: 13, score: 0.400865920. SAP survives: False.

| Rank | Baseline rank | Document | Chunk | Page/slide | Dense | Lexical | Blended | Body keyword matches | Formula |
|---:|---:|---|---|---|---:|---:|---:|---|---|
| 1 | 1 | doc_cf57d6670b15 | chk_5e92961f8f | Slide 3 | 0.554385100 | 0.25 | 0.602192550 | ['what'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 2 | 2 | doc_cf57d6670b15 | chk_62f403d9a8 | Slide 3 | 0.554385100 | 0.25 | 0.602192550 | ['what'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 3 | 3 | doc_cf57d6670b15 | chk_786b3da1fb | Slide 2 | 0.551661550 | 0.25 | 0.600830775 | ['what'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 4 | 4 | doc_cf57d6670b15 | chk_496d9bb308 | Slide 2 | 0.000000000 | 0.25 | 0.550000000 | ['what'] | `min(1.0, 0.4 + 0.6*lexical)` |
| 5 | 5 | doc_e2842eeb2cb3 | chk_c1cb9eacb5 | Page 25 | 0.612862700 | 0.00 | 0.429003890 | [] | `min(1.0, 0.7*dense)` |
| 6 | 6 | doc_e2842eeb2cb3 | chk_f1f3c4e009 | Page 8 | 0.593228340 | 0.00 | 0.415259838 | [] | `min(1.0, 0.7*dense)` |
| 7 | 7 | doc_cf57d6670b15 | chk_ef03dd69f3 | Slide 5 | 0.591558100 | 0.00 | 0.414090670 | [] | `min(1.0, 0.7*dense)` |
| 8 | 8 | doc_cf57d6670b15 | chk_61cb3a73c5 | Slide 5 | 0.591558100 | 0.00 | 0.414090670 | [] | `min(1.0, 0.7*dense)` |
| 9 | 9 | doc_cf57d6670b15 | chk_957860ad0e | Slide 6 | 0.590194300 | 0.00 | 0.413136010 | [] | `min(1.0, 0.7*dense)` |
| 10 | 10 | doc_cf57d6670b15 | chk_2ef94e244e | Slide 6 | 0.590194300 | 0.00 | 0.413136010 | [] | `min(1.0, 0.7*dense)` |

Moved out: None.
Moved in: None.

### Stopword-only

Keywords: ['sap_redacted_pdfa']. Top-10 cutoff: 0.397423740. Best SAP rank: 9, score: 0.400865920. SAP survives: True.

| Rank | Baseline rank | Document | Chunk | Page/slide | Dense | Lexical | Blended | Body keyword matches | Formula |
|---:|---:|---|---|---|---:|---:|---:|---|---|
| 1 | 5 | doc_e2842eeb2cb3 | chk_c1cb9eacb5 | Page 25 | 0.612862700 | 0.00 | 0.429003890 | [] | `min(1.0, 0.7*dense)` |
| 2 | 6 | doc_e2842eeb2cb3 | chk_f1f3c4e009 | Page 8 | 0.593228340 | 0.00 | 0.415259838 | [] | `min(1.0, 0.7*dense)` |
| 3 | 7 | doc_cf57d6670b15 | chk_ef03dd69f3 | Slide 5 | 0.591558100 | 0.00 | 0.414090670 | [] | `min(1.0, 0.7*dense)` |
| 4 | 8 | doc_cf57d6670b15 | chk_61cb3a73c5 | Slide 5 | 0.591558100 | 0.00 | 0.414090670 | [] | `min(1.0, 0.7*dense)` |
| 5 | 9 | doc_cf57d6670b15 | chk_957860ad0e | Slide 6 | 0.590194300 | 0.00 | 0.413136010 | [] | `min(1.0, 0.7*dense)` |
| 6 | 10 | doc_cf57d6670b15 | chk_2ef94e244e | Slide 6 | 0.590194300 | 0.00 | 0.413136010 | [] | `min(1.0, 0.7*dense)` |
| 7 | 11 | doc_cf57d6670b15 | chk_f867845048 | Slide 4 | 0.575025740 | 0.00 | 0.402518018 | [] | `min(1.0, 0.7*dense)` |
| 8 | 12 | doc_cf57d6670b15 | chk_ca0da581a3 | Slide 4 | 0.575025740 | 0.00 | 0.402518018 | [] | `min(1.0, 0.7*dense)` |
| 9 | 13 | doc_3ca7a20cb73b | chk_10630e0da6 | Page 21 | 0.572665600 | 0.00 | 0.400865920 | [] | `min(1.0, 0.7*dense)` |
| 10 | 14 | doc_e2842eeb2cb3 | chk_6a5418a1a6 | Page 11 | 0.567748200 | 0.00 | 0.397423740 | [] | `min(1.0, 0.7*dense)` |

Moved out: chk_5e92961f8f, chk_62f403d9a8, chk_786b3da1fb, chk_496d9bb308.
Moved in: chk_f867845048, chk_ca0da581a3, chk_10630e0da6, chk_6a5418a1a6.

### Stopword + bonus removal

Keywords: ['sap_redacted_pdfa']. Top-10 cutoff: 0.397423740. Best SAP rank: 9, score: 0.400865920. SAP survives: True.

| Rank | Baseline rank | Document | Chunk | Page/slide | Dense | Lexical | Blended | Body keyword matches | Formula |
|---:|---:|---|---|---|---:|---:|---:|---|---|
| 1 | 5 | doc_e2842eeb2cb3 | chk_c1cb9eacb5 | Page 25 | 0.612862700 | 0.00 | 0.429003890 | [] | `min(1.0, 0.7*dense)` |
| 2 | 6 | doc_e2842eeb2cb3 | chk_f1f3c4e009 | Page 8 | 0.593228340 | 0.00 | 0.415259838 | [] | `min(1.0, 0.7*dense)` |
| 3 | 7 | doc_cf57d6670b15 | chk_ef03dd69f3 | Slide 5 | 0.591558100 | 0.00 | 0.414090670 | [] | `min(1.0, 0.7*dense)` |
| 4 | 8 | doc_cf57d6670b15 | chk_61cb3a73c5 | Slide 5 | 0.591558100 | 0.00 | 0.414090670 | [] | `min(1.0, 0.7*dense)` |
| 5 | 9 | doc_cf57d6670b15 | chk_957860ad0e | Slide 6 | 0.590194300 | 0.00 | 0.413136010 | [] | `min(1.0, 0.7*dense)` |
| 6 | 10 | doc_cf57d6670b15 | chk_2ef94e244e | Slide 6 | 0.590194300 | 0.00 | 0.413136010 | [] | `min(1.0, 0.7*dense)` |
| 7 | 11 | doc_cf57d6670b15 | chk_f867845048 | Slide 4 | 0.575025740 | 0.00 | 0.402518018 | [] | `min(1.0, 0.7*dense)` |
| 8 | 12 | doc_cf57d6670b15 | chk_ca0da581a3 | Slide 4 | 0.575025740 | 0.00 | 0.402518018 | [] | `min(1.0, 0.7*dense)` |
| 9 | 13 | doc_3ca7a20cb73b | chk_10630e0da6 | Page 21 | 0.572665600 | 0.00 | 0.400865920 | [] | `min(1.0, 0.7*dense)` |
| 10 | 14 | doc_e2842eeb2cb3 | chk_6a5418a1a6 | Page 11 | 0.567748200 | 0.00 | 0.397423740 | [] | `min(1.0, 0.7*dense)` |

Moved out: chk_5e92961f8f, chk_62f403d9a8, chk_786b3da1fb, chk_496d9bb308.
Moved in: chk_f867845048, chk_ca0da581a3, chk_10630e0da6, chk_6a5418a1a6.

## Query 2: What is the study design described in the SAP?

Current keywords: ['what', 'study', 'design', 'described']. Candidates: 216.

### Baseline

Keywords: ['what', 'study', 'design', 'described']. Top-10 cutoff: 0.645057450. Best SAP rank: 32, score: 0.425381320. SAP survives: False.

| Rank | Baseline rank | Document | Chunk | Page/slide | Dense | Lexical | Blended | Body keyword matches | Formula |
|---:|---:|---|---|---|---:|---:|---:|---|---|
| 1 | 1 | doc_e2842eeb2cb3 | chk_f1f3c4e009 | Page 8 | 0.663612900 | 0.50 | 0.781806450 | ['study', 'design'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 2 | 2 | doc_e2842eeb2cb3 | chk_a391234a51 | Page 4 | 0.625401260 | 0.50 | 0.762700630 | ['study', 'design'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 3 | 3 | doc_e2842eeb2cb3 | chk_9de4abd6aa | Page 2 | 0.607226250 | 0.50 | 0.753613125 | ['study', 'design'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 4 | 4 | doc_e2842eeb2cb3 | chk_f7a0b03b62 | Page 7 | 0.594325100 | 0.50 | 0.747162550 | ['study', 'design'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 5 | 5 | doc_e2842eeb2cb3 | chk_6aece63d8a | Page 6 | 0.000000000 | 0.50 | 0.700000000 | ['study', 'design'] | `min(1.0, 0.4 + 0.6*lexical)` |
| 6 | 6 | doc_e2842eeb2cb3 | chk_e1fe3a6f8d | Page 9 | 0.000000000 | 0.50 | 0.700000000 | ['study', 'design'] | `min(1.0, 0.4 + 0.6*lexical)` |
| 7 | 7 | doc_cf57d6670b15 | chk_957860ad0e | Slide 6 | 0.644199000 | 0.25 | 0.647099500 | ['study'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 8 | 8 | doc_cf57d6670b15 | chk_2ef94e244e | Slide 6 | 0.644199000 | 0.25 | 0.647099500 | ['study'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 9 | 9 | doc_cf57d6670b15 | chk_5e92961f8f | Slide 3 | 0.640114900 | 0.25 | 0.645057450 | ['what'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 10 | 10 | doc_cf57d6670b15 | chk_62f403d9a8 | Slide 3 | 0.640114900 | 0.25 | 0.645057450 | ['what'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |

Moved out: None.
Moved in: None.

### Stopword-only

Keywords: ['study', 'design', 'described']. Top-10 cutoff: 0.550000000. Best SAP rank: 30, score: 0.425381320. SAP survives: False.

| Rank | Baseline rank | Document | Chunk | Page/slide | Dense | Lexical | Blended | Body keyword matches | Formula |
|---:|---:|---|---|---|---:|---:|---:|---|---|
| 1 | 1 | doc_e2842eeb2cb3 | chk_f1f3c4e009 | Page 8 | 0.663612900 | 0.50 | 0.781806450 | ['study', 'design'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 2 | 2 | doc_e2842eeb2cb3 | chk_a391234a51 | Page 4 | 0.625401260 | 0.50 | 0.762700630 | ['study', 'design'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 3 | 3 | doc_e2842eeb2cb3 | chk_9de4abd6aa | Page 2 | 0.607226250 | 0.50 | 0.753613125 | ['study', 'design'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 4 | 4 | doc_e2842eeb2cb3 | chk_f7a0b03b62 | Page 7 | 0.594325100 | 0.50 | 0.747162550 | ['study', 'design'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 5 | 5 | doc_e2842eeb2cb3 | chk_6aece63d8a | Page 6 | 0.000000000 | 0.50 | 0.700000000 | ['study', 'design'] | `min(1.0, 0.4 + 0.6*lexical)` |
| 6 | 6 | doc_e2842eeb2cb3 | chk_e1fe3a6f8d | Page 9 | 0.000000000 | 0.50 | 0.700000000 | ['study', 'design'] | `min(1.0, 0.4 + 0.6*lexical)` |
| 7 | 7 | doc_cf57d6670b15 | chk_957860ad0e | Slide 6 | 0.644199000 | 0.25 | 0.647099500 | ['study'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 8 | 8 | doc_cf57d6670b15 | chk_2ef94e244e | Slide 6 | 0.644199000 | 0.25 | 0.647099500 | ['study'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 9 | 11 | doc_e2842eeb2cb3 | chk_4bfbff44ea | Page 16 | 0.600586240 | 0.25 | 0.625293120 | ['study'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 10 | 14 | doc_e2842eeb2cb3 | chk_c18f593fdd | Page 1 | 0.000000000 | 0.25 | 0.550000000 | ['study'] | `min(1.0, 0.4 + 0.6*lexical)` |

Moved out: chk_5e92961f8f, chk_62f403d9a8.
Moved in: chk_4bfbff44ea, chk_c18f593fdd.

### Stopword + bonus removal

Keywords: ['study', 'design', 'described']. Top-10 cutoff: 0.550000000. Best SAP rank: 29, score: 0.425381320. SAP survives: False.

| Rank | Baseline rank | Document | Chunk | Page/slide | Dense | Lexical | Blended | Body keyword matches | Formula |
|---:|---:|---|---|---|---:|---:|---:|---|---|
| 1 | 5 | doc_e2842eeb2cb3 | chk_6aece63d8a | Page 6 | 0.000000000 | 0.50 | 0.700000000 | ['study', 'design'] | `min(1.0, 0.4 + 0.6*lexical)` |
| 2 | 6 | doc_e2842eeb2cb3 | chk_e1fe3a6f8d | Page 9 | 0.000000000 | 0.50 | 0.700000000 | ['study', 'design'] | `min(1.0, 0.4 + 0.6*lexical)` |
| 3 | 1 | doc_e2842eeb2cb3 | chk_f1f3c4e009 | Page 8 | 0.663612900 | 0.50 | 0.581806450 | ['study', 'design'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.0)` |
| 4 | 2 | doc_e2842eeb2cb3 | chk_a391234a51 | Page 4 | 0.625401260 | 0.50 | 0.562700630 | ['study', 'design'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.0)` |
| 5 | 3 | doc_e2842eeb2cb3 | chk_9de4abd6aa | Page 2 | 0.607226250 | 0.50 | 0.553613125 | ['study', 'design'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.0)` |
| 6 | 14 | doc_e2842eeb2cb3 | chk_c18f593fdd | Page 1 | 0.000000000 | 0.25 | 0.550000000 | ['study'] | `min(1.0, 0.4 + 0.6*lexical)` |
| 7 | 15 | doc_e2842eeb2cb3 | chk_0def134528 | Page 3 | 0.000000000 | 0.25 | 0.550000000 | ['study'] | `min(1.0, 0.4 + 0.6*lexical)` |
| 8 | 16 | doc_e2842eeb2cb3 | chk_9010fdbd95 | Page 5 | 0.000000000 | 0.25 | 0.550000000 | ['study'] | `min(1.0, 0.4 + 0.6*lexical)` |
| 9 | 17 | doc_e2842eeb2cb3 | chk_1f3be3f7a8 | Page 10 | 0.000000000 | 0.25 | 0.550000000 | ['study'] | `min(1.0, 0.4 + 0.6*lexical)` |
| 10 | 18 | doc_e2842eeb2cb3 | chk_462394cd4e | Page 11 | 0.000000000 | 0.25 | 0.550000000 | ['study'] | `min(1.0, 0.4 + 0.6*lexical)` |

Moved out: chk_f7a0b03b62, chk_957860ad0e, chk_2ef94e244e, chk_5e92961f8f, chk_62f403d9a8.
Moved in: chk_c18f593fdd, chk_0def134528, chk_9010fdbd95, chk_1f3be3f7a8, chk_462394cd4e.

## Query 3: What is the phase of the clinical trial?

Current keywords: ['what', 'phase', 'clinical', 'trial']. Candidates: 216.

### Baseline

Keywords: ['what', 'phase', 'clinical', 'trial']. Top-10 cutoff: 0.643637250. Best SAP rank: 15, score: 0.550000000. SAP survives: False.

| Rank | Baseline rank | Document | Chunk | Page/slide | Dense | Lexical | Blended | Body keyword matches | Formula |
|---:|---:|---|---|---|---:|---:|---:|---|---|
| 1 | 1 | doc_e2842eeb2cb3 | chk_f7a0b03b62 | Page 7 | 0.686192000 | 0.75 | 0.918096000 | ['phase', 'clinical', 'trial'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 2 | 2 | doc_e2842eeb2cb3 | chk_9010fdbd95 | Page 5 | 0.000000000 | 0.75 | 0.850000000 | ['phase', 'clinical', 'trial'] | `min(1.0, 0.4 + 0.6*lexical)` |
| 3 | 3 | doc_e2842eeb2cb3 | chk_d1c91d3597 | Page 17 | 0.663109960 | 0.25 | 0.656554980 | ['clinical'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 4 | 4 | doc_e2842eeb2cb3 | chk_f1f3c4e009 | Page 8 | 0.659275200 | 0.25 | 0.654637600 | ['phase'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 5 | 5 | doc_e2842eeb2cb3 | chk_1f3be3f7a8 | Page 10 | 0.658255100 | 0.25 | 0.654127550 | ['clinical'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 6 | 6 | doc_e2842eeb2cb3 | chk_a391234a51 | Page 4 | 0.655619600 | 0.25 | 0.652809800 | ['trial'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 7 | 7 | doc_e2842eeb2cb3 | chk_4bfbff44ea | Page 16 | 0.648322640 | 0.25 | 0.649161320 | ['clinical'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 8 | 8 | doc_e2842eeb2cb3 | chk_e1fe3a6f8d | Page 9 | 0.641603600 | 0.25 | 0.645801800 | ['trial'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 9 | 9 | doc_e2842eeb2cb3 | chk_ccebeb82d5 | Page 15 | 0.638490560 | 0.25 | 0.644245280 | ['clinical'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 10 | 10 | doc_e2842eeb2cb3 | chk_6aece63d8a | Page 6 | 0.637274500 | 0.25 | 0.643637250 | ['clinical'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |

Moved out: None.
Moved in: None.

### Stopword-only

Keywords: ['phase', 'clinical', 'trial']. Top-10 cutoff: 0.643637250. Best SAP rank: 13, score: 0.550000000. SAP survives: False.

| Rank | Baseline rank | Document | Chunk | Page/slide | Dense | Lexical | Blended | Body keyword matches | Formula |
|---:|---:|---|---|---|---:|---:|---:|---|---|
| 1 | 1 | doc_e2842eeb2cb3 | chk_f7a0b03b62 | Page 7 | 0.686192000 | 0.75 | 0.918096000 | ['phase', 'clinical', 'trial'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 2 | 2 | doc_e2842eeb2cb3 | chk_9010fdbd95 | Page 5 | 0.000000000 | 0.75 | 0.850000000 | ['phase', 'clinical', 'trial'] | `min(1.0, 0.4 + 0.6*lexical)` |
| 3 | 3 | doc_e2842eeb2cb3 | chk_d1c91d3597 | Page 17 | 0.663109960 | 0.25 | 0.656554980 | ['clinical'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 4 | 4 | doc_e2842eeb2cb3 | chk_f1f3c4e009 | Page 8 | 0.659275200 | 0.25 | 0.654637600 | ['phase'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 5 | 5 | doc_e2842eeb2cb3 | chk_1f3be3f7a8 | Page 10 | 0.658255100 | 0.25 | 0.654127550 | ['clinical'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 6 | 6 | doc_e2842eeb2cb3 | chk_a391234a51 | Page 4 | 0.655619600 | 0.25 | 0.652809800 | ['trial'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 7 | 7 | doc_e2842eeb2cb3 | chk_4bfbff44ea | Page 16 | 0.648322640 | 0.25 | 0.649161320 | ['clinical'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 8 | 8 | doc_e2842eeb2cb3 | chk_e1fe3a6f8d | Page 9 | 0.641603600 | 0.25 | 0.645801800 | ['trial'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 9 | 9 | doc_e2842eeb2cb3 | chk_ccebeb82d5 | Page 15 | 0.638490560 | 0.25 | 0.644245280 | ['clinical'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 10 | 10 | doc_e2842eeb2cb3 | chk_6aece63d8a | Page 6 | 0.637274500 | 0.25 | 0.643637250 | ['clinical'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |

Moved out: None.
Moved in: None.

### Stopword + bonus removal

Keywords: ['phase', 'clinical', 'trial']. Top-10 cutoff: 0.456554980. Best SAP rank: 3, score: 0.550000000. SAP survives: True.

| Rank | Baseline rank | Document | Chunk | Page/slide | Dense | Lexical | Blended | Body keyword matches | Formula |
|---:|---:|---|---|---|---:|---:|---:|---|---|
| 1 | 2 | doc_e2842eeb2cb3 | chk_9010fdbd95 | Page 5 | 0.000000000 | 0.75 | 0.850000000 | ['phase', 'clinical', 'trial'] | `min(1.0, 0.4 + 0.6*lexical)` |
| 2 | 1 | doc_e2842eeb2cb3 | chk_f7a0b03b62 | Page 7 | 0.686192000 | 0.75 | 0.718096000 | ['phase', 'clinical', 'trial'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.0)` |
| 3 | 15 | doc_3ca7a20cb73b | chk_bc7eb69b45 | Page 32 | 0.000000000 | 0.25 | 0.550000000 | ['trial'] | `min(1.0, 0.4 + 0.6*lexical)` |
| 4 | 16 | doc_3ca7a20cb73b | chk_4bf152f2d8 | Page 36 | 0.000000000 | 0.25 | 0.550000000 | ['trial'] | `min(1.0, 0.4 + 0.6*lexical)` |
| 5 | 17 | doc_3ca7a20cb73b | chk_c65b04261a | Page 37 | 0.000000000 | 0.25 | 0.550000000 | ['trial'] | `min(1.0, 0.4 + 0.6*lexical)` |
| 6 | 20 | doc_e2842eeb2cb3 | chk_9de4abd6aa | Page 2 | 0.000000000 | 0.25 | 0.550000000 | ['clinical'] | `min(1.0, 0.4 + 0.6*lexical)` |
| 7 | 21 | doc_e2842eeb2cb3 | chk_83442accfe | Page 14 | 0.000000000 | 0.25 | 0.550000000 | ['clinical'] | `min(1.0, 0.4 + 0.6*lexical)` |
| 8 | 22 | doc_e2842eeb2cb3 | chk_623702e63b | Page 12 | 0.660347600 | 0.00 | 0.462243320 | [] | `min(1.0, 0.7*dense)` |
| 9 | 23 | doc_e2842eeb2cb3 | chk_462394cd4e | Page 11 | 0.652826670 | 0.00 | 0.456978669 | [] | `min(1.0, 0.7*dense)` |
| 10 | 3 | doc_e2842eeb2cb3 | chk_d1c91d3597 | Page 17 | 0.663109960 | 0.25 | 0.456554980 | ['clinical'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.0)` |

Moved out: chk_f1f3c4e009, chk_1f3be3f7a8, chk_a391234a51, chk_4bfbff44ea, chk_e1fe3a6f8d, chk_ccebeb82d5, chk_6aece63d8a.
Moved in: chk_bc7eb69b45, chk_4bf152f2d8, chk_c65b04261a, chk_9de4abd6aa, chk_83442accfe, chk_623702e63b, chk_462394cd4e.

## Query 4: What is the primary purpose of the study?

Current keywords: ['what', 'primary', 'purpose', 'study']. Candidates: 216.

### Baseline

Keywords: ['what', 'primary', 'purpose', 'study']. Top-10 cutoff: 0.746694935. Best SAP rank: 31, score: 0.429136281. SAP survives: False.

| Rank | Baseline rank | Document | Chunk | Page/slide | Dense | Lexical | Blended | Body keyword matches | Formula |
|---:|---:|---|---|---|---:|---:|---:|---|---|
| 1 | 1 | doc_e2842eeb2cb3 | chk_83442accfe | Page 14 | 0.000000000 | 0.75 | 0.850000000 | ['primary', 'purpose', 'study'] | `min(1.0, 0.4 + 0.6*lexical)` |
| 2 | 2 | doc_e2842eeb2cb3 | chk_a391234a51 | Page 4 | 0.616421600 | 0.50 | 0.758210800 | ['primary', 'study'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 3 | 3 | doc_e2842eeb2cb3 | chk_6aece63d8a | Page 6 | 0.609828800 | 0.50 | 0.754914400 | ['primary', 'study'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 4 | 4 | doc_e2842eeb2cb3 | chk_462394cd4e | Page 11 | 0.605045700 | 0.50 | 0.752522850 | ['primary', 'study'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 5 | 5 | doc_e2842eeb2cb3 | chk_d1c91d3597 | Page 17 | 0.602679400 | 0.50 | 0.751339700 | ['primary', 'study'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 6 | 6 | doc_e2842eeb2cb3 | chk_f7a0b03b62 | Page 7 | 0.602059600 | 0.50 | 0.751029800 | ['primary', 'study'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 7 | 7 | doc_e2842eeb2cb3 | chk_e0c1023dfd | Page 19 | 0.601091200 | 0.50 | 0.750545600 | ['primary', 'study'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 8 | 8 | doc_e2842eeb2cb3 | chk_1f3be3f7a8 | Page 10 | 0.599052550 | 0.50 | 0.749526275 | ['primary', 'study'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 9 | 9 | doc_e2842eeb2cb3 | chk_4bfbff44ea | Page 16 | 0.596527200 | 0.50 | 0.748263600 | ['primary', 'study'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 10 | 10 | doc_e2842eeb2cb3 | chk_ccebeb82d5 | Page 15 | 0.593389870 | 0.50 | 0.746694935 | ['primary', 'study'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |

Moved out: None.
Moved in: None.

### Stopword-only

Keywords: ['primary', 'purpose', 'study']. Top-10 cutoff: 0.746694935. Best SAP rank: 29, score: 0.429136281. SAP survives: False.

| Rank | Baseline rank | Document | Chunk | Page/slide | Dense | Lexical | Blended | Body keyword matches | Formula |
|---:|---:|---|---|---|---:|---:|---:|---|---|
| 1 | 1 | doc_e2842eeb2cb3 | chk_83442accfe | Page 14 | 0.000000000 | 0.75 | 0.850000000 | ['primary', 'purpose', 'study'] | `min(1.0, 0.4 + 0.6*lexical)` |
| 2 | 2 | doc_e2842eeb2cb3 | chk_a391234a51 | Page 4 | 0.616421600 | 0.50 | 0.758210800 | ['primary', 'study'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 3 | 3 | doc_e2842eeb2cb3 | chk_6aece63d8a | Page 6 | 0.609828800 | 0.50 | 0.754914400 | ['primary', 'study'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 4 | 4 | doc_e2842eeb2cb3 | chk_462394cd4e | Page 11 | 0.605045700 | 0.50 | 0.752522850 | ['primary', 'study'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 5 | 5 | doc_e2842eeb2cb3 | chk_d1c91d3597 | Page 17 | 0.602679400 | 0.50 | 0.751339700 | ['primary', 'study'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 6 | 6 | doc_e2842eeb2cb3 | chk_f7a0b03b62 | Page 7 | 0.602059600 | 0.50 | 0.751029800 | ['primary', 'study'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 7 | 7 | doc_e2842eeb2cb3 | chk_e0c1023dfd | Page 19 | 0.601091200 | 0.50 | 0.750545600 | ['primary', 'study'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 8 | 8 | doc_e2842eeb2cb3 | chk_1f3be3f7a8 | Page 10 | 0.599052550 | 0.50 | 0.749526275 | ['primary', 'study'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 9 | 9 | doc_e2842eeb2cb3 | chk_4bfbff44ea | Page 16 | 0.596527200 | 0.50 | 0.748263600 | ['primary', 'study'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 10 | 10 | doc_e2842eeb2cb3 | chk_ccebeb82d5 | Page 15 | 0.593389870 | 0.50 | 0.746694935 | ['primary', 'study'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |

Moved out: None.
Moved in: None.

### Stopword + bonus removal

Keywords: ['primary', 'purpose', 'study']. Top-10 cutoff: 0.551339700. Best SAP rank: 27, score: 0.429136281. SAP survives: False.

| Rank | Baseline rank | Document | Chunk | Page/slide | Dense | Lexical | Blended | Body keyword matches | Formula |
|---:|---:|---|---|---|---:|---:|---:|---|---|
| 1 | 1 | doc_e2842eeb2cb3 | chk_83442accfe | Page 14 | 0.000000000 | 0.75 | 0.850000000 | ['primary', 'purpose', 'study'] | `min(1.0, 0.4 + 0.6*lexical)` |
| 2 | 14 | doc_e2842eeb2cb3 | chk_c18f593fdd | Page 1 | 0.000000000 | 0.50 | 0.700000000 | ['primary', 'study'] | `min(1.0, 0.4 + 0.6*lexical)` |
| 3 | 15 | doc_e2842eeb2cb3 | chk_0def134528 | Page 3 | 0.000000000 | 0.50 | 0.700000000 | ['primary', 'study'] | `min(1.0, 0.4 + 0.6*lexical)` |
| 4 | 16 | doc_e2842eeb2cb3 | chk_9010fdbd95 | Page 5 | 0.000000000 | 0.50 | 0.700000000 | ['primary', 'study'] | `min(1.0, 0.4 + 0.6*lexical)` |
| 5 | 17 | doc_e2842eeb2cb3 | chk_e1fe3a6f8d | Page 9 | 0.000000000 | 0.50 | 0.700000000 | ['primary', 'study'] | `min(1.0, 0.4 + 0.6*lexical)` |
| 6 | 18 | doc_e2842eeb2cb3 | chk_623702e63b | Page 12 | 0.000000000 | 0.50 | 0.700000000 | ['primary', 'study'] | `min(1.0, 0.4 + 0.6*lexical)` |
| 7 | 2 | doc_e2842eeb2cb3 | chk_a391234a51 | Page 4 | 0.616421600 | 0.50 | 0.558210800 | ['primary', 'study'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.0)` |
| 8 | 3 | doc_e2842eeb2cb3 | chk_6aece63d8a | Page 6 | 0.609828800 | 0.50 | 0.554914400 | ['primary', 'study'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.0)` |
| 9 | 4 | doc_e2842eeb2cb3 | chk_462394cd4e | Page 11 | 0.605045700 | 0.50 | 0.552522850 | ['primary', 'study'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.0)` |
| 10 | 5 | doc_e2842eeb2cb3 | chk_d1c91d3597 | Page 17 | 0.602679400 | 0.50 | 0.551339700 | ['primary', 'study'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.0)` |

Moved out: chk_f7a0b03b62, chk_e0c1023dfd, chk_1f3be3f7a8, chk_4bfbff44ea, chk_ccebeb82d5.
Moved in: chk_c18f593fdd, chk_0def134528, chk_9010fdbd95, chk_e1fe3a6f8d, chk_623702e63b.

## Query 5: What is a project manager?

Current keywords: ['what', 'project', 'manager']. Candidates: 216.

### Baseline

Keywords: ['what', 'project', 'manager']. Top-10 cutoff: 0.318145842. Best SAP rank: 15, score: 0.306463745. SAP survives: False.

| Rank | Baseline rank | Document | Chunk | Page/slide | Dense | Lexical | Blended | Body keyword matches | Formula |
|---:|---:|---|---|---|---:|---:|---:|---|---|
| 1 | 1 | doc_e2842eeb2cb3 | chk_c18f593fdd | Page 1 | 0.000000000 | 0.50 | 0.700000000 | ['project', 'manager'] | `min(1.0, 0.4 + 0.6*lexical)` |
| 2 | 2 | doc_cf57d6670b15 | chk_786b3da1fb | Slide 2 | 0.505209450 | 0.25 | 0.577604725 | ['what'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 3 | 3 | doc_cf57d6670b15 | chk_496d9bb308 | Slide 2 | 0.505209450 | 0.25 | 0.577604725 | ['what'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 4 | 4 | doc_cf57d6670b15 | chk_5e92961f8f | Slide 3 | 0.494377670 | 0.25 | 0.572188835 | ['what'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 5 | 5 | doc_cf57d6670b15 | chk_62f403d9a8 | Slide 3 | 0.494377670 | 0.25 | 0.572188835 | ['what'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 6 | 6 | doc_5ceea85f298b | chk_7b3c392cc5 | Slide None | 0.456276740 | 0.25 | 0.553138370 | ['project'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 7 | 7 | doc_cf57d6670b15 | chk_957860ad0e | Slide 6 | 0.531221330 | 0.00 | 0.371854931 | [] | `min(1.0, 0.7*dense)` |
| 8 | 8 | doc_cf57d6670b15 | chk_2ef94e244e | Slide 6 | 0.531221330 | 0.00 | 0.371854931 | [] | `min(1.0, 0.7*dense)` |
| 9 | 9 | doc_cf57d6670b15 | chk_f867845048 | Slide 4 | 0.454494060 | 0.00 | 0.318145842 | [] | `min(1.0, 0.7*dense)` |
| 10 | 10 | doc_cf57d6670b15 | chk_ca0da581a3 | Slide 4 | 0.454494060 | 0.00 | 0.318145842 | [] | `min(1.0, 0.7*dense)` |

Moved out: None.
Moved in: None.

Generic regression: top result remains doc_e2842eeb2cb3, chk_c18f593fdd, body matches ['project', 'manager'], score 0.700000000. No intent or evidence-support gate is added.

### Stopword-only

Keywords: ['project', 'manager']. Top-10 cutoff: 0.318145842. Best SAP rank: 15, score: 0.306463745. SAP survives: False.

| Rank | Baseline rank | Document | Chunk | Page/slide | Dense | Lexical | Blended | Body keyword matches | Formula |
|---:|---:|---|---|---|---:|---:|---:|---|---|
| 1 | 1 | doc_e2842eeb2cb3 | chk_c18f593fdd | Page 1 | 0.000000000 | 0.50 | 0.700000000 | ['project', 'manager'] | `min(1.0, 0.4 + 0.6*lexical)` |
| 2 | 6 | doc_5ceea85f298b | chk_7b3c392cc5 | Slide None | 0.456276740 | 0.25 | 0.553138370 | ['project'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.2)` |
| 3 | 7 | doc_cf57d6670b15 | chk_957860ad0e | Slide 6 | 0.531221330 | 0.00 | 0.371854931 | [] | `min(1.0, 0.7*dense)` |
| 4 | 8 | doc_cf57d6670b15 | chk_2ef94e244e | Slide 6 | 0.531221330 | 0.00 | 0.371854931 | [] | `min(1.0, 0.7*dense)` |
| 5 | 2 | doc_cf57d6670b15 | chk_786b3da1fb | Slide 2 | 0.505209450 | 0.00 | 0.353646615 | [] | `min(1.0, 0.7*dense)` |
| 6 | 3 | doc_cf57d6670b15 | chk_496d9bb308 | Slide 2 | 0.505209450 | 0.00 | 0.353646615 | [] | `min(1.0, 0.7*dense)` |
| 7 | 4 | doc_cf57d6670b15 | chk_5e92961f8f | Slide 3 | 0.494377670 | 0.00 | 0.346064369 | [] | `min(1.0, 0.7*dense)` |
| 8 | 5 | doc_cf57d6670b15 | chk_62f403d9a8 | Slide 3 | 0.494377670 | 0.00 | 0.346064369 | [] | `min(1.0, 0.7*dense)` |
| 9 | 9 | doc_cf57d6670b15 | chk_f867845048 | Slide 4 | 0.454494060 | 0.00 | 0.318145842 | [] | `min(1.0, 0.7*dense)` |
| 10 | 10 | doc_cf57d6670b15 | chk_ca0da581a3 | Slide 4 | 0.454494060 | 0.00 | 0.318145842 | [] | `min(1.0, 0.7*dense)` |

Moved out: None.
Moved in: None.

Generic regression: top result remains doc_e2842eeb2cb3, chk_c18f593fdd, body matches ['project', 'manager'], score 0.700000000. No intent or evidence-support gate is added.

### Stopword + bonus removal

Keywords: ['project', 'manager']. Top-10 cutoff: 0.318145842. Best SAP rank: 15, score: 0.306463745. SAP survives: False.

| Rank | Baseline rank | Document | Chunk | Page/slide | Dense | Lexical | Blended | Body keyword matches | Formula |
|---:|---:|---|---|---|---:|---:|---:|---|---|
| 1 | 1 | doc_e2842eeb2cb3 | chk_c18f593fdd | Page 1 | 0.000000000 | 0.50 | 0.700000000 | ['project', 'manager'] | `min(1.0, 0.4 + 0.6*lexical)` |
| 2 | 7 | doc_cf57d6670b15 | chk_957860ad0e | Slide 6 | 0.531221330 | 0.00 | 0.371854931 | [] | `min(1.0, 0.7*dense)` |
| 3 | 8 | doc_cf57d6670b15 | chk_2ef94e244e | Slide 6 | 0.531221330 | 0.00 | 0.371854931 | [] | `min(1.0, 0.7*dense)` |
| 4 | 2 | doc_cf57d6670b15 | chk_786b3da1fb | Slide 2 | 0.505209450 | 0.00 | 0.353646615 | [] | `min(1.0, 0.7*dense)` |
| 5 | 3 | doc_cf57d6670b15 | chk_496d9bb308 | Slide 2 | 0.505209450 | 0.00 | 0.353646615 | [] | `min(1.0, 0.7*dense)` |
| 6 | 6 | doc_5ceea85f298b | chk_7b3c392cc5 | Slide None | 0.456276740 | 0.25 | 0.353138370 | ['project'] | `min(1.0, 0.5*dense + 0.5*lexical + 0.0)` |
| 7 | 4 | doc_cf57d6670b15 | chk_5e92961f8f | Slide 3 | 0.494377670 | 0.00 | 0.346064369 | [] | `min(1.0, 0.7*dense)` |
| 8 | 5 | doc_cf57d6670b15 | chk_62f403d9a8 | Slide 3 | 0.494377670 | 0.00 | 0.346064369 | [] | `min(1.0, 0.7*dense)` |
| 9 | 9 | doc_cf57d6670b15 | chk_f867845048 | Slide 4 | 0.454494060 | 0.00 | 0.318145842 | [] | `min(1.0, 0.7*dense)` |
| 10 | 10 | doc_cf57d6670b15 | chk_ca0da581a3 | Slide 4 | 0.454494060 | 0.00 | 0.318145842 | [] | `min(1.0, 0.7*dense)` |

Moved out: None.
Moved in: None.

Generic regression: top result remains doc_e2842eeb2cb3, chk_c18f593fdd, body matches ['project', 'manager'], score 0.700000000. No intent or evidence-support gate is added.


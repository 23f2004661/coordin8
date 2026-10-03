# Read-Only RRF/Fusion Trace

Actual fusion inputs, internal score-map values, returned outputs, reranking, and context assembly observed without changing production behavior.

The first RRF list is the blended top10, not raw dense ranks. Sparse list is empty. Thus score = 1/(60 + pre-RRF rank). Fusion computes ten scores but returns only five; internal ranks 6-10 are not returned candidates.

## Query A: What is SAP_Redacted_pdfa-v1.pdf about?

### Complete Pre-RRF Input

| Rank | Document/title | Chunk | Page/slide | Raw dense rank | Dense | Lexical | Blended |
|---:|---|---|---|---|---:|---:|---:|
| 1 | doc_e2842eeb2cb3: fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_c1cb9eacb5 | Page 25 | 1 | 0.612862700 | 0.00 | 0.429003890 |
| 2 | doc_e2842eeb2cb3: fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_f1f3c4e009 | Page 8 | 2 | 0.593228340 | 0.00 | 0.415259838 |
| 3 | doc_cf57d6670b15: POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_ef03dd69f3 | Slide 5 | 3 | 0.591558100 | 0.00 | 0.414090670 |
| 4 | doc_cf57d6670b15: POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_61cb3a73c5 | Slide 5 | 4 | 0.591558100 | 0.00 | 0.414090670 |
| 5 | doc_cf57d6670b15: POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_957860ad0e | Slide 6 | 5 | 0.590194300 | 0.00 | 0.413136010 |
| 6 | doc_cf57d6670b15: POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_2ef94e244e | Slide 6 | 6 | 0.590194300 | 0.00 | 0.413136010 |
| 7 | doc_cf57d6670b15: POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_f867845048 | Slide 4 | 7 | 0.575025740 | 0.00 | 0.402518018 |
| 8 | doc_cf57d6670b15: POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_ca0da581a3 | Slide 4 | 8 | 0.575025740 | 0.00 | 0.402518018 |
| 9 | doc_3ca7a20cb73b: SAP_Redacted_pdfa-v1 | chk_10630e0da6 | Page 21 | 9 | 0.572665600 | 0.00 | 0.400865920 |
| 10 | doc_e2842eeb2cb3: fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_6a5418a1a6 | Page 11 | 10 | 0.567748200 | 0.00 | 0.397423740 |

### Exact RRF Calculation / Internal Top 10

| Internal rank | Document/title | Chunk | Page/slide | Dense rank | Pre-RRF rank | Calculation | RRF score | Returned rank | Reranker rank | Final context |
|---:|---|---|---|---|---:|---|---:|---|---|---|
| 1 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_c1cb9eacb5 | Page 25 | 1 | 1 | 1 / (60 + 1) | 0.016393442623 | 1 | 1 | True |
| 2 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_f1f3c4e009 | Page 8 | 2 | 2 | 1 / (60 + 2) | 0.016129032258 | 2 | 2 | True |
| 3 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_ef03dd69f3 | Slide 5 | 3 | 3 | 1 / (60 + 3) | 0.015873015873 | 3 | 3 | True |
| 4 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_61cb3a73c5 | Slide 5 | 4 | 4 | 1 / (60 + 4) | 0.015625000000 | 4 | 4 | True |
| 5 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_957860ad0e | Slide 6 | 5 | 5 | 1 / (60 + 5) | 0.015384615385 | 5 | 5 | True |
| 6 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_2ef94e244e | Slide 6 | 6 | 6 | 1 / (60 + 6) | 0.015151515152 | None | None | False |
| 7 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_f867845048 | Slide 4 | 7 | 7 | 1 / (60 + 7) | 0.014925373134 | None | None | False |
| 8 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_ca0da581a3 | Slide 4 | 8 | 8 | 1 / (60 + 8) | 0.014705882353 | None | None | False |
| 9 | SAP_Redacted_pdfa-v1 | chk_10630e0da6 | Page 21 | 9 | 9 | 1 / (60 + 9) | 0.014492753623 | None | None | False |
| 10 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_6a5418a1a6 | Page 11 | 10 | 10 | 1 / (60 + 10) | 0.014285714286 | None | None | False |

### SAP Dense Candidates

| Chunk | Page | Dense rank | Combined rank | Pre-RRF rank | Lexical input rank | RRF score | Internal RRF rank | Returned rank | Reranker rank | Final context | Lost at |
|---|---|---:|---:|---|---|---|---|---|---|---|---|
| chk_10630e0da6 | 21 | 9 | 9 | 9 | None | 0.014492753623188406 | 9 | None | None | False | fusion top-5 cutoff |
| chk_e904bf185b | 69 | 13 | 13 | None | None | None | None | None | None | False | pre-RRF top-10 cutoff |
| chk_1d60ffc0a3 | 158 | 14 | 14 | None | None | None | None | None | None | False | pre-RRF top-10 cutoff |
| chk_67222548af | 119 | 15 | 15 | None | None | None | None | None | None | False | pre-RRF top-10 cutoff |
| chk_8da6387947 | 161 | 16 | 16 | None | None | None | None | None | None | False | pre-RRF top-10 cutoff |
| chk_f78c0dadfc | 182 | 19 | 19 | None | None | None | None | None | None | False | pre-RRF top-10 cutoff |

### Final Context Concentration

- fda_22350s26_and_200678s28_saxagliptin_statistical_prea: 2/5 (40%).
- POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1): 3/5 (60%).
- Exact duplicate text groups: [['chk_ef03dd69f3', 'chk_61cb3a73c5']]
- Context assembler retains all five reranked items; no additional truncation.

## Query B: What is the study design described in the SAP?

### Complete Pre-RRF Input

| Rank | Document/title | Chunk | Page/slide | Raw dense rank | Dense | Lexical | Blended |
|---:|---|---|---|---|---:|---:|---:|
| 1 | doc_e2842eeb2cb3: fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_f1f3c4e009 | Page 8 | 1 | 0.663612900 | 0.50 | 0.781806450 |
| 2 | doc_e2842eeb2cb3: fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_a391234a51 | Page 4 | 10 | 0.625401260 | 0.50 | 0.762700630 |
| 3 | doc_e2842eeb2cb3: fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_9de4abd6aa | Page 2 | 12 | 0.607226250 | 0.50 | 0.753613125 |
| 4 | doc_e2842eeb2cb3: fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_f7a0b03b62 | Page 7 | 18 | 0.594325100 | 0.50 | 0.747162550 |
| 5 | doc_e2842eeb2cb3: fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_6aece63d8a | Page 6 | None | 0.000000000 | 0.50 | 0.700000000 |
| 6 | doc_e2842eeb2cb3: fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_e1fe3a6f8d | Page 9 | None | 0.000000000 | 0.50 | 0.700000000 |
| 7 | doc_cf57d6670b15: POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_957860ad0e | Slide 6 | 3 | 0.644199000 | 0.25 | 0.647099500 |
| 8 | doc_cf57d6670b15: POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_2ef94e244e | Slide 6 | 2 | 0.644199000 | 0.25 | 0.647099500 |
| 9 | doc_e2842eeb2cb3: fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_4bfbff44ea | Page 16 | 13 | 0.600586240 | 0.25 | 0.625293120 |
| 10 | doc_e2842eeb2cb3: fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_c18f593fdd | Page 1 | None | 0.000000000 | 0.25 | 0.550000000 |

### Exact RRF Calculation / Internal Top 10

| Internal rank | Document/title | Chunk | Page/slide | Dense rank | Pre-RRF rank | Calculation | RRF score | Returned rank | Reranker rank | Final context |
|---:|---|---|---|---|---:|---|---:|---|---|---|
| 1 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_f1f3c4e009 | Page 8 | 1 | 1 | 1 / (60 + 1) | 0.016393442623 | 1 | 1 | True |
| 2 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_a391234a51 | Page 4 | 10 | 2 | 1 / (60 + 2) | 0.016129032258 | 2 | 2 | True |
| 3 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_9de4abd6aa | Page 2 | 12 | 3 | 1 / (60 + 3) | 0.015873015873 | 3 | 3 | True |
| 4 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_f7a0b03b62 | Page 7 | 18 | 4 | 1 / (60 + 4) | 0.015625000000 | 4 | 4 | True |
| 5 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_6aece63d8a | Page 6 | None | 5 | 1 / (60 + 5) | 0.015384615385 | 5 | 5 | True |
| 6 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_e1fe3a6f8d | Page 9 | None | 6 | 1 / (60 + 6) | 0.015151515152 | None | None | False |
| 7 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_957860ad0e | Slide 6 | 3 | 7 | 1 / (60 + 7) | 0.014925373134 | None | None | False |
| 8 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_2ef94e244e | Slide 6 | 2 | 8 | 1 / (60 + 8) | 0.014705882353 | None | None | False |
| 9 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_4bfbff44ea | Page 16 | 13 | 9 | 1 / (60 + 9) | 0.014492753623 | None | None | False |
| 10 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_c18f593fdd | Page 1 | None | 10 | 1 / (60 + 10) | 0.014285714286 | None | None | False |

### SAP Dense Candidates

| Chunk | Page | Dense rank | Combined rank | Pre-RRF rank | Lexical input rank | RRF score | Internal RRF rank | Returned rank | Reranker rank | Final context | Lost at |
|---|---|---:|---:|---|---|---|---|---|---|---|---|
| chk_67222548af | 119 | 11 | 30 | None | None | None | None | None | None | False | pre-RRF top-10 cutoff |

### Final Context Concentration

- fda_22350s26_and_200678s28_saxagliptin_statistical_prea: 5/5 (100%).
- Exact duplicate text groups: []
- Context assembler retains all five reranked items; no additional truncation.

## Query C: What is the phase of the clinical trial?

### Complete Pre-RRF Input

| Rank | Document/title | Chunk | Page/slide | Raw dense rank | Dense | Lexical | Blended |
|---:|---|---|---|---|---:|---:|---:|
| 1 | doc_e2842eeb2cb3: fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_f7a0b03b62 | Page 7 | 1 | 0.686192000 | 0.75 | 0.918096000 |
| 2 | doc_e2842eeb2cb3: fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_9010fdbd95 | Page 5 | None | 0.000000000 | 0.75 | 0.850000000 |
| 3 | doc_e2842eeb2cb3: fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_d1c91d3597 | Page 17 | 2 | 0.663109960 | 0.25 | 0.656554980 |
| 4 | doc_e2842eeb2cb3: fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_f1f3c4e009 | Page 8 | 4 | 0.659275200 | 0.25 | 0.654637600 |
| 5 | doc_e2842eeb2cb3: fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_1f3be3f7a8 | Page 10 | 5 | 0.658255100 | 0.25 | 0.654127550 |
| 6 | doc_e2842eeb2cb3: fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_a391234a51 | Page 4 | 6 | 0.655619600 | 0.25 | 0.652809800 |
| 7 | doc_e2842eeb2cb3: fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_4bfbff44ea | Page 16 | 8 | 0.648322640 | 0.25 | 0.649161320 |
| 8 | doc_e2842eeb2cb3: fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_e1fe3a6f8d | Page 9 | 9 | 0.641603600 | 0.25 | 0.645801800 |
| 9 | doc_e2842eeb2cb3: fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_ccebeb82d5 | Page 15 | 10 | 0.638490560 | 0.25 | 0.644245280 |
| 10 | doc_e2842eeb2cb3: fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_6aece63d8a | Page 6 | 11 | 0.637274500 | 0.25 | 0.643637250 |

### Exact RRF Calculation / Internal Top 10

| Internal rank | Document/title | Chunk | Page/slide | Dense rank | Pre-RRF rank | Calculation | RRF score | Returned rank | Reranker rank | Final context |
|---:|---|---|---|---|---:|---|---:|---|---|---|
| 1 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_f7a0b03b62 | Page 7 | 1 | 1 | 1 / (60 + 1) | 0.016393442623 | 1 | 1 | True |
| 2 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_9010fdbd95 | Page 5 | None | 2 | 1 / (60 + 2) | 0.016129032258 | 2 | 2 | True |
| 3 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_d1c91d3597 | Page 17 | 2 | 3 | 1 / (60 + 3) | 0.015873015873 | 3 | 3 | True |
| 4 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_f1f3c4e009 | Page 8 | 4 | 4 | 1 / (60 + 4) | 0.015625000000 | 4 | 4 | True |
| 5 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_1f3be3f7a8 | Page 10 | 5 | 5 | 1 / (60 + 5) | 0.015384615385 | 5 | 5 | True |
| 6 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_a391234a51 | Page 4 | 6 | 6 | 1 / (60 + 6) | 0.015151515152 | None | None | False |
| 7 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_4bfbff44ea | Page 16 | 8 | 7 | 1 / (60 + 7) | 0.014925373134 | None | None | False |
| 8 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_e1fe3a6f8d | Page 9 | 9 | 8 | 1 / (60 + 8) | 0.014705882353 | None | None | False |
| 9 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_ccebeb82d5 | Page 15 | 10 | 9 | 1 / (60 + 9) | 0.014492753623 | None | None | False |
| 10 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_6aece63d8a | Page 6 | 11 | 10 | 1 / (60 + 10) | 0.014285714286 | None | None | False |

### SAP Dense Candidates

| Chunk | Page | Dense rank | Combined rank | Pre-RRF rank | Lexical input rank | RRF score | Internal RRF rank | Returned rank | Reranker rank | Final context | Lost at |
|---|---|---:|---:|---|---|---|---|---|---|---|---|
| chk_518963973b | 110 | 14 | 21 | None | None | None | None | None | None | False | pre-RRF top-10 cutoff |
| chk_67222548af | 119 | 17 | 24 | None | None | None | None | None | None | False | pre-RRF top-10 cutoff |

### Final Context Concentration

- fda_22350s26_and_200678s28_saxagliptin_statistical_prea: 5/5 (100%).
- Exact duplicate text groups: []
- Context assembler retains all five reranked items; no additional truncation.

## Query D: What is the primary purpose of the study?

### Complete Pre-RRF Input

| Rank | Document/title | Chunk | Page/slide | Raw dense rank | Dense | Lexical | Blended |
|---:|---|---|---|---|---:|---:|---:|
| 1 | doc_e2842eeb2cb3: fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_83442accfe | Page 14 | None | 0.000000000 | 0.75 | 0.850000000 |
| 2 | doc_e2842eeb2cb3: fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_a391234a51 | Page 4 | 1 | 0.616421600 | 0.50 | 0.758210800 |
| 3 | doc_e2842eeb2cb3: fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_6aece63d8a | Page 6 | 3 | 0.609828800 | 0.50 | 0.754914400 |
| 4 | doc_e2842eeb2cb3: fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_462394cd4e | Page 11 | 4 | 0.605045700 | 0.50 | 0.752522850 |
| 5 | doc_e2842eeb2cb3: fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_d1c91d3597 | Page 17 | 5 | 0.602679400 | 0.50 | 0.751339700 |
| 6 | doc_e2842eeb2cb3: fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_f7a0b03b62 | Page 7 | 6 | 0.602059600 | 0.50 | 0.751029800 |
| 7 | doc_e2842eeb2cb3: fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_e0c1023dfd | Page 19 | 7 | 0.601091200 | 0.50 | 0.750545600 |
| 8 | doc_e2842eeb2cb3: fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_1f3be3f7a8 | Page 10 | 8 | 0.599052550 | 0.50 | 0.749526275 |
| 9 | doc_e2842eeb2cb3: fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_4bfbff44ea | Page 16 | 11 | 0.596527200 | 0.50 | 0.748263600 |
| 10 | doc_e2842eeb2cb3: fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_ccebeb82d5 | Page 15 | 13 | 0.593389870 | 0.50 | 0.746694935 |

### Exact RRF Calculation / Internal Top 10

| Internal rank | Document/title | Chunk | Page/slide | Dense rank | Pre-RRF rank | Calculation | RRF score | Returned rank | Reranker rank | Final context |
|---:|---|---|---|---|---:|---|---:|---|---|---|
| 1 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_83442accfe | Page 14 | None | 1 | 1 / (60 + 1) | 0.016393442623 | 1 | 1 | True |
| 2 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_a391234a51 | Page 4 | 1 | 2 | 1 / (60 + 2) | 0.016129032258 | 2 | 2 | True |
| 3 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_6aece63d8a | Page 6 | 3 | 3 | 1 / (60 + 3) | 0.015873015873 | 3 | 3 | True |
| 4 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_462394cd4e | Page 11 | 4 | 4 | 1 / (60 + 4) | 0.015625000000 | 4 | 4 | True |
| 5 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_d1c91d3597 | Page 17 | 5 | 5 | 1 / (60 + 5) | 0.015384615385 | 5 | 5 | True |
| 6 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_f7a0b03b62 | Page 7 | 6 | 6 | 1 / (60 + 6) | 0.015151515152 | None | None | False |
| 7 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_e0c1023dfd | Page 19 | 7 | 7 | 1 / (60 + 7) | 0.014925373134 | None | None | False |
| 8 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_1f3be3f7a8 | Page 10 | 8 | 8 | 1 / (60 + 8) | 0.014705882353 | None | None | False |
| 9 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_4bfbff44ea | Page 16 | 11 | 9 | 1 / (60 + 9) | 0.014492753623 | None | None | False |
| 10 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_ccebeb82d5 | Page 15 | 13 | 10 | 1 / (60 + 10) | 0.014285714286 | None | None | False |

### SAP Dense Candidates

| Chunk | Page | Dense rank | Combined rank | Pre-RRF rank | Lexical input rank | RRF score | Internal RRF rank | Returned rank | Reranker rank | Final context | Lost at |
|---|---|---:|---:|---|---|---|---|---|---|---|---|
| chk_a5f0626a0e | 43 | 2 | 29 | None | None | None | None | None | None | False | pre-RRF top-10 cutoff |
| chk_67222548af | 119 | 9 | 30 | None | None | None | None | None | None | False | pre-RRF top-10 cutoff |
| chk_5863853205 | 121 | 10 | 31 | None | None | None | None | None | None | False | pre-RRF top-10 cutoff |
| chk_10630e0da6 | 21 | 15 | 32 | None | None | None | None | None | None | False | pre-RRF top-10 cutoff |
| chk_db12d63469 | 120 | 19 | 35 | None | None | None | None | None | None | False | pre-RRF top-10 cutoff |

### Final Context Concentration

- fda_22350s26_and_200678s28_saxagliptin_statistical_prea: 5/5 (100%).
- Exact duplicate text groups: []
- Context assembler retains all five reranked items; no additional truncation.

## Query E: What is a project manager?

### Complete Pre-RRF Input

| Rank | Document/title | Chunk | Page/slide | Raw dense rank | Dense | Lexical | Blended |
|---:|---|---|---|---|---:|---:|---:|
| 1 | doc_e2842eeb2cb3: fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_c18f593fdd | Page 1 | None | 0.000000000 | 0.50 | 0.700000000 |
| 2 | doc_5ceea85f298b: coordin8-q3-verification | chk_7b3c392cc5 | sec_doc_5ceea85f298b_main | 7 | 0.456276740 | 0.25 | 0.553138370 |
| 3 | doc_cf57d6670b15: POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_957860ad0e | Slide 6 | 1 | 0.531221330 | 0.00 | 0.371854931 |
| 4 | doc_cf57d6670b15: POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_2ef94e244e | Slide 6 | 2 | 0.531221330 | 0.00 | 0.371854931 |
| 5 | doc_cf57d6670b15: POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_786b3da1fb | Slide 2 | 3 | 0.505209450 | 0.00 | 0.353646615 |
| 6 | doc_cf57d6670b15: POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_496d9bb308 | Slide 2 | 4 | 0.505209450 | 0.00 | 0.353646615 |
| 7 | doc_cf57d6670b15: POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_5e92961f8f | Slide 3 | 5 | 0.494377670 | 0.00 | 0.346064369 |
| 8 | doc_cf57d6670b15: POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_62f403d9a8 | Slide 3 | 6 | 0.494377670 | 0.00 | 0.346064369 |
| 9 | doc_cf57d6670b15: POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_f867845048 | Slide 4 | 9 | 0.454494060 | 0.00 | 0.318145842 |
| 10 | doc_cf57d6670b15: POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_ca0da581a3 | Slide 4 | 8 | 0.454494060 | 0.00 | 0.318145842 |

### Exact RRF Calculation / Internal Top 10

| Internal rank | Document/title | Chunk | Page/slide | Dense rank | Pre-RRF rank | Calculation | RRF score | Returned rank | Reranker rank | Final context |
|---:|---|---|---|---|---:|---|---:|---|---|---|
| 1 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_c18f593fdd | Page 1 | None | 1 | 1 / (60 + 1) | 0.016393442623 | 1 | 1 | True |
| 2 | coordin8-q3-verification | chk_7b3c392cc5 | sec_doc_5ceea85f298b_main | 7 | 2 | 1 / (60 + 2) | 0.016129032258 | 2 | 2 | True |
| 3 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_957860ad0e | Slide 6 | 1 | 3 | 1 / (60 + 3) | 0.015873015873 | 3 | 3 | True |
| 4 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_2ef94e244e | Slide 6 | 2 | 4 | 1 / (60 + 4) | 0.015625000000 | 4 | 4 | True |
| 5 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_786b3da1fb | Slide 2 | 3 | 5 | 1 / (60 + 5) | 0.015384615385 | 5 | 5 | True |
| 6 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_496d9bb308 | Slide 2 | 4 | 6 | 1 / (60 + 6) | 0.015151515152 | None | None | False |
| 7 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_5e92961f8f | Slide 3 | 5 | 7 | 1 / (60 + 7) | 0.014925373134 | None | None | False |
| 8 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_62f403d9a8 | Slide 3 | 6 | 8 | 1 / (60 + 8) | 0.014705882353 | None | None | False |
| 9 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_f867845048 | Slide 4 | 9 | 9 | 1 / (60 + 9) | 0.014492753623 | None | None | False |
| 10 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_ca0da581a3 | Slide 4 | 8 | 10 | 1 / (60 + 10) | 0.014285714286 | None | None | False |

### SAP Dense Candidates

| Chunk | Page | Dense rank | Combined rank | Pre-RRF rank | Lexical input rank | RRF score | Internal RRF rank | Returned rank | Reranker rank | Final context | Lost at |
|---|---|---:|---:|---|---|---|---|---|---|---|---|
| chk_67222548af | 119 | 14 | 15 | None | None | None | None | None | None | False | pre-RRF top-10 cutoff |
| chk_b070aaddbc | 172 | 17 | 18 | None | None | None | None | None | None | False | pre-RRF top-10 cutoff |
| chk_4778572633 | 171 | 18 | 19 | None | None | None | None | None | None | False | pre-RRF top-10 cutoff |
| chk_157f371880 | 179 | 19 | 20 | None | None | None | None | None | None | False | pre-RRF top-10 cutoff |

### Final Context Concentration

- fda_22350s26_and_200678s28_saxagliptin_statistical_prea: 1/5 (20%).
- coordin8-q3-verification: 1/5 (20%).
- POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1): 3/5 (60%).
- Exact duplicate text groups: [['chk_957860ad0e', 'chk_2ef94e244e']]
- Context assembler retains all five reranked items; no additional truncation.


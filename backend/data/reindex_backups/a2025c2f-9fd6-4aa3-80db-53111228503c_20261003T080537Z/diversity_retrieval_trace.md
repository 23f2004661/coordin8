# Generic Final-Context Diversity Trace

Actual pre-RRF score/order and RRF formula checked against the prior trace. No Qdrant writes, reindexing, schema changes, or Groq calls.

## Query A: What is SAP_Redacted_pdfa-v1.pdf about?

### Pre-RRF Top 10

| Rank | Document/title | Chunk | Page/slide | Dense | Lexical | Blended |
|---:|---|---|---|---:|---:|---:|
| 1 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_c1cb9eacb5 | Page 25 | 0.6129 | 0.00 | 0.429003890 |
| 2 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_f1f3c4e009 | Page 8 | 0.5932 | 0.00 | 0.415259838 |
| 3 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_ef03dd69f3 | Slide 5 | 0.5916 | 0.00 | 0.414090670 |
| 4 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_61cb3a73c5 | Slide 5 | 0.5916 | 0.00 | 0.414090670 |
| 5 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_957860ad0e | Slide 6 | 0.5902 | 0.00 | 0.413136010 |
| 6 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_2ef94e244e | Slide 6 | 0.5902 | 0.00 | 0.413136010 |
| 7 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_f867845048 | Slide 4 | 0.5750 | 0.00 | 0.402518018 |
| 8 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_ca0da581a3 | Slide 4 | 0.5750 | 0.00 | 0.402518018 |
| 9 | SAP_Redacted_pdfa-v1 | chk_10630e0da6 | Page 21 | 0.5727 | 0.00 | 0.400865920 |
| 10 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_6a5418a1a6 | Page 11 | 0.5677 | 0.00 | 0.397423740 |

### Selected Final Context

| Final rank | Original rank | Document/title | Chunk | Page/slide | Blended | Unchanged RRF |
|---:|---:|---|---|---|---:|---:|
| 1 | 1 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_c1cb9eacb5 | Page 25 | 0.429003890 | 0.016393442623 |
| 2 | 2 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_f1f3c4e009 | Page 8 | 0.415259838 | 0.016129032258 |
| 3 | 3 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_ef03dd69f3 | Slide 5 | 0.414090670 | 0.015873015873 |
| 4 | 5 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_957860ad0e | Slide 6 | 0.413136010 | 0.015384615385 |
| 5 | 9 | SAP_Redacted_pdfa-v1 | chk_10630e0da6 | Page 21 | 0.400865920 | 0.014492753623 |

Policy: {"deduplicated_baseline_cutoff": 0.4025180179999999, "minimum_promotable_relevance": 0.36226621619999994, "eligible_document_count": 3, "soft_cap_per_document": 2, "rank_order_backfill": true}

Duplicate removals: [{"removed_chunk_id": "chk_61cb3a73c5", "retained_chunk_id": "chk_ef03dd69f3", "document_id": "doc_cf57d6670b15", "page": null, "slide": 5, "removed_at": "exact normalized-text deduplication"}, {"removed_chunk_id": "chk_2ef94e244e", "retained_chunk_id": "chk_957860ad0e", "document_id": "doc_cf57d6670b15", "page": null, "slide": 6, "removed_at": "exact normalized-text deduplication"}, {"removed_chunk_id": "chk_ca0da581a3", "retained_chunk_id": "chk_f867845048", "document_id": "doc_cf57d6670b15", "page": null, "slide": 4, "removed_at": "exact normalized-text deduplication"}]

Other removals: [{"chunk_id": "chk_f867845048", "document_id": "doc_cf57d6670b15", "page": null, "slide": 4, "removed_at": "final candidate selection", "reason": "document soft-cap during diversity pass"}, {"chunk_id": "chk_6a5418a1a6", "document_id": "doc_e2842eeb2cb3", "page": 11, "slide": null, "removed_at": "final candidate selection", "reason": "final top-K reached"}]

Distribution: [{"document_id": "doc_e2842eeb2cb3", "document_title": "fda_22350s26_and_200678s28_saxagliptin_statistical_prea", "count": 2}, {"document_id": "doc_cf57d6670b15", "document_title": "POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1)", "count": 2}, {"document_id": "doc_3ca7a20cb73b", "document_title": "SAP_Redacted_pdfa-v1", "count": 1}]

SAP in final context: True

## Query B: What is the study design described in the SAP?

### Pre-RRF Top 10

| Rank | Document/title | Chunk | Page/slide | Dense | Lexical | Blended |
|---:|---|---|---|---:|---:|---:|
| 1 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_f1f3c4e009 | Page 8 | 0.6636 | 0.50 | 0.781806450 |
| 2 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_a391234a51 | Page 4 | 0.6254 | 0.50 | 0.762700630 |
| 3 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_9de4abd6aa | Page 2 | 0.6072 | 0.50 | 0.753613125 |
| 4 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_f7a0b03b62 | Page 7 | 0.5943 | 0.50 | 0.747162550 |
| 5 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_6aece63d8a | Page 6 | 0.0000 | 0.50 | 0.700000000 |
| 6 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_e1fe3a6f8d | Page 9 | 0.0000 | 0.50 | 0.700000000 |
| 7 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_957860ad0e | Slide 6 | 0.6442 | 0.25 | 0.647099500 |
| 8 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_2ef94e244e | Slide 6 | 0.6442 | 0.25 | 0.647099500 |
| 9 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_4bfbff44ea | Page 16 | 0.6006 | 0.25 | 0.625293120 |
| 10 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_c18f593fdd | Page 1 | 0.0000 | 0.25 | 0.550000000 |

### Selected Final Context

| Final rank | Original rank | Document/title | Chunk | Page/slide | Blended | Unchanged RRF |
|---:|---:|---|---|---|---:|---:|
| 1 | 1 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_f1f3c4e009 | Page 8 | 0.781806450 | 0.016393442623 |
| 2 | 2 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_a391234a51 | Page 4 | 0.762700630 | 0.016129032258 |
| 3 | 3 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_9de4abd6aa | Page 2 | 0.753613125 | 0.015873015873 |
| 4 | 4 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_f7a0b03b62 | Page 7 | 0.747162550 | 0.015625000000 |
| 5 | 7 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_957860ad0e | Slide 6 | 0.647099500 | 0.014925373134 |

Policy: {"deduplicated_baseline_cutoff": 0.7, "minimum_promotable_relevance": 0.63, "eligible_document_count": 2, "soft_cap_per_document": 3, "rank_order_backfill": true}

Duplicate removals: [{"removed_chunk_id": "chk_2ef94e244e", "retained_chunk_id": "chk_957860ad0e", "document_id": "doc_cf57d6670b15", "page": null, "slide": 6, "removed_at": "exact normalized-text deduplication"}]

Other removals: [{"chunk_id": "chk_6aece63d8a", "document_id": "doc_e2842eeb2cb3", "page": 6, "slide": null, "removed_at": "final candidate selection", "reason": "document soft-cap during diversity pass"}, {"chunk_id": "chk_e1fe3a6f8d", "document_id": "doc_e2842eeb2cb3", "page": 9, "slide": null, "removed_at": "final candidate selection", "reason": "document soft-cap during diversity pass"}, {"chunk_id": "chk_4bfbff44ea", "document_id": "doc_e2842eeb2cb3", "page": 16, "slide": null, "removed_at": "final candidate selection", "reason": "outside relevance gate and not needed for backfill"}, {"chunk_id": "chk_c18f593fdd", "document_id": "doc_e2842eeb2cb3", "page": 1, "slide": null, "removed_at": "final candidate selection", "reason": "outside relevance gate and not needed for backfill"}]

Distribution: [{"document_id": "doc_e2842eeb2cb3", "document_title": "fda_22350s26_and_200678s28_saxagliptin_statistical_prea", "count": 4}, {"document_id": "doc_cf57d6670b15", "document_title": "POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1)", "count": 1}]

SAP in final context: False

## Query C: What is the phase of the clinical trial?

### Pre-RRF Top 10

| Rank | Document/title | Chunk | Page/slide | Dense | Lexical | Blended |
|---:|---|---|---|---:|---:|---:|
| 1 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_f7a0b03b62 | Page 7 | 0.6862 | 0.75 | 0.918096000 |
| 2 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_9010fdbd95 | Page 5 | 0.0000 | 0.75 | 0.850000000 |
| 3 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_d1c91d3597 | Page 17 | 0.6631 | 0.25 | 0.656554980 |
| 4 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_f1f3c4e009 | Page 8 | 0.6593 | 0.25 | 0.654637600 |
| 5 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_1f3be3f7a8 | Page 10 | 0.6583 | 0.25 | 0.654127550 |
| 6 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_a391234a51 | Page 4 | 0.6556 | 0.25 | 0.652809800 |
| 7 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_4bfbff44ea | Page 16 | 0.6483 | 0.25 | 0.649161320 |
| 8 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_e1fe3a6f8d | Page 9 | 0.6416 | 0.25 | 0.645801800 |
| 9 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_ccebeb82d5 | Page 15 | 0.6385 | 0.25 | 0.644245280 |
| 10 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_6aece63d8a | Page 6 | 0.6373 | 0.25 | 0.643637250 |

### Selected Final Context

| Final rank | Original rank | Document/title | Chunk | Page/slide | Blended | Unchanged RRF |
|---:|---:|---|---|---|---:|---:|
| 1 | 1 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_f7a0b03b62 | Page 7 | 0.918096000 | 0.016393442623 |
| 2 | 2 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_9010fdbd95 | Page 5 | 0.850000000 | 0.016129032258 |
| 3 | 3 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_d1c91d3597 | Page 17 | 0.656554980 | 0.015873015873 |
| 4 | 4 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_f1f3c4e009 | Page 8 | 0.654637600 | 0.015625000000 |
| 5 | 5 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_1f3be3f7a8 | Page 10 | 0.654127550 | 0.015384615385 |

Policy: {"deduplicated_baseline_cutoff": 0.65412755, "minimum_promotable_relevance": 0.588714795, "eligible_document_count": 1, "soft_cap_per_document": 5, "rank_order_backfill": true}

Duplicate removals: []

Other removals: [{"chunk_id": "chk_a391234a51", "document_id": "doc_e2842eeb2cb3", "page": 4, "slide": null, "removed_at": "final candidate selection", "reason": "final top-K reached"}, {"chunk_id": "chk_4bfbff44ea", "document_id": "doc_e2842eeb2cb3", "page": 16, "slide": null, "removed_at": "final candidate selection", "reason": "final top-K reached"}, {"chunk_id": "chk_e1fe3a6f8d", "document_id": "doc_e2842eeb2cb3", "page": 9, "slide": null, "removed_at": "final candidate selection", "reason": "final top-K reached"}, {"chunk_id": "chk_ccebeb82d5", "document_id": "doc_e2842eeb2cb3", "page": 15, "slide": null, "removed_at": "final candidate selection", "reason": "final top-K reached"}, {"chunk_id": "chk_6aece63d8a", "document_id": "doc_e2842eeb2cb3", "page": 6, "slide": null, "removed_at": "final candidate selection", "reason": "final top-K reached"}]

Distribution: [{"document_id": "doc_e2842eeb2cb3", "document_title": "fda_22350s26_and_200678s28_saxagliptin_statistical_prea", "count": 5}]

SAP in final context: False

## Query D: What is the primary purpose of the study?

### Pre-RRF Top 10

| Rank | Document/title | Chunk | Page/slide | Dense | Lexical | Blended |
|---:|---|---|---|---:|---:|---:|
| 1 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_83442accfe | Page 14 | 0.0000 | 0.75 | 0.850000000 |
| 2 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_a391234a51 | Page 4 | 0.6164 | 0.50 | 0.758210800 |
| 3 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_6aece63d8a | Page 6 | 0.6098 | 0.50 | 0.754914400 |
| 4 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_462394cd4e | Page 11 | 0.6050 | 0.50 | 0.752522850 |
| 5 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_d1c91d3597 | Page 17 | 0.6027 | 0.50 | 0.751339700 |
| 6 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_f7a0b03b62 | Page 7 | 0.6021 | 0.50 | 0.751029800 |
| 7 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_e0c1023dfd | Page 19 | 0.6011 | 0.50 | 0.750545600 |
| 8 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_1f3be3f7a8 | Page 10 | 0.5991 | 0.50 | 0.749526275 |
| 9 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_4bfbff44ea | Page 16 | 0.5965 | 0.50 | 0.748263600 |
| 10 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_ccebeb82d5 | Page 15 | 0.5934 | 0.50 | 0.746694935 |

### Selected Final Context

| Final rank | Original rank | Document/title | Chunk | Page/slide | Blended | Unchanged RRF |
|---:|---:|---|---|---|---:|---:|
| 1 | 1 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_83442accfe | Page 14 | 0.850000000 | 0.016393442623 |
| 2 | 2 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_a391234a51 | Page 4 | 0.758210800 | 0.016129032258 |
| 3 | 3 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_6aece63d8a | Page 6 | 0.754914400 | 0.015873015873 |
| 4 | 4 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_462394cd4e | Page 11 | 0.752522850 | 0.015625000000 |
| 5 | 5 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_d1c91d3597 | Page 17 | 0.751339700 | 0.015384615385 |

Policy: {"deduplicated_baseline_cutoff": 0.7513396999999999, "minimum_promotable_relevance": 0.67620573, "eligible_document_count": 1, "soft_cap_per_document": 5, "rank_order_backfill": true}

Duplicate removals: []

Other removals: [{"chunk_id": "chk_f7a0b03b62", "document_id": "doc_e2842eeb2cb3", "page": 7, "slide": null, "removed_at": "final candidate selection", "reason": "final top-K reached"}, {"chunk_id": "chk_e0c1023dfd", "document_id": "doc_e2842eeb2cb3", "page": 19, "slide": null, "removed_at": "final candidate selection", "reason": "final top-K reached"}, {"chunk_id": "chk_1f3be3f7a8", "document_id": "doc_e2842eeb2cb3", "page": 10, "slide": null, "removed_at": "final candidate selection", "reason": "final top-K reached"}, {"chunk_id": "chk_4bfbff44ea", "document_id": "doc_e2842eeb2cb3", "page": 16, "slide": null, "removed_at": "final candidate selection", "reason": "final top-K reached"}, {"chunk_id": "chk_ccebeb82d5", "document_id": "doc_e2842eeb2cb3", "page": 15, "slide": null, "removed_at": "final candidate selection", "reason": "final top-K reached"}]

Distribution: [{"document_id": "doc_e2842eeb2cb3", "document_title": "fda_22350s26_and_200678s28_saxagliptin_statistical_prea", "count": 5}]

SAP in final context: False

## Query E: What is a project manager?

### Pre-RRF Top 10

| Rank | Document/title | Chunk | Page/slide | Dense | Lexical | Blended |
|---:|---|---|---|---:|---:|---:|
| 1 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_c18f593fdd | Page 1 | 0.0000 | 0.50 | 0.700000000 |
| 2 | coordin8-q3-verification | chk_7b3c392cc5 | sec_doc_5ceea85f298b_main | 0.4563 | 0.25 | 0.553138370 |
| 3 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_957860ad0e | Slide 6 | 0.5312 | 0.00 | 0.371854931 |
| 4 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_2ef94e244e | Slide 6 | 0.5312 | 0.00 | 0.371854931 |
| 5 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_786b3da1fb | Slide 2 | 0.5052 | 0.00 | 0.353646615 |
| 6 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_496d9bb308 | Slide 2 | 0.5052 | 0.00 | 0.353646615 |
| 7 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_5e92961f8f | Slide 3 | 0.4944 | 0.00 | 0.346064369 |
| 8 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_62f403d9a8 | Slide 3 | 0.4944 | 0.00 | 0.346064369 |
| 9 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_f867845048 | Slide 4 | 0.4545 | 0.00 | 0.318145842 |
| 10 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_ca0da581a3 | Slide 4 | 0.4545 | 0.00 | 0.318145842 |

### Selected Final Context

| Final rank | Original rank | Document/title | Chunk | Page/slide | Blended | Unchanged RRF |
|---:|---:|---|---|---|---:|---:|
| 1 | 1 | fda_22350s26_and_200678s28_saxagliptin_statistical_prea | chk_c18f593fdd | Page 1 | 0.700000000 | 0.016393442623 |
| 2 | 2 | coordin8-q3-verification | chk_7b3c392cc5 | sec_doc_5ceea85f298b_main | 0.553138370 | 0.016129032258 |
| 3 | 3 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_957860ad0e | Slide 6 | 0.371854931 | 0.015873015873 |
| 4 | 5 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_786b3da1fb | Slide 2 | 0.353646615 | 0.015384615385 |
| 5 | 7 | POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1) | chk_5e92961f8f | Slide 3 | 0.346064369 | 0.014925373134 |

Policy: {"deduplicated_baseline_cutoff": 0.346064369, "minimum_promotable_relevance": 0.3114579321, "eligible_document_count": 3, "soft_cap_per_document": 2, "rank_order_backfill": true}

Duplicate removals: [{"removed_chunk_id": "chk_2ef94e244e", "retained_chunk_id": "chk_957860ad0e", "document_id": "doc_cf57d6670b15", "page": null, "slide": 6, "removed_at": "exact normalized-text deduplication"}, {"removed_chunk_id": "chk_496d9bb308", "retained_chunk_id": "chk_786b3da1fb", "document_id": "doc_cf57d6670b15", "page": null, "slide": 2, "removed_at": "exact normalized-text deduplication"}, {"removed_chunk_id": "chk_62f403d9a8", "retained_chunk_id": "chk_5e92961f8f", "document_id": "doc_cf57d6670b15", "page": null, "slide": 3, "removed_at": "exact normalized-text deduplication"}, {"removed_chunk_id": "chk_ca0da581a3", "retained_chunk_id": "chk_f867845048", "document_id": "doc_cf57d6670b15", "page": null, "slide": 4, "removed_at": "exact normalized-text deduplication"}]

Other removals: [{"chunk_id": "chk_f867845048", "document_id": "doc_cf57d6670b15", "page": null, "slide": 4, "removed_at": "final candidate selection", "reason": "document soft-cap during diversity pass"}]

Distribution: [{"document_id": "doc_e2842eeb2cb3", "document_title": "fda_22350s26_and_200678s28_saxagliptin_statistical_prea", "count": 1}, {"document_id": "doc_5ceea85f298b", "document_title": "coordin8-q3-verification", "count": 1}, {"document_id": "doc_cf57d6670b15", "document_title": "POD5_AI_Regulatory_Writing_Copilot_Executive_Presentation (1)", "count": 3}]

SAP in final context: False


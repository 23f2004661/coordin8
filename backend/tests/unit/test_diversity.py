from dataclasses import asdict
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.knowledge_base import KnowledgeBase
from app.retrieval.chunk_retriever import RetrievedChunk
from app.retrieval.diversity import FinalCandidateSelector
from app.retrieval.hybrid import HybridFusion
from app.retrieval.reranker import PassThroughReranker


def chunk(chunk_id, document_id, score, text=None):
    return RetrievedChunk(
        chunk_id=chunk_id, document_id=document_id, score=score,
        content=text if text is not None else chunk_id,
        section_id=None, page=None, slide=None, sheet=None,
    )


def test_exact_normalized_duplicates_keep_highest_ranked_occurrence():
    candidates = [chunk("first", "doc_a", 0.9, "Same\r\ntext"),
                  chunk("second", "doc_b", 0.8, " Same\ntext\n"),
                  chunk("third", "doc_a", 0.7, "Distinct")]
    before = [asdict(item) for item in candidates]
    selected = FinalCandidateSelector().select(candidates, 5)
    assert [item.chunk_id for item in selected] == ["first", "third"]
    assert [asdict(item) for item in candidates] == before


def test_near_text_and_case_differences_are_not_deduplicated():
    candidates = [chunk("first", "doc_a", 0.9, "Study design"),
                  chunk("second", "doc_a", 0.8, "Study  design"),
                  chunk("third", "doc_a", 0.7, "study design"),
                  chunk("fourth", "doc_a", 0.6, "Study designs")]
    assert FinalCandidateSelector().select(candidates, 5) == candidates


def test_single_document_can_fill_all_five_slots():
    candidates = [chunk(f"chunk_{index}", "one_document", 1.0 - index * 0.01) for index in range(7)]
    assert FinalCandidateSelector().select(candidates, 5) == candidates[:5]


def test_second_strong_document_enters_and_multiple_chunks_remain():
    candidates = [chunk(f"chunk_{index}", "doc_a", 1.0 - index * 0.01) for index in range(5)]
    candidates.append(chunk("other", "doc_b", 0.95))
    selected = FinalCandidateSelector().select(candidates, 5)
    assert len(selected) == 5
    assert sum(item.document_id == "doc_a" for item in selected) == 4
    assert selected[-1].chunk_id == "other"


def test_weak_document_cannot_displace_stronger_candidates():
    candidates = [chunk(f"chunk_{index}", "doc_a", 1.0 - index * 0.01) for index in range(5)]
    candidates.append(chunk("weak", "doc_b", 0.05))
    assert FinalCandidateSelector().select(candidates, 5) == candidates[:5]


def query_pattern():
    scores = [0.429003890, 0.415259838, 0.414090670, 0.414090670,
              0.413136010, 0.413136010, 0.402518018, 0.402518018,
              0.400865920, 0.397423740]
    documents = ["doc_a", "doc_a", "doc_b", "doc_b", "doc_b", "doc_b",
                 "doc_b", "doc_b", "doc_c", "doc_a"]
    texts = ["first", "second", "duplicate_1", "duplicate_1", "duplicate_2",
             "duplicate_2", "duplicate_3", "duplicate_3", "third_document", "last"]
    return [chunk(f"chunk_{index + 1}", document, score, text)
            for index, (document, score, text) in enumerate(zip(documents, scores, texts))]


def test_query_a_pattern_uses_generic_diversity_and_preserves_scores():
    candidates = query_pattern()
    before = [asdict(item) for item in candidates]
    selected = FinalCandidateSelector().select(candidates, 5)
    assert [item.chunk_id for item in selected] == ["chunk_1", "chunk_2", "chunk_3", "chunk_5", "chunk_9"]
    assert [item.document_id for item in selected] == ["doc_a", "doc_a", "doc_b", "doc_b", "doc_c"]
    assert [asdict(item) for item in candidates] == before


def test_document_names_do_not_affect_selection():
    candidates = query_pattern()
    baseline = [item.chunk_id for item in FinalCandidateSelector().select(candidates, 5)]
    replacements = {"doc_a": "arbitrary.pdf", "doc_b": "another-title", "doc_c": "unrelated-id"}
    for item in candidates:
        item.document_id = replacements[item.document_id]
    assert [item.chunk_id for item in FinalCandidateSelector().select(candidates, 5)] == baseline


def test_rrf_scores_remain_original_rank_scores_and_reranker_contract_is_unchanged():
    candidates = query_pattern()
    relevance = {item.chunk_id: item.score for item in candidates}
    fused = HybridFusion().fuse_ranks(candidates, [], top_k=len(candidates))
    ranked = PassThroughReranker().rerank("arbitrary question", fused, top_n=len(fused))
    assert [item.chunk_id for item in ranked] == [item.chunk_id for item in candidates]
    before = [asdict(item) for item in ranked]
    selected = FinalCandidateSelector().select(ranked, 5, relevance)
    assert selected[-1].chunk_id == "chunk_9"
    for rank, item in enumerate(ranked, start=1):
        assert item.score == pytest.approx(1.0 / (60 + rank))
        assert item.reranker_score == round(item.score, 4)
    assert selected[-1].score == pytest.approx(1.0 / 69)
    assert [asdict(item) for item in ranked] == before


def test_original_relevance_blocks_weak_alternative_despite_flat_rrf_scores():
    candidates = [chunk(f"chunk_{index}", "doc_a", 0.9 - index * 0.01) for index in range(5)]
    candidates.append(chunk("weak", "doc_b", 0.01))
    relevance = {item.chunk_id: item.score for item in candidates}
    fused = HybridFusion().fuse_ranks(candidates, [], top_k=6)
    assert "weak" not in [item.chunk_id for item in FinalCandidateSelector().select(fused, 5, relevance)]


def test_knowledge_base_retains_pool_until_generic_selection():
    candidates = query_pattern()
    selector = Mock(wraps=FinalCandidateSelector())
    kb = SimpleNamespace(
        fusion=HybridFusion(), reranker=PassThroughReranker(), final_selector=selector
    )
    selected = KnowledgeBase._select_final_candidates(kb, "arbitrary question", candidates, 5)
    assert len(selector.select.call_args.args[0]) == 10
    assert selected[-1].chunk_id == "chunk_9"
    assert selector.select.call_args.kwargs["relevance_scores"]["chunk_9"] == 0.400865920


def test_empty_and_zero_limit_are_safe():
    selector = FinalCandidateSelector()
    assert selector.select([], 5) == []
    assert selector.select([chunk("first", "doc", 1.0)], 0) == []
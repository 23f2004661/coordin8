from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from app.indexing.embeddings import (
    LocalSentenceTransformerEmbeddingProvider,
    MockEmbeddingProvider,
    get_embedding_provider,
)


@pytest.fixture
def local_model():
    model = Mock()
    model.get_sentence_embedding_dimension.return_value = 384
    model.encode.return_value.tolist.return_value = [[1.0] + [0.0] * 383]
    with patch("app.indexing.embeddings._load_local_model", return_value=model):
        yield model


@pytest.mark.parametrize("provider_name, expected_class", [
    ("mock", MockEmbeddingProvider),
    ("local", LocalSentenceTransformerEmbeddingProvider),
])
def test_factory_honors_configuration(provider_name, expected_class, local_model):
    settings = SimpleNamespace(
        embedding_provider=provider_name,
        embedding_model="BAAI/bge-small-en-v1.5",
        embedding_dimensions=384,
    )
    with patch("app.indexing.embeddings.get_settings", return_value=settings):
        provider = get_embedding_provider()
    assert isinstance(provider, expected_class)
    assert len(provider.embed_text("phase 3 clinical trial")) == 384
    if provider_name == "local":
        assert provider.model_name == settings.embedding_model


def test_local_batch_and_empty_input(local_model):
    provider = LocalSentenceTransformerEmbeddingProvider("BAAI/bge-small-en-v1.5", 384)
    assert provider.embed_batch([]) == []
    local_model.encode.return_value.tolist.return_value = [[0.0] * 384, [0.0] * 384]
    assert [len(vector) for vector in provider.embed_batch(["study", "manager"])] == [384, 384]
    assert local_model.encode.call_args.kwargs["normalize_embeddings"] is True


def test_local_rejects_configured_dimension_mismatch(local_model):
    with pytest.raises(ValueError, match="configured 1024.*returns 384"):
        LocalSentenceTransformerEmbeddingProvider("BAAI/bge-small-en-v1.5", 1024)


def test_local_rejects_invalid_output_dimension(local_model):
    provider = LocalSentenceTransformerEmbeddingProvider("BAAI/bge-small-en-v1.5", 384)
    local_model.encode.return_value.tolist.return_value = [[0.0] * 383]
    with pytest.raises(ValueError, match="invalid vector dimensions"):
        provider.embed_text("study")


def test_local_loading_failure_never_falls_back_to_mock():
    settings = SimpleNamespace(
        embedding_provider="local", embedding_model="missing-model", embedding_dimensions=384
    )
    with patch("app.indexing.embeddings.get_settings", return_value=settings), patch(
        "app.indexing.embeddings._load_local_model", side_effect=OSError("Model unavailable")
    ), patch("app.indexing.embeddings.MockEmbeddingProvider") as mock_provider:
        with pytest.raises(RuntimeError, match="Cannot load local embedding model"):
            get_embedding_provider()
        mock_provider.assert_not_called()


def test_unknown_provider_fails_explicitly():
    with patch("app.indexing.embeddings.get_settings", return_value=SimpleNamespace(
        embedding_provider="unknown"
    )):
        with pytest.raises(ValueError, match="Unsupported embedding provider"):
            get_embedding_provider()


def test_knowledge_base_shares_local_provider(tmp_path, local_model):
    from app.knowledge_base import KnowledgeBase

    provider = LocalSentenceTransformerEmbeddingProvider("BAAI/bge-small-en-v1.5", 384)
    with patch("app.indexing.qdrant.QdrantManager._init_client"):
        kb = KnowledgeBase(
            "provider_wiring", storage_dir=tmp_path,
            db_url=f"sqlite:///{tmp_path / 'metadata.db'}", embedding_provider=provider,
        )
    try:
        assert kb.embeddings is provider
        assert kb.index_pipeline.embeddings is provider
        assert kb.doc_retriever.embeddings is provider
        assert kb.chk_retriever.embeddings is provider
        assert kb.qdrant.vector_size == 384
    finally:
        kb.close()


def test_new_qdrant_collections_use_provider_dimension():
    from app.indexing.qdrant import QdrantManager

    with patch.object(QdrantManager, "_init_client"):
        manager = QdrantManager(collection_prefix="dimension_test", vector_size=384)
    manager.client = Mock()
    manager.client.get_collections.return_value.collections = []
    manager.ensure_collections()
    assert manager.client.create_collection.call_count == 4
    for call in manager.client.create_collection.call_args_list:
        assert call.kwargs["vectors_config"].size == 384


def test_existing_mock_index_is_rejected_before_any_collection_write():
    from app.indexing.qdrant import QdrantManager

    with patch.object(QdrantManager, "_init_client"):
        manager = QdrantManager(collection_prefix="dimension_test", vector_size=384)
    manager.client = Mock()
    manager.client.get_collections.return_value.collections = [
        SimpleNamespace(name="dimension_test_chunks")
    ]
    manager.client.get_collection.return_value.config.params.vectors = SimpleNamespace(size=1024)
    with pytest.raises(ValueError, match="Rebuild the scoped index"):
        manager.ensure_collections()
    manager.client.create_collection.assert_not_called()
    manager.client.delete_collection.assert_not_called()
    manager.client.upsert.assert_not_called()


def test_rebuild_mapping_preserves_payload_and_omits_only_approved_orphan():
    from scripts.reindex import APPROVED_ORPHAN, build_sources

    payload = {"chunk_id": "chunk_body", "document_id": "doc_sap", "page": 109,
               "section_id": "section_109", "source": "original.pdf"}
    points = [
        SimpleNamespace(id=1, payload=payload),
        SimpleNamespace(id=2, payload={"chunk_id": APPROVED_ORPHAN}),
    ]
    chunks = {"chunk_body": {"document_id": "doc_sap", "content": "Study design body text"}}
    sources, omitted = build_sources({"project_chunks": points}, chunks)
    assert sources["project_chunks"] == [(1, payload, "Study design body text")]
    assert sources["project_chunks"][0][1] is payload
    assert omitted == [APPROVED_ORPHAN]


def test_rebuild_rejects_unapproved_orphan():
    from scripts.reindex import build_sources

    with pytest.raises(ValueError, match="Unapproved point"):
        build_sources({"project_chunks": [SimpleNamespace(id=1, payload={"chunk_id": "unknown"})]}, {})


def test_rebuild_rejects_missing_catalog_chunks():
    from scripts.reindex import build_sources

    with pytest.raises(ValueError, match="Catalog chunks"):
        build_sources({"project_chunks": []}, {"missing": {"document_id": "doc", "content": "body"}})


def test_rebuild_rejects_document_association_mismatch():
    from scripts.reindex import build_sources

    point = SimpleNamespace(id=1, payload={"chunk_id": "chunk", "document_id": "wrong"})
    with pytest.raises(ValueError, match="Document association mismatch"):
        build_sources({"project_chunks": [point]}, {"chunk": {"document_id": "doc", "content": "body"}})


def test_rebuild_rejects_empty_text():
    from scripts.reindex import build_sources

    point = SimpleNamespace(id=1, payload={"chunk_id": "chunk", "document_id": "doc"})
    with pytest.raises(ValueError, match="no valid stored text"):
        build_sources({"project_chunks": [point]}, {"chunk": {"document_id": "doc", "content": " "}})


def test_rebuild_cli_rejects_other_projects(monkeypatch):
    from scripts.reindex import main
    import sys

    monkeypatch.setattr(sys, "argv", ["reindex.py", "--project-id", "other-project"])
    with pytest.raises(SystemExit) as error:
        main()
    assert error.value.code == 2
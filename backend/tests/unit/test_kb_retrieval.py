"""Unit tests for retrieval and context assembly via KnowledgeBase."""

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.db.session import Base
from app.db.models import ChunkRecord
from app.knowledge_base import KnowledgeBase
from app.indexing.qdrant import QdrantManager
from app.retrieval.chunk_retriever import ChunkRetriever, LEXICAL_STOPWORDS, is_image_placeholder
from app.retrieval.query_parser import ParsedQuery, QueryParser
from app.retrieval.section_retriever import SectionCandidate


class TestImagePlaceholder(unittest.TestCase):
    def test_only_standalone_placeholders_match(self):
        cases = [
            ("[Embedded Image on Page 109: Im0.png]", True),
            ("[Embedded Image on Page 139: Im0.png]", True),
            (" \n[Embedded Image on Page 109: Im0.png]\t", True),
            ("The objective of this study is to evaluate...", False),
            ("A bar chart showing enrollment by treatment arm...", False),
            ("[Embedded Image on Page 109: Im0.png]\nA bar chart showing enrollment.", False),
            ("See [Embedded Image on Page 109: Im0.png] for enrollment.", False),
            ("[Embedded Image on Page 109: Im0.png] extra text", False),
            ("", False),
            (" \n\t", False),
        ]
        for content, expected in cases:
            with self.subTest(content=content):
                self.assertEqual(is_image_placeholder(content), expected)


class TestKnowledgeBaseRetrieval(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.storage_path = Path(self.temp_dir.name)
        self.kb = KnowledgeBase(
            kb_id="retrieval_test_kb",
            storage_dir=self.storage_path,
            db_url=f"sqlite:///{self.storage_path / 'retrieval.db'}",
            collection_prefix="retrieval_test_qdrant",
        )

        # Ingest test documentation
        doc1_content = (
            "# API Gateway Migration Plan\n\n"
            "## Decision Rationale\n"
            "We decided to move the API gateway migration to Q4 due to dependency on Kubernetes v1.30.\n\n"
            "## Risk Assessment\n"
            "Upstream latency must remain below 45 milliseconds during traffic switchover."
        ).encode("utf-8")

        self.doc1 = self.kb.ingest_bytes(
            content=doc1_content,
            filename="api_gateway_plan.md",
            title="Gateway Migration Strategy",
        )

    def tearDown(self):
        self.kb.close()
        self.temp_dir.cleanup()

    def test_search_hierarchical_hybrid(self):
        """Test hierarchical search across ingested chunks."""
        search_res = self.kb.search("Why was API gateway moved to Q4?", limit=3)

        self.assertEqual(search_res["kb_id"], "retrieval_test_kb")
        self.assertGreater(search_res["candidate_documents"], 0)
        self.assertGreater(len(search_res["results"]), 0)

        top_hit = search_res["results"][0]
        self.assertIn("chunk_id", top_hit)
        self.assertIn("document_id", top_hit)
        self.assertEqual(top_hit["document_title"], "Gateway Migration Strategy")
        self.assertIn("provenance", top_hit)
        self.assertIn("lineage", top_hit)
        self.assertIn("content", top_hit)

    def test_query_context_prompt_assembly(self):
        """Test that query_context formats evidence blocks and citations for LLM consumption."""
        ctx_res = self.kb.query_context("Kubernetes latency constraint", limit=3)

        self.assertEqual(ctx_res["kb_id"], "retrieval_test_kb")
        self.assertIn("formatted_context", ctx_res)
        self.assertIn("evidence_units", ctx_res)
        self.assertGreater(len(ctx_res["evidence_units"]), 0)

        # Verify evidence citations conform to Section 20
        first_evidence = ctx_res["evidence_units"][0]
        self.assertIn("citation", first_evidence)
        self.assertIn("content", first_evidence)
        self.assertIn("--- EVIDENCE ITEM", ctx_res["formatted_context"])
        self.assertGreater(ctx_res["estimated_tokens"], 0)

    def test_search_scoped_to_document_id(self):
        """Test searching with an explicit document_id filter."""
        doc2_content = b"# Unrelated Marketing Document\nQuarterly brand guidelines and logo rules."
        doc2 = self.kb.ingest_bytes(doc2_content, "marketing.md", title="Marketing Guide")

        # Search specifically within doc1
        res = self.kb.search("guidelines", document_id=self.doc1["document_id"])
        # Should not return doc2 chunks
        for item in res["results"]:
            self.assertEqual(item["document_id"], self.doc1["document_id"])

    def test_placeholders_cannot_displace_substantive_image_labelled_chunks(self):
        document_id = self.doc1["document_id"]
        section_id = f"sec_{document_id}_main"
        contents = {
            "chk_placeholder_109": "[Embedded Image on Page 109: Im0.png]",
            "chk_placeholder_139": "[Embedded Image on Page 139: Im0.png]",
            "chk_body": "The objective of this study is to evaluate treatment safety.",
            "chk_chart": "A bar chart showing enrollment by treatment arm.",
        }
        with self.kb.session() as db:
            for chunk_id, content in contents.items():
                db.add(ChunkRecord(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    section_id=section_id,
                    content_type="image",
                    content=content,
                ))
            db.commit()

        hits = [
            {"payload": {"chunk_id": chunk_id}, "score": score}
            for chunk_id, score in [
                ("chk_placeholder_109", 1.0),
                ("chk_placeholder_139", 0.99),
                ("chk_body", 0.8),
                ("chk_chart", 0.7),
            ]
        ]
        with patch.object(self.kb.qdrant, "client", object()), patch.object(
            self.kb.qdrant, "search_points", return_value=hits
        ):
            with self.kb.session() as db:
                chunks = self.kb.chk_retriever.retrieve_chunks(
                    db,
                    [SectionCandidate(document_id, section_id, "Main", None, 0.5)],
                    self.kb.query_parser.parse("overview"),
                    limit=2,
                )
            context = self.kb.query_context("overview", limit=2)

        self.assertEqual([chunk.chunk_id for chunk in chunks], ["chk_body", "chk_chart"])
        self.assertEqual(
            {unit["content"] for unit in context["evidence_units"]},
            {contents["chk_body"], contents["chk_chart"]},
        )
        self.assertNotIn("[Embedded Image on Page", context["formatted_context"])

    def test_placeholder_only_document_produces_no_evidence(self):
        document_id = self.doc1["document_id"]
        with self.kb.session() as db:
            db.query(ChunkRecord).filter(ChunkRecord.document_id == document_id).delete()
            db.add(ChunkRecord(
                chunk_id="chk_placeholder_only",
                document_id=document_id,
                content_type="image",
                content="[Embedded Image on Page 109: Im0.png]",
            ))
            db.commit()

        with patch.object(self.kb.qdrant, "client", None):
            context = self.kb.query_context("overview")

        self.assertEqual(context["evidence_units"], [])
        self.assertEqual(context["formatted_context"], "")

    def test_dense_budget_excludes_placeholders_before_limit_for_sap_query(self):
        document_id = self.doc1["document_id"]
        contents = {
            "chk_dense_placeholder_109": "[Embedded Image on Page 109: Im0.png]",
            "chk_dense_placeholder_139": "[Embedded Image on Page 139: Im0.png]",
            "chk_dense_sap_body": "The objective of this study is to evaluate treatment safety.",
            "chk_dense_chart": "A bar chart showing enrollment by treatment arm.",
        }
        with self.kb.session() as db:
            for chunk_id, content in contents.items():
                db.add(ChunkRecord(
                    chunk_id=chunk_id, document_id=document_id,
                    content_type="image", content=content,
                ))
            db.commit()
        pool = [
            SimpleNamespace(
                id=rank, score=score,
                payload={"chunk_id": chunk_id, "document_id": document_id},
            )
            for rank, (chunk_id, score) in enumerate([
                ("chk_dense_placeholder_109", 1.0),
                ("chk_dense_placeholder_139", 0.99),
                ("chk_dense_sap_body", 0.8),
                ("chk_dense_chart", 0.7),
            ], start=1)
        ]
        requests = []
        dense_results = []

        def query_points(**kwargs):
            requests.append(kwargs)
            condition = kwargs["query_filter"].must_not[0]
            self.assertEqual(condition.key, "chunk_id")
            excluded = set(condition.match.any)
            eligible = [point for point in pool if point.payload["chunk_id"] not in excluded]
            selected = eligible[:kwargs["limit"]]
            dense_results.append([point.payload["chunk_id"] for point in selected])
            return SimpleNamespace(points=selected)

        client = SimpleNamespace(query_points=query_points)
        with patch.object(self.kb.qdrant, "client", client):
            with self.kb.session() as db:
                chunks = self.kb.chk_retriever.retrieve_chunks(
                    db,
                    [SectionCandidate(document_id, "main", "SAP", None, 0.5)],
                    self.kb.query_parser.parse("What is SAP_Redacted_pdfa-v1.pdf about?"),
                    limit=1,
                )
                self.assertEqual(db.query(ChunkRecord).filter(
                    ChunkRecord.chunk_id.in_(contents)
                ).count(), 4)
        self.assertEqual(requests[0]["limit"], 2)
        self.assertEqual(dense_results, [["chk_dense_sap_body", "chk_dense_chart"]])
        self.assertEqual(set(requests[0]["query_filter"].must_not[0].match.any), {
            "chk_dense_placeholder_109", "chk_dense_placeholder_139"
        })
        self.assertEqual(chunks[0].chunk_id, "chk_dense_sap_body")
        self.assertEqual(chunks[0].dense_score, 0.8)
        self.assertEqual(chunks[0].sparse_score, 0.0)
        self.assertAlmostEqual(chunks[0].score, 0.56)


class TestQdrantPlaceholderFilter(unittest.TestCase):
    def test_filter_is_forwarded_before_limit_for_both_client_apis(self):
        points = [SimpleNamespace(id=1, score=0.87, payload={"chunk_id": "body"})]
        for modern in (True, False):
            with self.subTest(modern=modern):
                with patch.object(QdrantManager, "_init_client"):
                    manager = QdrantManager(collection_prefix="isolated_test")
                method = Mock(return_value=SimpleNamespace(points=points) if modern else points)
                manager.client = SimpleNamespace(**{
                    "query_points" if modern else "search": method
                })
                hits = manager.search_points(
                    "isolated_test_chunks", [1.0], limit=2, excluded_chunk_ids=["placeholder"]
                )
                options = method.call_args.kwargs
                self.assertEqual(options["collection_name"], "isolated_test_chunks")
                self.assertEqual(options["limit"], 2)
                self.assertEqual(options["query_filter"].must_not[0].key, "chunk_id")
                self.assertEqual(options["query_filter"].must_not[0].match.any, ["placeholder"])
                self.assertEqual(hits, [{"id": 1, "score": 0.87, "payload": {"chunk_id": "body"}}])

    def test_empty_exclusion_preserves_unfiltered_search(self):
        with patch.object(QdrantManager, "_init_client"):
            manager = QdrantManager()
        method = Mock(return_value=SimpleNamespace(points=[]))
        manager.client = SimpleNamespace(query_points=method)
        self.assertEqual(manager.search_points("test_chunks", [1.0], excluded_chunk_ids=[]), [])
        self.assertNotIn("query_filter", method.call_args.kwargs)


class TestLexicalStopwords(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.qdrant = SimpleNamespace(client=None, prefix="test", search_points=Mock())
        self.retriever = ChunkRetriever(qdrant=self.qdrant)
        self.section = SectionCandidate("doc_test", "main", "Main", None, 0.5)

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def retrieve(self, content, keywords, summary=None, dense=None, query="Unmatched question"):
        self.db.query(ChunkRecord).delete()
        self.db.add(ChunkRecord(
            chunk_id="chunk_test", document_id="doc_test", content=content,
            summary=summary, content_type="image",
        ))
        self.db.commit()
        self.qdrant.client = object() if dense is not None else None
        self.qdrant.search_points.return_value = [
            {"payload": {"chunk_id": "chunk_test"}, "score": dense}
        ] if dense is not None else []
        parsed = ParsedQuery(raw_query=query, keywords=list(keywords))
        result = self.retriever.retrieve_chunks(self.db, [self.section], parsed, limit=1)[0]
        self.assertEqual(parsed.keywords, list(keywords))
        return result

    def test_stopwords_never_add_body_or_summary_keyword_boosts(self):
        for word in sorted(LEXICAL_STOPWORDS):
            with self.subTest(word=word):
                chunk = self.retrieve(
                    f"{word.upper()} generic prose", [word.upper()], summary=f"{word} summary"
                )
                self.assertEqual(chunk.sparse_score, 0.0)
                self.assertEqual(chunk.score, 0.2)

    def test_domain_keywords_remain_usable(self):
        for word in ["study", "design", "phase", "clinical", "trial", "purpose", "project", "manager"]:
            with self.subTest(word=word):
                chunk = self.retrieve(f"Relevant {word} evidence", ["what", word])
                self.assertEqual(chunk.sparse_score, 0.25)
                self.assertAlmostEqual(chunk.score, 0.55)

    def test_filename_question_words_do_not_boost_unrelated_text(self):
        query = "What is SAP_Redacted_pdfa-v1.pdf about?"
        parsed = QueryParser().parse(query)
        chunk = self.retrieve(
            "What is this presentation about?", parsed.keywords,
            summary="What is this about?", dense=0.5543851, query=query,
        )
        self.assertEqual(chunk.sparse_score, 0.0)
        self.assertAlmostEqual(chunk.score, 0.7 * 0.5543851)
        sap = self.retrieve("Statistical analysis plan body", parsed.keywords, dense=0.5726656, query=query)
        self.assertAlmostEqual(sap.score, 0.40086592)
        self.assertGreater(sap.score, chunk.score)
        self.assertNotIn("sap", QueryParser().parse("What is SAP about?").keywords)

    def test_exact_phrase_and_summary_bonuses_are_preserved(self):
        exact = self.retrieve("What is the study?", ["what", "study"], query="What is the study?")
        self.assertEqual(exact.sparse_score, 0.85)
        self.assertAlmostEqual(exact.score, 0.4 + 0.6 * 0.85)
        summary = self.retrieve("Body without domain match", ["what", "study"], summary="Study summary")
        self.assertEqual(summary.sparse_score, 0.2)
        self.assertAlmostEqual(summary.score, 0.52)

    def test_dense_formulas_and_hybrid_bonus_are_preserved(self):
        dense_only = self.retrieve("Generic prose", ["what"], dense=0.8)
        self.assertAlmostEqual(dense_only.score, 0.7 * 0.8)
        hybrid = self.retrieve("Study evidence", ["what", "study"], dense=0.8)
        self.assertEqual(hybrid.sparse_score, 0.25)
        self.assertAlmostEqual(hybrid.score, 0.5 * 0.8 + 0.5 * 0.25 + 0.2)


if __name__ == "__main__":
    unittest.main()

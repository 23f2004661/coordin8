"""Rigorous RAG Tests across Heterogeneous Document Modalities.

Tests ingestion, chunking, hierarchical indexing, search, and citation assembly
for:
1. Plain Text (.txt)
2. Markdown (.md)
3. HTML documents (.html)
4. Excel spreadsheets (.xlsx)
5. CSV tables (.csv)
6. Code files (Python .py and JSON .json)
7. Microsoft Word documents (.docx)
8. Microsoft PowerPoint presentations (.pptx)
9. PDF files with native text (.pdf)
10. PDF files with embedded images (.pdf)
11. Multi-modal simultaneous ingestion and cross-retrieval
"""

import io
import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image, ImageDraw
import docx
import openpyxl
import pptx

from app.knowledge_base import KnowledgeBase


def make_test_pdf_bytes(text_content: str) -> bytes:
    """Construct a valid minimal single-page PDF with embedded text stream."""
    safe_text = text_content.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    stream_content = f"BT /F1 12 Tf 50 700 Td ({safe_text}) Tj ET".encode("utf-8")
    stream_len = len(stream_content)
    header = (
        f"%PDF-1.4\n"
        f"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
        f"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
        f"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj\n"
        f"4 0 obj << /Length {stream_len} >> stream\n"
    ).encode("utf-8")
    footer = (
        b"\nendstream\nendobj\n"
        b"5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n"
        b"xref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000266 00000 n \n0000000373 00000 n \n"
        b"trailer << /Size 6 /Root 1 0 R >>\nstartxref\n450\n%%EOF\n"
    )
    return header + stream_content + footer


class TestModalitiesRAG(unittest.TestCase):
    """Rigorous tests covering ingestion and hierarchical retrieval across all modalities."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp_dir.name)
        self.kb = KnowledgeBase(
            kb_id="modalities_test_kb",
            storage_dir=self.workspace,
            collection_prefix="modalities_qdrant",
        )

    def tearDown(self):
        self.kb.close()
        self.temp_dir.cleanup()

    # 1. Plain Text (.txt)
    def test_rag_text_document(self):
        """Test RAG pipeline on plain text documents."""
        txt_path = self.workspace / "infrastructure_backup.txt"
        txt_path.write_text(
            "Infrastructure Backup Policy\n\n"
            "All primary PostgreSQL database snapshots occur every 4 hours.\n"
            "Cold storage backups are replicated to the us-west-2 disaster recovery vault.",
            encoding="utf-8",
        )

        res = self.kb.ingest_file(txt_path, title="Infrastructure Backup Policy")
        self.assertTrue(res["success"])
        self.assertEqual(res["file_type"], "txt")

        # Query for specific backup frequency
        search_res = self.kb.search("database snapshots frequency hours")
        self.assertGreater(len(search_res["results"]), 0)
        top = search_res["results"][0]
        self.assertIn("4 hours", top["content"])
        self.assertEqual(top["document_title"], "Infrastructure Backup Policy")

        # Verify prompt context assembly
        ctx = self.kb.query_context("snapshots frequency")
        self.assertIn("4 hours", ctx["formatted_context"])
        self.assertIn("Infrastructure Backup Policy", ctx["formatted_context"])

    # 2. Markdown (.md)
    def test_rag_markdown_document(self):
        """Test RAG pipeline on Markdown documents with headings and lists."""
        md_path = self.workspace / "service_slas.md"
        md_path.write_text(
            "# System Service Level Agreements\n\n"
            "## Network Latency Requirements\n"
            "Maximum P99 response latency is strictly capped at 25 milliseconds for internal services.\n\n"
            "## Availability Targets\n"
            "* Tier 1 core services: 99.999% uptime\n"
            "* Tier 2 internal dashboards: 99.9% uptime",
            encoding="utf-8",
        )

        res = self.kb.ingest_file(md_path, title="Service SLAs")
        self.assertTrue(res["success"])
        self.assertEqual(res["file_type"], "md")

        search_res = self.kb.search("P99 response latency milliseconds limit")
        self.assertGreater(len(search_res["results"]), 0)
        self.assertIn("25 milliseconds", search_res["results"][0]["content"])

    # 3. HTML Document (.html)
    def test_rag_html_document(self):
        """Test RAG pipeline on HTML documents with tag stripping and structure extraction."""
        html_path = self.workspace / "security_spec.html"
        html_path.write_text(
            "<!DOCTYPE html>\n"
            "<html>\n"
            "<head><title>API Security Specification</title></head>\n"
            "<body>\n"
            "<h1>API Security Architecture</h1>\n"
            "<p>All incoming webhook requests must verify HMAC SHA256 signatures before processing.</p>\n"
            "<ul>\n"
            "<li>Signature header: X-Coordin8-Signature</li>\n"
            "<li>Clock skew tolerance: 300 seconds</li>\n"
            "</ul>\n"
            "</body>\n"
            "</html>",
            encoding="utf-8",
        )

        res = self.kb.ingest_file(html_path, title="Security Spec")
        self.assertTrue(res["success"])

        # Search for signature requirement
        search_res = self.kb.search("webhook HMAC SHA256 signature verification")
        self.assertGreater(len(search_res["results"]), 0)
        top_content = search_res["results"][0]["content"]
        self.assertIn("HMAC SHA256", top_content)
        self.assertIn("300 seconds", top_content)
        # Ensure HTML boilerplate tags were cleanly parsed
        self.assertNotIn("<!DOCTYPE html>", top_content)

    # 4. Excel Spreadsheets (.xlsx)
    def test_rag_excel_document(self):
        """Test RAG pipeline on native Excel workbooks created with openpyxl."""
        xlsx_path = self.workspace / "regional_revenue.xlsx"
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Q3_Targets"
        ws.append(["Region", "TargetSales", "RegionalLead"])
        ws.append(["EMEA", 9500000, "Elena Rostova"])
        ws.append(["APAC", 12400000, "Kenji Sato"])
        ws.append(["Americas", 18200000, "Marcus Sterling"])
        wb.save(str(xlsx_path))

        res = self.kb.ingest_file(xlsx_path, title="Regional Revenue Q3")
        self.assertTrue(res["success"])
        self.assertEqual(res["file_type"], "xlsx")

        search_res = self.kb.search("Elena Rostova EMEA TargetSales")
        self.assertGreater(len(search_res["results"]), 0)
        top = search_res["results"][0]
        self.assertIn("Elena Rostova", top["content"])
        self.assertIn("9500000", top["content"])
        # Provenance should indicate sheet
        self.assertIn("Q3_Targets", top["provenance"])

    # 5. CSV Table (.csv)
    def test_rag_csv_document(self):
        """Test RAG pipeline on comma-separated tabular data."""
        csv_path = self.workspace / "k8s_clusters.csv"
        csv_path.write_text(
            "ClusterName,NodeCount,CloudProvider,Region\n"
            "us-east-cluster-9,128,AWS,us-east-1\n"
            "eu-west-cluster-4,64,GCP,europe-west3\n"
            "apac-south-cluster-2,32,Azure,ap-south-1\n",
            encoding="utf-8",
        )

        res = self.kb.ingest_file(csv_path, title="Kubernetes Clusters")
        self.assertTrue(res["success"])

        search_res = self.kb.search("us-east-cluster-9 AWS node count")
        self.assertGreater(len(search_res["results"]), 0)
        self.assertIn("us-east-cluster-9", search_res["results"][0]["content"])
        self.assertIn("128", search_res["results"][0]["content"])

    # 6. Code Files (Python .py and JSON .json)
    def test_rag_code_python_and_json(self):
        """Test RAG pipeline on programming language code files and configuration schemas."""
        py_path = self.workspace / "rate_limiter.py"
        py_path.write_text(
            "# Token bucket rate limiter implementation\n\n"
            "def check_client_rate_limit(client_id: str, max_tokens: int = 100) -> bool:\n"
            "    '''Enforce token bucket throttling with Redis atomic increment.'''\n"
            "    current_tokens = redis.get(f'tokens:{client_id}')\n"
            "    return int(current_tokens) <= max_tokens\n",
            encoding="utf-8",
        )

        json_path = self.workspace / "cluster_config.json"
        json_path.write_text(
            json.dumps(
                {
                    "cluster_name": "production-eu-west-cluster",
                    "max_replicas": 48,
                    "autoscaling_threshold_cpu": "75%",
                    "ingress_class": "traefik-v3",
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        self.kb.ingest_file(py_path, title="Rate Limiter Implementation")
        self.kb.ingest_file(json_path, title="Cluster Config JSON")

        # Search Python code
        py_res = self.kb.search("check_client_rate_limit token bucket redis")
        self.assertGreater(len(py_res["results"]), 0)
        self.assertIn("check_client_rate_limit", py_res["results"][0]["content"])

        # Search JSON config
        json_res = self.kb.search("production-eu-west-cluster autoscaling threshold")
        self.assertGreater(len(json_res["results"]), 0)
        self.assertIn("production-eu-west-cluster", json_res["results"][0]["content"])

    # 7. Microsoft Word Document (.docx)
    def test_rag_word_document(self):
        """Test RAG pipeline on Microsoft Word (.docx) files created with python-docx."""
        docx_path = self.workspace / "vendor_agreement.docx"
        doc = docx.Document()
        doc.add_heading("Master Services Agreement", level=1)
        doc.add_paragraph("This agreement governs the enterprise subscription terms between the parties.")
        doc.add_heading("Termination and Term", level=2)
        doc.add_paragraph("The minimum commitment duration is 36 consecutive months from effective date.")

        t = doc.add_table(rows=2, cols=2)
        t.cell(0, 0).text = "Deliverable"
        t.cell(0, 1).text = "SLA"
        t.cell(1, 0).text = "Ticket Response"
        t.cell(1, 1).text = "Under 15 minutes"
        doc.save(str(docx_path))

        res = self.kb.ingest_file(docx_path, title="Vendor Agreement")
        self.assertTrue(res["success"])
        self.assertEqual(res["file_type"], "docx")

        search_res = self.kb.search("minimum commitment duration months")
        self.assertGreater(len(search_res["results"]), 0)
        top = search_res["results"][0]
        self.assertIn("36 consecutive months", top["content"])
        self.assertEqual(top["document_title"], "Vendor Agreement")

    # 8. Microsoft PowerPoint Presentation (.pptx)
    def test_rag_powerpoint_presentation(self):
        """Test RAG pipeline on PowerPoint (.pptx) files created with python-pptx."""
        pptx_path = self.workspace / "architecture_review.pptx"
        prs = pptx.Presentation()

        # Slide 1: Title
        slide1 = prs.slides.add_slide(prs.slide_layouts[0])
        slide1.shapes.title.text = "Q4 Engineering Strategic Roadmap"
        slide1.placeholders[1].text = "Presented by Core Platform Architecture Team"

        # Slide 2: Migration Details
        slide2 = prs.slides.add_slide(prs.slide_layouts[1])
        slide2.shapes.title.text = "Gateway Migration Milestones"
        slide2.placeholders[1].text = (
            "Milestone Alpha: Envoy proxy migration completed by November 15.\n"
            "Milestone Beta: Cut over public DNS traffic with zero downtime."
        )
        prs.save(str(pptx_path))

        res = self.kb.ingest_file(pptx_path, title="Architecture Review Deck")
        self.assertTrue(res["success"])
        self.assertEqual(res["file_type"], "pptx")

        search_res = self.kb.search("Envoy proxy migration completed date")
        self.assertGreater(len(search_res["results"]), 0)
        top = search_res["results"][0]
        self.assertIn("November 15", top["content"])
        # Provenance should reflect slide number
        self.assertIn("Slide", top["provenance"])

    # 9. PDF File with Native Text (.pdf)
    def test_rag_pdf_with_text(self):
        """Test RAG pipeline on a PDF containing native text streams."""
        pdf_path = self.workspace / "compliance_policy.pdf"
        text_payload = "Strict Compliance Rule: Hardware security modules must use FIPS 140-3 Level 4 validation."
        pdf_bytes = make_test_pdf_bytes(text_payload)
        pdf_path.write_bytes(pdf_bytes)

        res = self.kb.ingest_file(pdf_path, title="Compliance Policy PDF")
        self.assertTrue(res["success"])
        self.assertEqual(res["file_type"], "pdf")

        search_res = self.kb.search("FIPS 140-3 validation rule")
        self.assertGreater(len(search_res["results"]), 0)
        top = search_res["results"][0]
        self.assertIn("FIPS 140-3", top["content"])
        self.assertIn("Page", top["provenance"])

    # 10. PDF File with Embedded Images (.pdf)
    def test_rag_pdf_with_image(self):
        """Test RAG pipeline on a PDF with embedded visual images."""
        pdf_path = self.workspace / "visual_architecture.pdf"

        # Generate a synthetic image and write it as PDF via Pillow
        img = Image.new("RGB", (300, 200), color=(50, 120, 200))
        draw = ImageDraw.Draw(img)
        draw.text((30, 80), "Embedded Network Diagram", fill=(255, 255, 255))

        img.save(str(pdf_path), format="PDF", resolution=100.0)

        res = self.kb.ingest_file(pdf_path, title="Visual Architecture PDF")
        self.assertTrue(res["success"])
        self.assertEqual(res["file_type"], "pdf")

        # Verify that document was indexed and read_document includes image or page marker
        doc_md = self.kb.read_document(res["document_id"])
        self.assertIsNotNone(doc_md)
        self.assertIn("PAGE 1", doc_md)

    # 11. Simultaneous Ingestion of Heterogeneous Modalities in One KB
    def test_rag_multi_modal_cross_retrieval(self):
        """Test simultaneous ingestion of Word, Excel, PPTX, PDF, and Code into a single KnowledgeBase."""
        # 1. Word doc
        word_p = self.workspace / "doc_contract.docx"
        doc = docx.Document()
        doc.add_paragraph("Unique keyword: QUANTUM_ALGORITHM_PATENT_PENDING.")
        doc.save(str(word_p))

        # 2. Excel sheet
        excel_p = self.workspace / "doc_ledger.xlsx"
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Ledger"
        ws.append(["Transaction", "HashId"])
        ws.append(["GenesisBlock", "BLCK_999888777_HASH"])
        wb.save(str(excel_p))

        # 3. PowerPoint
        ppt_p = self.workspace / "doc_slides.pptx"
        prs = pptx.Presentation()
        s = prs.slides.add_slide(prs.slide_layouts[0])
        s.shapes.title.text = "Keynote: NEBULA_EXPANSION_INITIATIVE"
        prs.save(str(ppt_p))

        # 4. Text PDF
        pdf_p = self.workspace / "doc_manual.pdf"
        pdf_p.write_bytes(make_test_pdf_bytes("Security clearance code: OMEGA_PROTOCOL_LEVEL_FIVE."))

        # 5. Code
        code_p = self.workspace / "doc_script.py"
        code_p.write_text("API_ROUTER_SECRET_KEY = 'VAULT_SECRET_PASS_9988'", encoding="utf-8")

        # Ingest all 5 diverse formats
        self.kb.ingest_file(word_p, title="Patent Word Doc")
        self.kb.ingest_file(excel_p, title="Ledger Excel Sheet")
        self.kb.ingest_file(ppt_p, title="Keynote Deck")
        self.kb.ingest_file(pdf_p, title="Manual PDF")
        self.kb.ingest_file(code_p, title="Router Code")

        self.assertEqual(len(self.kb.list_documents()), 5)

        # Cross-retrieval query 1 -> Targets Word doc
        r1 = self.kb.search("QUANTUM_ALGORITHM_PATENT_PENDING")
        self.assertIn("QUANTUM_ALGORITHM", r1["results"][0]["content"])
        self.assertEqual(r1["results"][0]["document_title"], "Patent Word Doc")

        # Cross-retrieval query 2 -> Targets Excel sheet
        r2 = self.kb.search("BLCK_999888777_HASH")
        self.assertIn("BLCK_999888777_HASH", r2["results"][0]["content"])
        self.assertEqual(r2["results"][0]["document_title"], "Ledger Excel Sheet")

        # Cross-retrieval query 3 -> Targets PowerPoint
        r3 = self.kb.search("NEBULA_EXPANSION_INITIATIVE")
        self.assertIn("NEBULA_EXPANSION", r3["results"][0]["content"])
        self.assertEqual(r3["results"][0]["document_title"], "Keynote Deck")

        # Cross-retrieval query 4 -> Targets PDF
        r4 = self.kb.search("OMEGA_PROTOCOL_LEVEL_FIVE")
        self.assertIn("OMEGA_PROTOCOL", r4["results"][0]["content"])
        self.assertEqual(r4["results"][0]["document_title"], "Manual PDF")

        # Cross-retrieval query 5 -> Targets Python script
        r5 = self.kb.search("VAULT_SECRET_PASS_9988")
        self.assertIn("VAULT_SECRET_PASS", r5["results"][0]["content"])
        self.assertEqual(r5["results"][0]["document_title"], "Router Code")


if __name__ == "__main__":
    unittest.main()

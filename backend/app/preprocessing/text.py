"""Text and Markdown preprocessor adapter.

Conforms to Section 5 of ProjectDetails.md.
"""

from pathlib import Path
import uuid
from app.domain.document import Document, DocumentMetadata, DocumentType
from app.domain.provenance import PageRef, Provenance
from app.domain.section import Block, BlockType, Section
from app.preprocessing.base import BasePreprocessor
from app.utils.hashing import compute_sha256_file


class TextPreprocessor(BasePreprocessor):
    """Processes Plaintext and Markdown documents into canonical representation."""

    def process(self, file_path: str | Path, document_id: str) -> Document:
        path = Path(file_path)
        content_text = path.read_text(encoding="utf-8", errors="replace")
        source_hash = compute_sha256_file(path)
        file_size = path.stat().st_size

        ext = path.suffix.lower()
        if ext == ".md":
            ft = DocumentType.MARKDOWN
        else:
            ft = DocumentType.TXT

        # Special extraction for HTML files
        if ext in (".html", ".htm"):
            import html, re
            # Remove scripts and styles
            no_scripts = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", content_text, flags=re.DOTALL | re.IGNORECASE)
            # Format headings, paragraphs, and list items into clean markdown
            clean = re.sub(r"<h([1-6])[^>]*>(.*?)</h\1>", r"\n\n# \2\n\n", no_scripts, flags=re.IGNORECASE)
            clean = re.sub(r"<p[^>]*>(.*?)</p>", r"\n\n\1\n\n", clean, flags=re.IGNORECASE)
            clean = re.sub(r"<li[^>]*>(.*?)</li>", r"\n* \1", clean, flags=re.IGNORECASE)
            clean = re.sub(r"<br\s*/?>", "\n", clean, flags=re.IGNORECASE)
            clean = re.sub(r"<[^>]+>", " ", clean)
            content_text = html.unescape(re.sub(r"\n\s*\n", "\n\n", clean)).strip()

        metadata = DocumentMetadata(
            title=path.stem,
            source_path=str(path),
            file_type=ft,
            file_size_bytes=file_size,
            source_hash=source_hash,
            page_count=1,
        )

        doc_prov = Provenance(
            file_id=document_id,
            document_id=document_id,
            file_name=path.name,
            file_type=path.suffix.lstrip(".").lower() or "txt",
        )

        is_code = ext in (".py", ".js", ".ts", ".json", ".sql", ".sh", ".yaml", ".yml", ".css")

        # Split content by double newlines or headers into meaningful blocks
        raw_paragraphs = [p.strip() for p in content_text.split("\n\n") if p.strip()]
        if not raw_paragraphs:
            raw_paragraphs = [content_text.strip() or f"Content of {path.name}"]

        blocks = []
        for p in raw_paragraphs:
            if is_code:
                btype = BlockType.CODE
            elif p.startswith("#"):
                btype = BlockType.HEADING
            else:
                btype = BlockType.TEXT

            blocks.append(
                Block(
                    block_id=f"blk_{uuid.uuid4().hex[:8]}",
                    block_type=btype,
                    content=p,
                    provenance=doc_prov,
                )
            )

        section = Section(
            section_id=f"sec_{document_id}_main",
            title=path.stem,
            level=1,
            blocks=blocks,
            provenance=doc_prov,
        )

        return Document(
            document_id=document_id,
            metadata=metadata,
            sections=[section],
            normalized_markdown=content_text,
            provenance=doc_prov,
        )

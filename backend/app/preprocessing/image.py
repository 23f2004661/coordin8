"""Image preprocessor adapter.

Conforms to Section 5.5 of ProjectDetails.md:
Classifies images and generates content and retrieval descriptions alongside OCR.
"""

from pathlib import Path
import uuid
from app.core.logging import logger
from app.domain.asset import Asset, AssetDescription, AssetType
from app.domain.document import Document, DocumentMetadata, DocumentType
from app.domain.provenance import Provenance
from app.domain.section import Block, BlockType, Section
from app.ocr import get_ocr_provider
from app.preprocessing.base import BasePreprocessor
from app.utils.hashing import compute_sha256_file


class ImagePreprocessor(BasePreprocessor):
    """Processes images, creating visual asset descriptions, OCR text, and canonical documents."""

    def __init__(self, ocr_provider=None) -> None:
        self.ocr_provider = ocr_provider or get_ocr_provider()

    def process(self, file_path: str | Path, document_id: str) -> Document:
        path = Path(file_path)
        source_hash = compute_sha256_file(path)
        file_size = path.stat().st_size

        metadata = DocumentMetadata(
            title=path.stem,
            source_path=str(path),
            file_type=DocumentType.IMAGE,
            file_size_bytes=file_size,
            source_hash=source_hash,
        )

        doc_prov = Provenance(
            file_id=document_id,
            document_id=document_id,
            file_name=path.name,
            file_type="image",
        )

        ocr_text = ""
        if self.ocr_provider:
            try:
                logger.info("ImagePreprocessor: invoking OCR provider for image %s", path.name)
                ocr_result = self.ocr_provider.parse_image(path)
                if ocr_result and ocr_result.text_markdown:
                    ocr_text = ocr_result.text_markdown.strip()
                    logger.info("ImagePreprocessor: extracted %d characters from %s", len(ocr_text), path.name)
            except Exception as exc:
                logger.warning("ImagePreprocessor: OCR failed for %s: %s", path.name, exc)

        caption = f"Image {path.name}"
        visual_desc = (
            f"Image showing: {ocr_text}"
            if ocr_text
            else f"Visual asset loaded from {path.name}"
        )
        retrieval_desc = (
            f"Extracted image text and content for {path.stem}:\n{ocr_text}"
            if ocr_text
            else f"Visual content representation for {path.stem}"
        )

        asset_id = f"ast_{uuid.uuid4().hex[:8]}"
        asset = Asset(
            asset_id=asset_id,
            document_id=document_id,
            asset_type=AssetType.EMBEDDED_IMAGE,
            file_path=str(path),
            description=AssetDescription(
                caption=caption,
                visual_description=visual_desc,
                retrieval_description=retrieval_desc,
            ),
            provenance=doc_prov,
        )

        section = Section(
            section_id=f"sec_{document_id}_image",
            title=path.stem,
            level=1,
            provenance=doc_prov,
        )

        img_block = Block(
            block_id=f"blk_{uuid.uuid4().hex[:8]}",
            block_type=BlockType.IMAGE,
            content=f"![{caption}]({path.name})",
            asset_id=asset_id,
            provenance=doc_prov,
        )
        section.blocks.append(img_block)

        if ocr_text:
            text_block = Block(
                block_id=f"blk_{uuid.uuid4().hex[:8]}",
                block_type=BlockType.TEXT,
                content=ocr_text,
                provenance=doc_prov,
            )
            section.blocks.append(text_block)

        normalized_md = (
            f"# Image: {path.stem}\n\n{img_block.content}\n\n{ocr_text if ocr_text else visual_desc}\n"
        )

        return Document(
            document_id=document_id,
            metadata=metadata,
            sections=[section],
            assets=[asset],
            normalized_markdown=normalized_md,
            provenance=doc_prov,
        )

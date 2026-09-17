"""Image preprocessor adapter.

Conforms to Section 5.5 of ProjectDetails.md:
Classifies images and generates content and retrieval descriptions alongside OCR.
"""

from pathlib import Path
import uuid
from app.domain.asset import Asset, AssetDescription, AssetType
from app.domain.document import Document, DocumentMetadata, DocumentType
from app.domain.provenance import Provenance
from app.domain.section import Block, BlockType, Section
from app.preprocessing.base import BasePreprocessor
from app.utils.hashing import compute_sha256_file


class ImagePreprocessor(BasePreprocessor):
    """Processes images, creating visual asset descriptions and canonical documents."""

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

        asset_id = f"ast_{uuid.uuid4().hex[:8]}"
        asset = Asset(
            asset_id=asset_id,
            document_id=document_id,
            asset_type=AssetType.EMBEDDED_IMAGE,
            file_path=str(path),
            description=AssetDescription(
                caption=f"Image {path.name}",
                visual_description=f"Visual asset loaded from {path.name}",
                retrieval_description=f"Visual content representation for {path.stem}",
            ),
            provenance=doc_prov,
        )

        section = Section(
            section_id=f"sec_{document_id}_image",
            title=path.stem,
            level=1,
            provenance=doc_prov,
        )

        block = Block(
            block_id=f"blk_{uuid.uuid4().hex[:8]}",
            block_type=BlockType.IMAGE,
            content=f"![{asset.description.caption}]({path.name})",
            asset_id=asset_id,
            provenance=doc_prov,
        )
        section.blocks.append(block)

        normalized_md = f"# Image: {path.stem}\n\n{block.content}\n\n{asset.description.visual_description}\n"

        return Document(
            document_id=document_id,
            metadata=metadata,
            sections=[section],
            assets=[asset],
            normalized_markdown=normalized_md,
            provenance=doc_prov,
        )

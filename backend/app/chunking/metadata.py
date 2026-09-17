"""Chunk metadata builder conforming to Section 9.2 of ProjectDetails.md."""

from app.domain.chunk import ChunkMetadata
from app.domain.document import Document
from app.domain.section import Section
from app.utils.tokenization import estimate_token_count


class ChunkMetadataBuilder:
    """Constructs complete chunk metadata payloads with provenance and lineage."""

    @staticmethod
    def build(
        chunk_id: str,
        document: Document,
        section: Section | None,
        content: str,
        content_type: str = "text",
        summary: str | None = None,
        entities: list[str] | None = None,
        topics: list[str] | None = None,
    ) -> ChunkMetadata:
        page = None
        slide = None
        sheet = None
        source_range = None

        if section and section.provenance:
            if section.provenance.page:
                page = section.provenance.page.page_number
            if section.provenance.slide:
                slide = section.provenance.slide.slide_number
            if section.provenance.sheet:
                sheet = section.provenance.sheet.sheet_name
                source_range = section.provenance.sheet.cell_range

        return ChunkMetadata(
            chunk_id=chunk_id,
            document_id=document.document_id,
            parent_id=section.section_id if section else None,
            document_type=document.metadata.file_type.value,
            section_id=section.section_id if section else None,
            content_type=content_type,
            page=page,
            slide=slide,
            sheet=sheet,
            source_range=source_range,
            token_count=estimate_token_count(content),
            summary=summary or (section.summary.summary if section and section.summary else None),
            entities=entities or [],
            topics=topics or (section.summary.topics if section and section.summary else []),
            asset_ids=[],
            pipeline_version="v1.0",
        )

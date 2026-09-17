"""Document and section summary generators for retrieval discovery.

Conforms to Section 8 of ProjectDetails.md:
Summaries are retrieval aids answering what, topics, entities, and questions answered.
"""

from app.domain.document import Document, DocumentSummary
from app.domain.section import Section, SectionSummary


class SummaryGenerator:
    """Generates retrieval-oriented summaries for documents and sections."""

    def generate_document_summary(self, document: Document) -> DocumentSummary:
        """Create a retrieval-oriented document summary (Section 8)."""
        title = document.metadata.title
        file_type = document.metadata.file_type.value
        section_titles = [s.title for s in document.sections[:5]]

        summary_text = (
            f"This {file_type.upper()} document '{title}' covers {len(document.sections)} major sections: "
            f"{', '.join(section_titles) if section_titles else 'general content'}. "
            f"It provides operational details, background information, and source evidence."
        )

        return DocumentSummary(
            summary=summary_text,
            main_topics=[title] + [s.title for s in document.sections[:3]],
            key_entities=[title],
            questions_answered=[
                f"What is discussed in {title}?",
                f"What are the main findings of {title}?",
            ],
            decisions_and_findings=[],
        )

    def generate_section_summary(self, section: Section) -> SectionSummary:
        """Create a concise section summary for hierarchical coarse-to-fine filtering."""
        block_count = len(section.blocks)
        summary_text = f"Section '{section.title}' contains {block_count} structural block(s) detailing specific points."
        return SectionSummary(
            summary=summary_text,
            topics=[section.title],
            entities=[],
            key_findings=[],
        )

"""Provenance validation and citation helpers."""

from app.domain.provenance import Provenance


def validate_provenance_lineage(provenance: Provenance) -> bool:
    """Verify that a provenance record contains valid references."""
    if not provenance.file_id or not provenance.document_id or not provenance.file_name:
        return False
    return True


def format_markdown_citation(provenance: Provenance) -> str:
    """Format a provenance record into a markdown citation footnote or tag."""
    citation = provenance.to_citation_string()
    return f"`[{citation}]`"

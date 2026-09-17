"""Structured output extraction models for LLM responses."""

from dataclasses import dataclass, field


@dataclass
class GroundedAnswer:
    """Standardized response structure for a RAG question."""
    query: str
    answer_text: str
    citations: list[str] = field(default_factory=list)
    confidence: float = 1.0
    evidence_count: int = 0
    model_name: str = ""

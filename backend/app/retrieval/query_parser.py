"""Stage 1: Query intent and modality analyzer conforming to Section 11 of ProjectDetails.md."""

from dataclasses import dataclass, field
import re
from typing import Any


@dataclass
class ParsedQuery:
    """Structured query analysis output."""
    raw_query: str
    intent: str = "find_information"
    modalities: list[str] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    requires_exact_calculation: bool = False
    filters: dict[str, Any] = field(default_factory=dict)


class QueryParser:
    """Analyzes incoming user query for intent, modal focus, and calculation requirements."""

    CALCULATION_KEYWORDS = {
        "average", "mean", "sum", "total", "calculate", "median",
        "standard deviation", "difference", "growth rate", "percentage",
    }

    MODALITY_HINTS = {
        "slide": "pptx",
        "presentation": "pptx",
        "sheet": "xlsx",
        "spreadsheet": "xlsx",
        "excel": "xlsx",
        "table": "xlsx",
        "meeting": "transcript",
        "transcript": "transcript",
        "spoke": "transcript",
        "diagram": "image",
        "chart": "image",
        "figure": "image",
        "photo": "image",
        "document": "pdf",
        "pdf": "pdf",
        "report": "pdf",
    }

    def parse(self, query: str) -> ParsedQuery:
        q_lower = query.lower()
        requires_calc = any(kw in q_lower for kw in self.CALCULATION_KEYWORDS)

        modalities = []
        for word, mod in self.MODALITY_HINTS.items():
            if word in q_lower and mod not in modalities:
                modalities.append(mod)

        # Simple capitalized entities extraction
        capitalized = re.findall(r"\b[A-Z][a-z0-9]+\b", query)
        entities = [w for w in capitalized if w.lower() not in {"what", "who", "when", "where", "how", "which"}]

        keywords = [w for w in re.findall(r"\w+", q_lower) if len(w) > 3]

        return ParsedQuery(
            raw_query=query,
            intent="calculate" if requires_calc else "find_information",
            modalities=modalities,
            entities=entities,
            keywords=keywords,
            requires_exact_calculation=requires_calc,
        )

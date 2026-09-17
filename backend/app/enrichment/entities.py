"""Entity extraction enrichment."""

import re


class EntityExtractor:
    """Extracts named entities, system names, and acronyms from text content."""

    def extract_entities(self, text: str) -> list[str]:
        if not text:
            return []
        # Basic heuristic extractor for capitalized multi-word phrases and acronyms
        acronyms = set(re.findall(r"\b[A-Z]{2,}\b", text))
        capitalized = set(re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", text))
        candidates = list(acronyms.union(capitalized))
        # Filter common words
        stop = {"The", "This", "That", "What", "When", "Where", "Which", "Page", "Section", "Slide"}
        return [c for c in candidates if c not in stop][:20]

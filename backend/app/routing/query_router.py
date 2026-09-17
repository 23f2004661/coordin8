"""Query routing engine conforming to Section 13 and Section 27 (Milestone 8)."""

from enum import Enum
from app.retrieval.query_parser import ParsedQuery


class RouteTarget(str, Enum):
    SEMANTIC_RAG = "semantic_rag"
    SPREADSHEET_CALCULATION = "spreadsheet_calculation"
    HYBRID_ANALYSIS = "hybrid_analysis"


class QueryRouter:
    """Routes query between semantic retrieval and safe exact spreadsheet calculations."""

    def determine_route(self, parsed_query: ParsedQuery) -> RouteTarget:
        if parsed_query.requires_exact_calculation and "xlsx" in parsed_query.modalities:
            return RouteTarget.SPREADSHEET_CALCULATION
        if parsed_query.requires_exact_calculation:
            return RouteTarget.HYBRID_ANALYSIS
        return RouteTarget.SEMANTIC_RAG

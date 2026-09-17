"""Safe dataframe operation definitions conforming to Section 13."""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class OperationType(str, Enum):
    MEAN = "mean"
    SUM = "sum"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    FILTER = "filter"


@dataclass
class SpreadsheetOperation:
    """Safe analytical query against a specific sheet."""
    workbook_id: str
    sheet_name: str
    operation: OperationType
    target_column: str
    filter_column: str | None = None
    filter_value: Any = None
    date_start: str | None = None
    date_end: str | None = None

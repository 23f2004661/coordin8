"""Spreadsheet schema and structure inspector conforming to Section 13."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class SheetSchema:
    sheet_name: str
    column_names: list[str]
    total_rows: int
    data_types: dict[str, str] = field(default_factory=dict)
    sample_values: dict[str, list[Any]] = field(default_factory=dict)


class SpreadsheetInspector:
    """Inspects Excel workbook structure without loading all rows into RAM."""

    def inspect_workbook(self, file_path: str | Path) -> list[SheetSchema]:
        """Inspect sheet names, columns, and dimensions."""
        # Baseline stub implementation returning schema
        return [
            SheetSchema(
                sheet_name="Sales",
                column_names=["Date", "Region", "Product", "Units", "Revenue", "GrossMargin"],
                total_rows=5000,
                data_types={"Revenue": "float", "Region": "string", "Date": "datetime"},
            )
        ]

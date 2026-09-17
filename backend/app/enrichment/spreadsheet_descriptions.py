"""Spreadsheet schema and sheet description generator conforming to Section 5.4."""

from typing import Any


class SpreadsheetDescriptionGenerator:
    """Generates semantic sheet and schema summaries for structured workbooks."""

    def describe_sheet(
        self,
        sheet_name: str,
        columns: list[str],
        row_count: int,
        date_ranges: str | None = None,
    ) -> str:
        """Generate a semantic summary for an Excel sheet."""
        col_list = ", ".join(columns[:10]) + ("..." if len(columns) > 10 else "")
        desc = (
            f"Sheet '{sheet_name}' contains {row_count} rows across columns: [{col_list}]."
        )
        if date_ranges:
            desc += f" Applicable time period covers: {date_ranges}."
        return desc

"""Spreadsheet analysis endpoints conforming to Section 13 & 17 of ProjectDetails.md."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.spreadsheets.executor import SpreadsheetExecutor
from app.spreadsheets.operations import OperationType, SpreadsheetOperation

router = APIRouter(prefix="/spreadsheets", tags=["spreadsheets"])
executor = SpreadsheetExecutor()


class AnalyzeSpreadsheetRequest(BaseModel):
    sheet_name: str
    operation: OperationType
    target_column: str
    filter_column: str | None = None
    filter_value: str | float | int | None = None


@router.post("/{document_id}/analyze")
def analyze_spreadsheet(document_id: str, request: AnalyzeSpreadsheetRequest):
    """Execute exact calculation on a spreadsheet table with provenance."""
    op = SpreadsheetOperation(
        workbook_id=document_id,
        sheet_name=request.sheet_name,
        operation=request.operation,
        target_column=request.target_column,
        filter_column=request.filter_column,
        filter_value=request.filter_value,
    )
    res = executor.execute(op)
    return {
        "document_id": document_id,
        "sheet_name": request.sheet_name,
        "operation": request.operation.value,
        "target_column": request.target_column,
        "result_value": res.value,
        "citation": res.provenance_citation,
        "rows_computed": res.row_count,
    }

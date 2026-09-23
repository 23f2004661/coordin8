"""API routes aggregator for Coordin8."""

from fastapi import APIRouter
from app.api.agents import router as agents_router
from app.api.answers import router as answers_router
from app.api.documents import router as documents_router
from app.api.jobs import router as jobs_router
from app.api.search import router as search_router
from app.api.spreadsheets import router as spreadsheets_router

api_router = APIRouter(prefix="/api")

api_router.include_router(agents_router)
api_router.include_router(documents_router)
api_router.include_router(jobs_router)
api_router.include_router(search_router)
api_router.include_router(answers_router)
api_router.include_router(spreadsheets_router)

__all__ = ["api_router"]


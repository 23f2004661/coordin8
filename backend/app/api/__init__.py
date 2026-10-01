"""API routes aggregator for Coordin8."""

from fastapi import APIRouter, Depends
from app.api.auth import router as auth_router
from app.api.answers import router as answers_router
from app.api.documents import router as documents_router
from app.api.jobs import router as jobs_router
from app.api.search import router as search_router
from app.api.spreadsheets import router as spreadsheets_router
from app.api.projects import router as projects_router
from app.api.tasks import router as tasks_router
from app.api.employees import router as employees_router
from app.api.meetings import router as meetings_router
from app.api.reporting import router as reporting_router
from app.core.auth import deny_unscoped_knowledge_access

api_router = APIRouter(prefix="/api")

api_router.include_router(auth_router)
api_router.include_router(projects_router)
api_router.include_router(tasks_router)
api_router.include_router(employees_router)
api_router.include_router(meetings_router)
api_router.include_router(reporting_router)
# Legacy global operations have no project context, so retrieval is denied for every role.
unscoped_access = [Depends(deny_unscoped_knowledge_access)]
api_router.include_router(search_router, dependencies=unscoped_access)
api_router.include_router(answers_router, dependencies=unscoped_access)
api_router.include_router(documents_router, dependencies=unscoped_access)
api_router.include_router(jobs_router, dependencies=unscoped_access)
api_router.include_router(spreadsheets_router, dependencies=unscoped_access)

__all__ = ["api_router"]

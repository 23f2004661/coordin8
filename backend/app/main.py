"""Main FastAPI application for Coordin8."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import api_router
from app.core.config import get_settings
from app.core.logging import logger
from app.db.session import init_db
from app.indexing.qdrant import QdrantManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown hooks."""
    settings = get_settings()
    logger.info("Initializing Coordin8 Backend in %s mode...", settings.app_env)
    # Initialize SQL database tables
    try:
        init_db()
        logger.info("SQL database schema initialized.")
    except Exception as exc:
        logger.warning("Database initialization deferred: %s", exc)

    # Initialize Qdrant vector collections
    try:
        qdrant = QdrantManager()
        qdrant.ensure_collections()
    except Exception as exc:
        logger.warning("Qdrant collection check deferred: %s", exc)

    yield

    logger.info("Shutting down Coordin8 Backend.")


def create_app() -> FastAPI:
    """Application factory."""
    settings = get_settings()
    application = FastAPI(
        title="Coordin8 Knowledge API",
        description="Multimodal Hierarchical RAG Knowledge System",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS configuration
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    application.include_router(api_router)

    @application.get("/health", tags=["system"])
    @application.get("/api/health", tags=["system"])
    def health_check():
        return {"status": "ok", "service": "coordin8-backend", "version": "0.1.0"}

    @application.get("/", tags=["system"])
    def root():
        return {
            "name": "Coordin8 Knowledge API",
            "docs_url": "/docs",
            "api_prefix": "/api",
        }

    return application


app = create_app()

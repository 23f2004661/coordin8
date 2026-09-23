"""Database session and connection management for Coordin8."""

from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.core.config import get_settings

settings = get_settings()

# Support SQLite or PostgreSQL
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    echo=settings.app_env == "development",
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def create_db_engine(db_url: str | None = None, echo: bool | None = None):
    """Create a new SQLAlchemy engine for the specified database URL."""
    url = db_url or settings.database_url
    is_sqlite = url.startswith("sqlite")
    c_args = {"check_same_thread": False} if is_sqlite else {}
    is_echo = echo if echo is not None else (settings.app_env == "development")
    return create_engine(url, connect_args=c_args, echo=is_echo)


def create_session_factory(bind_engine=None):
    """Create a new sessionmaker bound to the given engine."""
    target = bind_engine or engine
    return sessionmaker(autocommit=False, autoflush=False, bind=target)


def get_db() -> Generator[Session, None, None]:
    """Dependency for obtaining a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(bind_engine=None) -> None:
    """Initialize tables if they do not already exist."""
    target = bind_engine or engine
    Base.metadata.create_all(bind=target)

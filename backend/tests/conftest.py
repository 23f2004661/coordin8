"""Test configuration and shared fixtures for Coordin8."""

import pytest
from app.db.session import Base, engine


@pytest.fixture(autouse=True)
def setup_test_database():
    """Ensure clean test tables."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

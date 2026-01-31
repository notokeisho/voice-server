"""Tests for database connection."""

import pytest
from sqlalchemy import text


@pytest.mark.asyncio
async def test_db_connection():
    """Test that the database connection works."""
    from app.database import get_session

    async with get_session() as session:
        result = await session.execute(text("SELECT 1"))
        assert result.scalar() == 1


@pytest.mark.asyncio
async def test_db_engine_exists():
    """Test that the async engine is properly configured."""
    from app.database import engine

    assert engine is not None
    assert "asyncpg" in str(engine.url.drivername)

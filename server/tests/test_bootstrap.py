"""Tests for bootstrap module."""

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings


@pytest.fixture
async def db_session():
    """Create a fresh database session for each test."""
    engine = create_async_engine(settings.database_url)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session
        await session.rollback()

    await engine.dispose()


@pytest.fixture
async def empty_whitelist(db_session: AsyncSession):
    """Ensure whitelist is empty for the test."""
    await db_session.execute(text("DELETE FROM whitelist"))
    await db_session.commit()
    yield db_session
    # Clean up after test
    await db_session.execute(text("DELETE FROM whitelist WHERE github_id = '12345678'"))
    await db_session.commit()


@pytest.mark.asyncio
async def test_ensure_initial_admin_adds_admin_when_whitelist_empty(
    empty_whitelist: AsyncSession, monkeypatch
):
    """Test that initial admin is added when whitelist is empty."""
    # Set environment variables
    monkeypatch.setattr("app.bootstrap.settings.initial_admin_github_id", "12345678")
    monkeypatch.setattr("app.bootstrap.settings.initial_admin_github_username", "testadmin")

    from app.bootstrap import ensure_initial_admin

    await ensure_initial_admin()

    # Verify admin was added
    result = await empty_whitelist.execute(
        text("SELECT github_id, github_username FROM whitelist WHERE github_id = '12345678'")
    )
    row = result.fetchone()
    assert row is not None
    assert row[0] == "12345678"
    assert row[1] == "testadmin"


@pytest.mark.asyncio
async def test_ensure_initial_admin_does_nothing_when_whitelist_not_empty(
    db_session: AsyncSession, monkeypatch
):
    """Test that nothing is added when whitelist already has data."""
    from app.models.whitelist import Whitelist

    # Clean up and add existing entry
    await db_session.execute(text("DELETE FROM whitelist WHERE github_id IN ('existing', '12345678')"))
    await db_session.commit()

    existing = Whitelist(github_id="existing", github_username="existinguser")
    db_session.add(existing)
    await db_session.commit()

    # Set environment variables
    monkeypatch.setattr("app.bootstrap.settings.initial_admin_github_id", "12345678")
    monkeypatch.setattr("app.bootstrap.settings.initial_admin_github_username", "testadmin")

    from app.bootstrap import ensure_initial_admin

    await ensure_initial_admin()

    # Verify new admin was NOT added
    result = await db_session.execute(
        text("SELECT github_id FROM whitelist WHERE github_id = '12345678'")
    )
    row = result.fetchone()
    assert row is None

    # Clean up
    await db_session.execute(text("DELETE FROM whitelist WHERE github_id = 'existing'"))
    await db_session.commit()


@pytest.mark.asyncio
async def test_ensure_initial_admin_does_nothing_when_env_not_set(
    empty_whitelist: AsyncSession, monkeypatch
):
    """Test that nothing happens when environment variables are not set."""
    # Ensure environment variables are None
    monkeypatch.setattr("app.bootstrap.settings.initial_admin_github_id", None)
    monkeypatch.setattr("app.bootstrap.settings.initial_admin_github_username", None)

    from app.bootstrap import ensure_initial_admin

    await ensure_initial_admin()

    # Verify nothing was added
    result = await empty_whitelist.execute(text("SELECT COUNT(*) FROM whitelist"))
    count = result.scalar()
    assert count == 0

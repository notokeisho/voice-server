"""Tests for Dictionary models and functions."""

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
async def test_user(db_session: AsyncSession):
    """Create a test user for dictionary tests."""
    from app.models.user import User

    # Clean up first (delete dictionary entries, then user)
    await db_session.execute(
        text(
            "DELETE FROM user_dictionary WHERE user_id IN "
            "(SELECT id FROM users WHERE github_id = 'dict_test_user')"
        )
    )
    await db_session.execute(text("DELETE FROM users WHERE github_id = 'dict_test_user'"))
    await db_session.commit()

    user = User(github_id="dict_test_user")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    yield user

    # Clean up after (delete dictionary entries, then user)
    await db_session.execute(
        text("DELETE FROM user_dictionary WHERE user_id = :user_id"),
        {"user_id": user.id},
    )
    await db_session.execute(text("DELETE FROM users WHERE github_id = 'dict_test_user'"))
    await db_session.commit()


# Global Dictionary Tests


@pytest.mark.asyncio
async def test_create_global_dictionary_entry(db_session: AsyncSession):
    """Test that a global dictionary entry can be created."""
    from app.models.global_dictionary import GlobalDictionary

    entry = GlobalDictionary(pattern="くろーど", replacement="Claude")
    db_session.add(entry)
    await db_session.flush()

    assert entry.id is not None
    assert entry.pattern == "くろーど"
    assert entry.replacement == "Claude"


@pytest.mark.asyncio
async def test_add_global_entry(db_session: AsyncSession):
    """Test the add_global_entry function."""
    from app.models.global_dictionary import add_global_entry, get_global_entries

    await db_session.execute(text("DELETE FROM global_dictionary WHERE pattern = 'テスト'"))
    await db_session.commit()

    await add_global_entry(db_session, "テスト", "TEST")

    entries = await get_global_entries(db_session)
    assert any(e.pattern == "テスト" and e.replacement == "TEST" for e in entries)

    await db_session.execute(text("DELETE FROM global_dictionary WHERE pattern = 'テスト'"))
    await db_session.commit()


# User Dictionary Tests


@pytest.mark.asyncio
async def test_create_user_dictionary_entry(db_session: AsyncSession, test_user):
    """Test that a user dictionary entry can be created."""
    from app.models.user_dictionary import UserDictionary

    entry = UserDictionary(user_id=test_user.id, pattern="いしだけん", replacement="石田研")
    db_session.add(entry)
    await db_session.flush()

    assert entry.id is not None
    assert entry.user_id == test_user.id
    assert entry.pattern == "いしだけん"
    assert entry.replacement == "石田研"


@pytest.mark.asyncio
async def test_add_user_entry(db_session: AsyncSession, test_user):
    """Test the add_user_entry function."""
    from app.models.user_dictionary import add_user_entry, get_user_entries

    await db_session.execute(
        text("DELETE FROM user_dictionary WHERE user_id = :user_id"),
        {"user_id": test_user.id},
    )
    await db_session.commit()

    await add_user_entry(db_session, test_user.id, "マイパターン", "MY_PATTERN")

    entries = await get_user_entries(db_session, test_user.id)
    assert len(entries) == 1
    assert entries[0].pattern == "マイパターン"
    assert entries[0].replacement == "MY_PATTERN"


@pytest.mark.asyncio
async def test_user_dictionary_limit(db_session: AsyncSession, test_user):
    """Test that user dictionary has a limit of 100 entries."""
    from app.models.user_dictionary import (
        USER_DICTIONARY_LIMIT,
        DictionaryLimitExceeded,
        add_user_entry,
    )

    await db_session.execute(
        text("DELETE FROM user_dictionary WHERE user_id = :user_id"),
        {"user_id": test_user.id},
    )
    await db_session.commit()

    # Add 100 entries
    for i in range(USER_DICTIONARY_LIMIT):
        await add_user_entry(db_session, test_user.id, f"pattern{i}", f"replacement{i}")

    # 101st entry should raise error
    with pytest.raises(DictionaryLimitExceeded):
        await add_user_entry(db_session, test_user.id, "pattern100", "replacement100")


@pytest.mark.asyncio
async def test_get_user_entry_count(db_session: AsyncSession, test_user):
    """Test getting the count of user dictionary entries."""
    from app.models.user_dictionary import add_user_entry, get_user_entry_count

    await db_session.execute(
        text("DELETE FROM user_dictionary WHERE user_id = :user_id"),
        {"user_id": test_user.id},
    )
    await db_session.commit()

    assert await get_user_entry_count(db_session, test_user.id) == 0

    await add_user_entry(db_session, test_user.id, "p1", "r1")
    await add_user_entry(db_session, test_user.id, "p2", "r2")

    assert await get_user_entry_count(db_session, test_user.id) == 2

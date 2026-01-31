"""Global Dictionary model and helper functions."""

from datetime import datetime

from sqlalchemy import ForeignKey, String, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class GlobalDictionary(Base):
    """Global dictionary for text replacement applied to all users."""

    __tablename__ = "global_dictionary"

    id: Mapped[int] = mapped_column(primary_key=True)
    pattern: Mapped[str] = mapped_column(String(255), index=True)
    replacement: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    def __repr__(self) -> str:
        return f"<GlobalDictionary(id={self.id}, pattern={self.pattern})>"


async def get_global_entries(session: AsyncSession) -> list[GlobalDictionary]:
    """Get all global dictionary entries.

    Args:
        session: Database session

    Returns:
        List of all global dictionary entries
    """
    result = await session.execute(select(GlobalDictionary))
    return list(result.scalars().all())


async def add_global_entry(
    session: AsyncSession,
    pattern: str,
    replacement: str,
    created_by: int | None = None,
) -> GlobalDictionary:
    """Add a global dictionary entry.

    Args:
        session: Database session
        pattern: Pattern to match
        replacement: Replacement text
        created_by: User ID of the admin who added this entry

    Returns:
        The created GlobalDictionary entry
    """
    entry = GlobalDictionary(pattern=pattern, replacement=replacement, created_by=created_by)
    session.add(entry)
    await session.commit()
    return entry


async def delete_global_entry(session: AsyncSession, entry_id: int) -> bool:
    """Delete a global dictionary entry.

    Args:
        session: Database session
        entry_id: ID of the entry to delete

    Returns:
        True if entry was deleted, False if entry was not found
    """
    result = await session.execute(select(GlobalDictionary).where(GlobalDictionary.id == entry_id))
    entry = result.scalar_one_or_none()
    if entry:
        await session.delete(entry)
        await session.commit()
        return True
    return False

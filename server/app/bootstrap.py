"""Bootstrap module for initial setup tasks."""

import logging

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.config import settings
from app.database import async_session_factory
from app.models.whitelist import Whitelist

logger = logging.getLogger(__name__)


async def ensure_initial_admin() -> None:
    """Ensure initial admin exists in whitelist if configured.

    This function checks if the INITIAL_ADMIN_GITHUB_ID environment variable
    is set. If set and the whitelist is empty, it adds the initial admin
    to the whitelist. This is useful for first-time setup.

    The function is idempotent and safe to call multiple times:
    - If env var is not set: does nothing
    - If whitelist is not empty: does nothing (protects existing data)
    - If already added: handles IntegrityError gracefully
    """
    if not settings.initial_admin_github_id:
        return

    async with async_session_factory() as session:
        # Check if whitelist is empty
        result = await session.execute(select(func.count()).select_from(Whitelist))
        count = result.scalar()

        if count == 0:
            entry = Whitelist(
                github_id=settings.initial_admin_github_id,
                github_username=settings.initial_admin_github_username,
            )
            try:
                session.add(entry)
                await session.commit()
                logger.info(
                    f"Initial admin added to whitelist: {settings.initial_admin_github_username}"
                )
            except IntegrityError:
                await session.rollback()
                logger.debug("Initial admin already exists, skipping")

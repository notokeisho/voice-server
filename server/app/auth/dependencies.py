"""Authentication dependencies for FastAPI."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select

from app.auth.jwt import verify_jwt_token
from app.database import async_session_factory
from app.models.user import User
from app.models.whitelist import is_whitelisted

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> User:
    """Get current authenticated user from JWT token.

    This dependency:
    1. Validates the JWT token
    2. Checks if user is in whitelist (every request)
    3. Returns the User object

    Args:
        credentials: HTTP Bearer credentials from Authorization header

    Returns:
        The authenticated User object

    Raises:
        HTTPException: 401 if token is missing or invalid
        HTTPException: 403 if user is not in whitelist
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = verify_jwt_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("user_id")
    github_id = payload.get("github_id")

    if not user_id or not github_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check whitelist on every request (for immediate revocation)
    async with async_session_factory() as session:
        if not await is_whitelisted(session, github_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not in whitelist",
            )

        # Get user from database
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current user and verify they are an admin.

    Args:
        current_user: The authenticated user from get_current_user

    Returns:
        The authenticated admin User object

    Raises:
        HTTPException: 403 if user is not an admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user

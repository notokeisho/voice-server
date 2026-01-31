"""JWT token creation and verification."""

from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

from app.config import settings


def create_jwt_token(user_id: int, github_id: str) -> str:
    """Create a JWT token for a user.

    Args:
        user_id: The user's database ID
        github_id: The user's GitHub ID

    Returns:
        The encoded JWT token string
    """
    expire = datetime.now(UTC) + timedelta(days=settings.jwt_expire_days)
    payload = {
        "user_id": user_id,
        "github_id": github_id,
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def verify_jwt_token(token: str) -> dict | None:
    """Verify a JWT token and return its payload.

    Args:
        token: The JWT token string to verify

    Returns:
        The decoded payload if valid, None if invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError:
        return None

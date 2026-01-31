"""Protected API endpoints for testing authentication."""

from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_admin_user, get_current_user
from app.models.user import User

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/protected")
async def protected_endpoint(current_user: User = Depends(get_current_user)):
    """Protected endpoint that requires authentication and whitelist.

    Args:
        current_user: The authenticated user from JWT token

    Returns:
        User information
    """
    return {
        "user_id": current_user.id,
        "github_id": current_user.github_id,
        "is_admin": current_user.is_admin,
    }


@router.get("/admin")
async def admin_endpoint(current_user: User = Depends(get_current_admin_user)):
    """Admin-only endpoint.

    Args:
        current_user: The authenticated admin user

    Returns:
        Admin status confirmation
    """
    return {
        "message": "Admin access granted",
        "user_id": current_user.id,
        "github_id": current_user.github_id,
    }

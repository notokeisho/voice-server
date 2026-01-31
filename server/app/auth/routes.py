"""Authentication routes for GitHub OAuth."""

from fastapi import APIRouter, HTTPException, Request, status

from app.auth.oauth import oauth

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login")
async def login(request: Request):
    """Redirect to GitHub OAuth login page.

    Returns:
        RedirectResponse to GitHub OAuth authorization URL
    """
    redirect_uri = str(request.url_for("callback"))
    github = oauth.create_client("github")
    return await github.authorize_redirect(request, redirect_uri)


@router.get("/callback")
async def callback(request: Request):
    """Handle GitHub OAuth callback.

    Args:
        request: The incoming request with OAuth code

    Returns:
        JSON response with JWT token on success

    Raises:
        HTTPException: If OAuth flow fails
    """
    # Check for error from GitHub
    error = request.query_params.get("error")
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth error: {error}",
        )

    # Check for authorization code
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing authorization code",
        )

    # Exchange code for access token and get user info
    github = oauth.create_client("github")
    try:
        token = await github.authorize_access_token(request)
        resp = await github.get("user", token=token)
        user_info = resp.json()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to authenticate with GitHub: {e}",
        ) from e

    # Import here to avoid circular imports
    from sqlalchemy import select

    from app.auth.jwt import create_jwt_token
    from app.database import async_session_factory
    from app.models.user import User
    from app.models.whitelist import is_whitelisted

    github_id = str(user_info.get("id"))
    github_avatar = user_info.get("avatar_url")

    # Check whitelist
    async with async_session_factory() as session:
        if not await is_whitelisted(session, github_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not in whitelist",
            )

        # Get or create user
        result = await session.execute(
            select(User).where(User.github_id == github_id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            user = User(github_id=github_id, github_avatar=github_avatar)
            session.add(user)
            await session.commit()
            await session.refresh(user)
        else:
            # Update avatar if changed
            if user.github_avatar != github_avatar:
                user.github_avatar = github_avatar
                await session.commit()

        # Create JWT token
        jwt_token = create_jwt_token(user_id=user.id, github_id=github_id)

    return {"access_token": jwt_token, "token_type": "bearer"}

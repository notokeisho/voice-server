"""Tests for authentication dependencies (middleware)."""

import asyncio

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.auth.jwt import create_jwt_token
from app.config import settings
from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


def run_async(coro):
    """Run async coroutine in a new event loop."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _setup_test_user(github_id: str, is_admin: bool = False) -> int:
    """Create a test user and return their ID."""
    from app.models.user import User

    engine = create_async_engine(settings.database_url)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Clean up first
        await session.execute(
            text(
                f"DELETE FROM user_dictionary WHERE user_id IN "
                f"(SELECT id FROM users WHERE github_id = '{github_id}')"
            )
        )
        await session.execute(text(f"DELETE FROM whitelist WHERE github_id = '{github_id}'"))
        await session.execute(text(f"DELETE FROM users WHERE github_id = '{github_id}'"))
        await session.commit()

        user = User(github_id=github_id, is_admin=is_admin)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        user_id = user.id

    await engine.dispose()
    return user_id


async def _cleanup_test_user(github_id: str):
    """Clean up test user."""
    engine = create_async_engine(settings.database_url)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        await session.execute(
            text(
                f"DELETE FROM user_dictionary WHERE user_id IN "
                f"(SELECT id FROM users WHERE github_id = '{github_id}')"
            )
        )
        await session.execute(text(f"DELETE FROM whitelist WHERE github_id = '{github_id}'"))
        await session.execute(text(f"DELETE FROM users WHERE github_id = '{github_id}'"))
        await session.commit()

    await engine.dispose()


async def _add_user_to_whitelist(github_id: str):
    """Add a user to whitelist."""
    engine = create_async_engine(settings.database_url)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        from app.models.whitelist import add_to_whitelist

        await add_to_whitelist(session, github_id)

    await engine.dispose()


async def _remove_user_from_whitelist(github_id: str):
    """Remove a user from whitelist."""
    engine = create_async_engine(settings.database_url)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        from app.models.whitelist import remove_from_whitelist

        await remove_from_whitelist(session, github_id)

    await engine.dispose()


def setup_test_user(github_id: str, is_admin: bool = False) -> int:
    """Sync wrapper for _setup_test_user."""
    return run_async(_setup_test_user(github_id, is_admin))


def cleanup_test_user(github_id: str):
    """Sync wrapper for _cleanup_test_user."""
    run_async(_cleanup_test_user(github_id))


def add_user_to_whitelist(github_id: str):
    """Sync wrapper for _add_user_to_whitelist."""
    run_async(_add_user_to_whitelist(github_id))


def remove_user_from_whitelist(github_id: str):
    """Sync wrapper for _remove_user_from_whitelist."""
    run_async(_remove_user_from_whitelist(github_id))


class TestProtectedEndpointWithoutToken:
    """Tests for accessing protected endpoints without authentication."""

    def test_protected_endpoint_without_token_returns_401(self, client: TestClient):
        """Test that accessing protected endpoint without token returns 401."""
        response = client.get("/api/protected")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_protected_endpoint_with_invalid_token_returns_401(self, client: TestClient):
        """Test that accessing protected endpoint with invalid token returns 401."""
        response = client.get(
            "/api/protected",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_protected_endpoint_with_malformed_header_returns_401(self, client: TestClient):
        """Test that malformed Authorization header returns 401."""
        response = client.get(
            "/api/protected",
            headers={"Authorization": "NotBearer token"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestWhitelistCheck:
    """Tests for whitelist verification on protected endpoints."""

    def test_protected_endpoint_not_whitelisted_returns_403(self, client: TestClient):
        """Test that valid token but not whitelisted returns 403."""
        github_id = "whitelist_test_user_1"
        try:
            user_id = setup_test_user(github_id)
            # User exists but not in whitelist
            token = create_jwt_token(user_id=user_id, github_id=github_id)
            response = client.get(
                "/api/protected",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == status.HTTP_403_FORBIDDEN
        finally:
            cleanup_test_user(github_id)

    def test_protected_endpoint_whitelisted_returns_200(self, client: TestClient):
        """Test that valid token and whitelisted returns 200."""
        github_id = "whitelist_test_user_2"
        try:
            user_id = setup_test_user(github_id)
            add_user_to_whitelist(github_id)

            token = create_jwt_token(user_id=user_id, github_id=github_id)
            response = client.get(
                "/api/protected",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == status.HTTP_200_OK
        finally:
            cleanup_test_user(github_id)

    def test_whitelist_removal_immediate_effect(self, client: TestClient):
        """Test that whitelist removal takes effect immediately."""
        github_id = "whitelist_test_user_3"
        try:
            user_id = setup_test_user(github_id)
            add_user_to_whitelist(github_id)
            token = create_jwt_token(user_id=user_id, github_id=github_id)

            # Access should work
            response = client.get(
                "/api/protected",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == status.HTTP_200_OK

            # Remove from whitelist
            remove_user_from_whitelist(github_id)

            # Same token should now fail (immediate effect)
            response = client.get(
                "/api/protected",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == status.HTTP_403_FORBIDDEN
        finally:
            cleanup_test_user(github_id)


class TestAdminOnlyEndpoint:
    """Tests for admin-only endpoints."""

    def test_admin_endpoint_without_token_returns_401(self, client: TestClient):
        """Test that admin endpoint without token returns 401."""
        response = client.get("/api/admin")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_admin_endpoint_non_admin_returns_403(self, client: TestClient):
        """Test that non-admin user gets 403 on admin endpoint."""
        github_id = "admin_test_user_1"
        try:
            user_id = setup_test_user(github_id, is_admin=False)
            add_user_to_whitelist(github_id)

            token = create_jwt_token(user_id=user_id, github_id=github_id)
            response = client.get(
                "/api/admin",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == status.HTTP_403_FORBIDDEN
        finally:
            cleanup_test_user(github_id)

    def test_admin_endpoint_admin_returns_200(self, client: TestClient):
        """Test that admin user can access admin endpoint."""
        github_id = "admin_test_user_2"
        try:
            user_id = setup_test_user(github_id, is_admin=True)
            add_user_to_whitelist(github_id)

            token = create_jwt_token(user_id=user_id, github_id=github_id)
            response = client.get(
                "/api/admin",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == status.HTTP_200_OK
        finally:
            cleanup_test_user(github_id)


class TestCurrentUserDependency:
    """Tests for getting current user from token."""

    def test_get_current_user_returns_user(self, client: TestClient):
        """Test that protected endpoint returns current user info."""
        github_id = "current_user_test"
        try:
            user_id = setup_test_user(github_id)
            add_user_to_whitelist(github_id)

            token = create_jwt_token(user_id=user_id, github_id=github_id)
            response = client.get(
                "/api/protected",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["user_id"] == user_id
            assert data["github_id"] == github_id
        finally:
            cleanup_test_user(github_id)

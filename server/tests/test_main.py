"""Tests for FastAPI application."""

from fastapi.testclient import TestClient


def test_app_starts():
    """Test that the FastAPI app can be imported and instantiated."""
    from app.main import app

    assert app is not None


def test_root_endpoint():
    """Test the root endpoint returns expected response."""
    from app.main import app

    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "status" in response.json()

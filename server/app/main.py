"""FastAPI application entry point."""

from fastapi import FastAPI

from app.config import settings

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)


@app.get("/")
async def root():
    """Root endpoint returning application status."""
    return {"status": "ok", "app": settings.app_name}

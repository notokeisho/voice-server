"""Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Voice Server"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://voice:password@localhost:5434/voice_server"

    # Whisper Server
    whisper_server_url: str = "http://localhost:8080"

    # JWT
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_days: int = 7

    # GitHub OAuth
    github_client_id: str = ""
    github_client_secret: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

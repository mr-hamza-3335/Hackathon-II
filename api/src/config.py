"""
Configuration module for environment variables.
T014: Create configuration module in api/src/config.py
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database Configuration (Neon PostgreSQL)
    database_url: str = "postgresql+asyncpg://localhost:5432/todo"

    # JWT Configuration (FR-028: 24-hour expiration, NFR-002: HS256)
    jwt_secret: str = "change-this-secret-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # CORS Configuration (FR-034, FR-035)
    frontend_url: str = "http://localhost:3000"

    # Rate Limiting (FR-036, FR-037)
    rate_limit_auth_per_minute: int = 10  # Per IP for auth endpoints
    rate_limit_tasks_per_minute: int = 100  # Per user for task endpoints

    # Environment
    environment: str = "development"
    debug: bool = True

    # Cookie settings (NFR-007)
    cookie_name: str = "auth_token"
    cookie_secure: bool = False  # Set True in production (HTTPS)
    cookie_samesite: str = "lax"
    cookie_httponly: bool = True
    cookie_max_age: int = 86400  # 24 hours in seconds

    # AI Assistant Configuration (Phase 3)
    anthropic_api_key: str = ""  # Required for AI features
    ai_model: str = "claude-3-haiku-20240307"  # Fast, cost-effective model
    ai_timeout_seconds: int = 10  # API timeout (NFR-301)
    ai_rate_limit_per_minute: int = 30  # Per user rate limit

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

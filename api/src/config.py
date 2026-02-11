"""
Configuration module for environment variables.
T014: Create configuration module in api/src/config.py
Phase III: Cohere AI Integration (FREE tier)
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
    frontend_url: str = "https://hackathon-ii-phi.vercel.app"

    # Rate Limiting (FR-036, FR-037)
    rate_limit_auth_per_minute: int = 10  # Per IP for auth endpoints
    rate_limit_tasks_per_minute: int = 100  # Per user for task endpoints

    # Environment
    environment: str = "development"
    debug: bool = True

    # Cookie settings (NFR-007)
    cookie_name: str = "auth_token"
    cookie_secure: bool = True  # HTTPS in production (Vercel + Render)
    cookie_samesite: str = "none"  # Required for cross-domain cookies
    cookie_httponly: bool = True
    cookie_max_age: int = 86400  # 24 hours in seconds

    # AI Assistant Configuration (Phase 3) - Cohere FREE tier
    # SECURITY: API keys loaded from environment variables only - NEVER hardcode
    cohere_api_key: str = ""  # Set via COHERE_API_KEY env var
    ai_provider: str = "cohere"  # AI provider name
    ai_model: str = "command-a-03-2025"  # Cohere model (FREE tier)
    ai_temperature: float = 0.3  # Lower temperature for consistent responses
    ai_max_tokens: int = 300  # Max tokens per response
    ai_timeout_seconds: int = 30  # API timeout
    ai_rate_limit_per_minute: int = 30  # Per user rate limit
    ai_max_input_length: int = 10000  # Max input message length for security

    # T-013: Dapr Configuration (Phase V — Event Publishing)
    # Constitution VII: All pub/sub via Dapr, no direct Kafka clients
    dapr_enabled: bool = False  # Enable event publishing via Dapr sidecar
    dapr_http_port: int = 3500  # Dapr sidecar HTTP port (auto-injected in K8s)
    dapr_pubsub_name: str = "pubsub-kafka"  # Dapr pubsub component name
    dapr_publish_timeout: float = 2.0  # HTTP timeout for publish calls (seconds)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

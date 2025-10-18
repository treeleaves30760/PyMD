"""Application Configuration"""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "PyMD Backend"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4

    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str
    REDIS_MAX_CONNECTIONS: int = 50

    # Auth0
    AUTH0_DOMAIN: str
    AUTH0_CLIENT_ID: str
    AUTH0_CLIENT_SECRET: str
    AUTH0_ALGORITHMS: list[str] = ["RS256"]

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list[str] = ["GET", "POST", "PUT", "DELETE", "PATCH"]
    CORS_HEADERS: list[str] = ["*"]

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60

    # Execution Limits
    EXECUTION_TIMEOUT_FREE: int = 30  # seconds
    EXECUTION_TIMEOUT_PRO: int = 300  # seconds
    EXECUTION_CPU_LIMIT_FREE: str = "0.5"  # CPU cores
    EXECUTION_CPU_LIMIT_PRO: str = "2.0"
    EXECUTION_MEMORY_LIMIT_FREE: str = "512m"
    EXECUTION_MEMORY_LIMIT_PRO: str = "2g"

    # Session
    SESSION_TTL: int = 86400  # 24 hours in seconds

    # Celery
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Create global settings instance
settings = Settings()

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # App
    APP_NAME: str = "POPULI Voting System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    SQL_ECHO: bool = False  # true = cetak setiap SQL ke log (ramah debugging, berisik)

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://populi:populi_dev_password@localhost:5432/voting_system"
    )
    DATABASE_URL_SYNC: str = Field(
        default="postgresql://populi:populi_dev_password@localhost:5432/voting_system"
    )

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET_KEY: str = Field(
        default="your-super-secret-jwt-key-change-in-production-min-32-chars",
        min_length=32,
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Password Hashing
    PASSWORD_HASH_ALGORITHM: str = "argon2id"
    ARGON2_TIME_COST: int = 3
    ARGON2_MEMORY_COST: int = 65536
    ARGON2_PARALLELISM: int = 4

    # AI Service
    AI_SERVICE_URL: str = "http://localhost:8001"
    AI_SERVICE_TIMEOUT: int = 30
    AI_SERVICE_API_KEY: str = "internal-service-key-change-in-production"

    # CORS
    CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"]
    )

    # Rate Limiting
    RATE_LIMIT_LOGIN: int = 5
    RATE_LIMIT_LOGIN_WINDOW: int = 300
    RATE_LIMIT_BIOMETRIC: int = 10
    RATE_LIMIT_BIOMETRIC_WINDOW: int = 300
    RATE_LIMIT_VOTING: int = 20
    RATE_LIMIT_VOTING_WINDOW: int = 60

    # Biometric
    MAX_BIOMETRIC_ATTEMPTS: int = 3
    BIOMETRIC_SIMILARITY_THRESHOLD: float = 0.85
    BIOMETRIC_CHALLENGE_EXPIRE_SECONDS: int = 120

    # Voting
    VOTING_TOKEN_EXPIRE_SECONDS: int = 300
    IDEMPOTENCY_KEY_EXPIRE_HOURS: int = 24

    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_IMAGE_TYPES: List[str] = Field(
        default_factory=lambda: ["image/jpeg", "image/png", "image/webp"]
    )

    @property
    def database_url_async(self) -> str:
        return self.DATABASE_URL

    @property
    def database_url_sync(self) -> str:
        return self.DATABASE_URL_SYNC


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
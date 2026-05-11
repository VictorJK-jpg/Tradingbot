"""Application settings via Pydantic v2.

All secrets come from environment variables. No hard-coded credentials.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Centralised configuration for all environments."""

    # App
    APP_NAME: str = Field(default="crypto-platform")
    DEBUG: bool = Field(default=False)
    ENVIRONMENT: str = Field(default="development")

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/crypto_platform"
    )

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    # Security
    SECRET_KEY: str = Field(default="change-me-in-production")
    ENCRYPTION_KEY: str = Field(default="change-me-in-production-32-bytes!")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)
    ALGORITHM: str = Field(default="HS256")

    # AI Provider (groq | openrouter | anthropic)
    AI_PROVIDER: str = Field(default="groq")
    AI_CALL_BUDGET_PER_USER: int = Field(default=50)

    # Groq (default)
    GROQ_API_KEY: str | None = Field(default=None)
    GROQ_MODEL: str = Field(default="llama-3.3-70b-versatile")

    # OpenRouter
    OPENROUTER_API_KEY: str | None = Field(default=None)
    OPENROUTER_MODEL: str = Field(default="meta-llama/llama-3.3-70b-instruct")

    # Anthropic
    ANTHROPIC_API_KEY: str | None = Field(default=None)
    ANTHROPIC_MODEL: str = Field(default="claude-sonnet-4-20250514")

    # External APIs
    COINGECKO_API_KEY: str | None = Field(default=None)
    CRYPTOPANIC_API_KEY: str | None = Field(default=None)
    NEWSAPI_KEY: str | None = Field(default=None)
    FRED_API_KEY: str | None = Field(default=None)
    LUNARCRUSH_API_KEY: str | None = Field(default=None)

    # Telegram
    TELEGRAM_BOT_TOKEN_DEV: str | None = Field(default=None)
    TELEGRAM_BOT_TOKEN_PROD: str | None = Field(default=None)
    TELEGRAM_CHAT_ID: str | None = Field(default=None)

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

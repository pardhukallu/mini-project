from typing import List, Optional
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "ShadowWatch"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"
    
    # Security & JWT
    SECRET_KEY: str = "shadowwatch_dev_super_secret_key_change_in_production_9f82d1c7e"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    # Defaults to async SQLite for friction-free local execution;
    # automatically upgrades to PostgreSQL when DATABASE_URL is configured
    DATABASE_URL: str = "sqlite+aiosqlite:///./shadowwatch.db"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
    
    # External APIs (Optional in Phase 1 / configurable in .env)
    GEMINI_API_KEY: Optional[str] = None

    # Email-existence verification (breach data cannot confirm a mailbox exists).
    # Default "smtp" probes the recipient's mail server directly: free, no key.
    # Optional paid providers: "abstract", "hunter", "zerobounce".
    EMAIL_VERIFICATION_PROVIDER: str = "smtp"
    EMAIL_VERIFICATION_API_KEY: Optional[str] = None
    EMAIL_VERIFICATION_TIMEOUT_SECONDS: float = 10.0

    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_url(cls, v: Optional[str]) -> str:
        if not v:
            return "sqlite+aiosqlite:///./shadowwatch.db"
        # Convert standard postgresql:// to postgresql+asyncpg:// if needed
        if v.startswith("postgresql://") and not v.startswith("postgresql+asyncpg://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        if v.startswith("postgres://") and not v.startswith("postgresql+asyncpg://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()

"""Application configuration using environment variables."""
import os
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "ScraperFC API"
    APP_ENV: str = "development"
    APP_VERSION: str = "1.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    
    # Database - Supabase/Postgres
    DATABASE_URL: Optional[str] = None
    SUPABASE_URL: Optional[str] = None
    SUPABASE_DB_HOST: Optional[str] = None
    SUPABASE_DB_PORT: str = "5432"
    SUPABASE_DB_NAME: str = "postgres"
    SUPABASE_DB_USER: Optional[str] = None
    SUPABASE_DB_PASSWORD: Optional[str] = None
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    
    # CORS
    CORS_ORIGINS: str = "*"
    
    # Sync configuration
    SYNC_INTERVAL_MINUTES: int = 5
    HISTORY_DAYS_PAST: int = 30
    HISTORY_DAYS_FUTURE: int = 30
    DEFAULT_TIMEZONE: str = "UTC"
    
    # Provider settings
    ENABLE_SOFASCORE: bool = True
    ENABLE_FBREF: bool = False  # Pode ser lento, desabilitado por padrão
    FBREF_WAIT_TIME: int = 6
    
    # Retry settings
    MAX_RETRIES: int = 3
    RETRY_BACKOFF_SECONDS: int = 2
    
    @property
    def database_url_computed(self) -> str:
        """Compute database URL from components or use direct URL."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        
        if not all([self.SUPABASE_DB_HOST, self.SUPABASE_DB_USER, self.SUPABASE_DB_PASSWORD]):
            raise ValueError(
                "Either DATABASE_URL or all of SUPABASE_DB_HOST, SUPABASE_DB_USER, "
                "and SUPABASE_DB_PASSWORD must be set"
            )
        
        return (
            f"postgresql://{self.SUPABASE_DB_USER}:{self.SUPABASE_DB_PASSWORD}"
            f"@{self.SUPABASE_DB_HOST}:{self.SUPABASE_DB_PORT}/{self.SUPABASE_DB_NAME}"
        )
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Convert CORS origins string to list."""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()

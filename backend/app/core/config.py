"""
Configuration Management for seitenkraft.org

Loads environment variables and provides typed configuration objects.
"""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application Settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    debug: bool = False
    log_level: str = "INFO"

    # Supabase
    supabase_url: str
    supabase_key: str
    supabase_db_password: Optional[str] = None

    # INWX API
    inwx_api_url: str = "https://api.ote.inwx.com/jsonrpc/"
    inwx_username: str
    inwx_password: str

    # Fake Authentication (POC only)
    fake_auth_token: str = "dev-token-123"

    # CORS
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080"
    ]

    @property
    def is_production(self) -> bool:
        """Check if running in production (based on INWX URL)"""
        return "api.inwx.com" in self.inwx_api_url


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Using lru_cache ensures we only load env vars once.
    """
    return Settings()

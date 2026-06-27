"""
config.py - typed configuration loaded from environment variables.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """all runtime config for the MaskWise API"""

    app_env: str = "development"
    app_port: int = 8005
    log_level: str = "INFO"

    # raw comma-separated string from env - parsed via api_keys_list below
    api_keys: str = "dev-only-key-replace-in-production"

    # slowapi format: "60/minute", "1000/hour"
    rate_limit: str = "60/minute"

    # postgres connection - real value comes from MASKWISE_DATABASE_URL in .env
    database_url: str = "postgresql://maskwise:devpass@localhost:5432/maskwise"

    # JWT login tokens - secret comes from MASKWISE_JWT_SECRET in .env
    jwt_secret: str = "dev-only-secret-replace-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    @property
    def api_keys_list(self) -> list[str]:
        """split MASKWISE_API_KEYS into a clean list at access time"""
        return [k.strip() for k in self.api_keys.split(",") if k.strip()]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="maskwise_",
        extra="ignore",
    )


settings = Settings()

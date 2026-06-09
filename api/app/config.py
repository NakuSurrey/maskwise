"""
config.py — typed configuration loaded from environment variables.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """all runtime config for the MaskWise API"""

    app_env: str = "development"
    app_port: int = 8005
    log_level: str = "INFO"

    # raw comma-separated string from env — parsed via api_keys_list below
    api_keys: str = "dev-only-key-replace-in-production"

    # slowapi format: "60/minute", "1000/hour"
    rate_limit: str = "60/minute"

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

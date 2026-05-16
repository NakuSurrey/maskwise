"""
config.py — typed configuration loaded from environment variables.

using pydantic-settings so:
  - every env var is type-checked on startup
  - missing required vars fail fast with a clear error
  - defaults are explicit, not buried in os.environ.get calls
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """all runtime config for the MaskWise API"""

    # ─── app ────────────────────────────────────────────────────
    app_env: str = "development"
    # values: development | production
    # production switches off interactive docs at /docs

    app_port: int = 8005
    # internal port — docker-compose maps host 127.0.0.1:8005 to this

    log_level: str = "INFO"
    # values: DEBUG | INFO | WARNING | ERROR
    # NEVER set to DEBUG in production — risk of logging request bodies

    # ─── stub phase note ────────────────────────────────────────
    # redis, postgres, cors, rate-limit settings will be added in Phase 1
    # right now we only need enough to run /health

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,        # APP_ENV and app_env both work
        extra="ignore",              # ignore unknown env vars (helpful when sharing one .env across services)
    )


# single shared instance — imported anywhere via `from app.config import settings`
settings = Settings()

from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[3] / '.env',
        extra='ignore',
    )

    # Keep SQLite in the backend directory regardless of the shell's current
    # working directory. This ensures Alembic and Uvicorn open the same file.
    database_url: str = f"sqlite:///{(BACKEND_ROOT / 'marketpulse.db').as_posix()}"

    @field_validator('database_url', mode='before')
    @classmethod
    def resolve_relative_sqlite_url(cls, value: str) -> str:
        if not isinstance(value, str) or not value.startswith('sqlite:///'):
            return value

        database_path = value.removeprefix('sqlite:///')
        if database_path == ':memory:' or database_path.startswith('file:'):
            return value

        path = Path(database_path)
        if not path.is_absolute():
            path = BACKEND_ROOT / path
        return f"sqlite:///{path.resolve().as_posix()}"

    admin_api_key: str = 'change-me'
    yahoo_timeout_seconds: float = 20.0
    yahoo_retries: int = 3
    yahoo_rate_limit_delay_seconds: float = 1.0
    ingestion_max_attempts: int = 3
    ingestion_retry_base_delay_seconds: float = 0.5
    fx_provider: str = 'frankfurter'
    fx_timeout_seconds: float = 10.0
    fx_retries: int = 3
    fx_stale_days: int = 7
    redis_url: str = 'redis://localhost:6379/0'
    market_data_provider: str = 'none'
    market_data_api_key: str | None = None
    market_data_api_secret: str | None = None
    market_data_mode: str = 'snapshot'
    market_data_delay_seconds: int = 0
    market_data_cache_ttl: int = 300
    market_data_max_subscriptions: int = 100
    market_data_max_connections: int = 1000
    market_data_persistence_mode: str = 'latest-state-only'


settings = Settings()

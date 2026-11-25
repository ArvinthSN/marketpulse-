from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[3] / '.env',
        extra='ignore',
    )

    database_url: str = 'sqlite:///./marketpulse.db'
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

    eodhd_api_key: str | None = None
    twelve_data_api_key: str | None = None
    massive_api_key: str | None = None
    market_data_fallback_providers: str = 'twelvedata,massive'
    market_data_provider_timeout_seconds: float = 15.0
    market_data_provider_retries: int = 2


settings = Settings()

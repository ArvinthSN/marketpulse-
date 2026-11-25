from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    database_url: str = 'postgresql+psycopg://marketpulse:marketpulse@localhost:5432/marketpulse'
    admin_api_key: str = 'change-me'
    yahoo_timeout_seconds: float = 20.0
    yahoo_retries: int = 3
    yahoo_rate_limit_delay_seconds: float = 1.0
    ingestion_max_attempts: int = 3
    ingestion_retry_base_delay_seconds: float = 0.5


settings = Settings()

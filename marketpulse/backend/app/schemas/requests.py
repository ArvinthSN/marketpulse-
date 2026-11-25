from pydantic import BaseModel, Field


class IngestionRequest(BaseModel):
    country_code: str | None = Field(default=None, min_length=2, max_length=2)
    exchange_code: str | None = Field(default=None, max_length=20)
    limit: int = Field(default=100, ge=1, le=10000)
    period: str = Field(default='1y', max_length=20)
    interval: str = Field(default='1d', max_length=20)

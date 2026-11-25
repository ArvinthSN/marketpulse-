from datetime import datetime
from pydantic import BaseModel


class DataCoverage(BaseModel):
    expected: int
    available: int
    missing: int


class DataQuality(BaseModel):
    data_status: str
    source: str = 'persisted_historical_data'
    last_market_observation: datetime | None = None
    calculated_at: datetime
    is_stale: bool
    coverage: DataCoverage
    warnings: list[str] = []


class CompanyPerformance(BaseModel):
    company_id: int
    symbol: str
    currency: str
    reporting_currency: str
    performance: dict[str, float | None]
    price_basis: str
    data_quality: DataQuality

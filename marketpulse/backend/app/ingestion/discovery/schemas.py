from datetime import datetime
from pydantic import BaseModel, Field


class DiscoveredInstrument(BaseModel):
    country_code: str = Field(min_length=2, max_length=2)
    exchange_code: str = Field(min_length=1, max_length=20)
    symbol: str = Field(min_length=1, max_length=50)
    original_symbol: str = Field(min_length=1, max_length=50)
    normalized_symbol: str = Field(min_length=1, max_length=50)
    company_name: str = Field(min_length=1, max_length=300)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    instrument_type: str = 'equity'
    active: bool = True
    source: str


class DiscoveryReport(BaseModel):
    source: str
    exchange_code: str | None = None
    country_code: str | None = None
    generated_at: datetime
    total_discovered: int = 0
    validated: int = 0
    rejected: int = 0
    duplicates: int = 0
    unsupported_symbols: int = 0
    exchange_coverage: dict[str, int] = Field(default_factory=dict)
    completeness: str

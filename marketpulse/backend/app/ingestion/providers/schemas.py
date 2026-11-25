from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class CompanyProfile(BaseModel):
    name: str
    short_name: str | None = None
    sector: str | None = None
    website: str | None = None
    market_cap: Decimal | None = None


class OHLCVRecord(BaseModel):
    timestamp: datetime
    open: Decimal = Field(gt=0)
    high: Decimal = Field(gt=0)
    low: Decimal = Field(gt=0)
    close: Decimal = Field(gt=0)
    adjusted_close: Decimal | None = Field(default=None, gt=0)
    volume: int = Field(ge=0)
    currency: str


class QuoteRecord(BaseModel):
    symbol: str
    price: Decimal | None = None
    currency: str | None = None
    timestamp: datetime | None = None

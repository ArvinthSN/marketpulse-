from datetime import datetime
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field


class QuoteDataStatus(str, Enum):
    LIVE = 'LIVE'
    DELAYED = 'DELAYED'
    SNAPSHOT = 'SNAPSHOT'
    STALE = 'STALE'
    UNAVAILABLE = 'UNAVAILABLE'


class NormalizedQuote(BaseModel):
    symbol: str = Field(min_length=1, max_length=50)
    company_id: int | None = None
    exchange: str = Field(min_length=1, max_length=20)
    price: Decimal | None = Field(default=None, gt=0)
    previous_close: Decimal | None = Field(default=None, gt=0)
    change: Decimal | None = None
    change_percentage: Decimal | None = None
    volume: int = Field(default=0, ge=0)
    currency: str = Field(min_length=3, max_length=3)
    source: str
    market_timestamp: datetime
    received_at: datetime
    data_delay_seconds: int = Field(default=0, ge=0)
    data_status: QuoteDataStatus


class SubscriptionMessage(BaseModel):
    action: str
    symbols: list[str] = Field(default_factory=list, max_length=100)

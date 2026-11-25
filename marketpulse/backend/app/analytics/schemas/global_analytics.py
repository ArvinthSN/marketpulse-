from datetime import datetime
from pydantic import BaseModel


class GlobalOverview(BaseModel):
    market: str = 'global'
    period: str
    reporting_currency: str
    calculated_at: datetime
    data_status: str
    tracked_companies: int
    active_exchanges: int
    market_breadth: dict

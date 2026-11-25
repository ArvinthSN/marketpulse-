from pydantic import BaseModel


class SectorAnalytics(BaseModel):
    sector_id: int
    sector_name: str
    reporting_currency: str
    market_cap_weighted_return: float | None
    equal_weighted_return: float | None
    total_market_cap: float | None
    total_volume: int | None
    listed_companies: int
    valid_companies: int
    breadth: dict

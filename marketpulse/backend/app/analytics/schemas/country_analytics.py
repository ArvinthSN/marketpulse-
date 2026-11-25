from pydantic import BaseModel


class CountryAnalytics(BaseModel):
    country_code: str
    country_name: str
    reporting_currency: str
    market_cap_weighted_return: float | None
    equal_weighted_return: float | None
    total_market_cap: float | None
    tracked_companies: int
    breadth: dict

from datetime import datetime, timedelta, timezone
from app.analytics.calculations.market_cap import market_cap_from_inputs


class MarketCapService:
    def __init__(self, stale_shares_days: int = 180, stale_price_days: int = 7):
        self.stale_shares_days = stale_shares_days
        self.stale_price_days = stale_price_days

    def calculate(self, company, latest_price: float | None, latest_observation_at: datetime | None,
                  reporting_currency: str, now: datetime | None = None):
        now = now or datetime.now(timezone.utc)
        if latest_observation_at is not None:
            observation_at = latest_observation_at.replace(tzinfo=timezone.utc) if latest_observation_at.tzinfo is None else latest_observation_at.astimezone(timezone.utc)
            price_stale = now - observation_at > timedelta(days=self.stale_price_days)
        else:
            price_stale = True

        shares = float(company.shares_outstanding) if company.shares_outstanding is not None else None
        shares_at = company.shares_outstanding_at
        shares_stale = True
        if shares_at is not None:
            shares_at = shares_at.replace(tzinfo=timezone.utc) if shares_at.tzinfo is None else shares_at.astimezone(timezone.utc)
            shares_stale = now - shares_at > timedelta(days=self.stale_shares_days)

        currency = reporting_currency
        if shares is None:
            return market_cap_from_inputs(latest_price, None, currency, 'missing_shares_outstanding', price_stale or shares_stale)
        if shares_stale:
            result = market_cap_from_inputs(latest_price, shares, currency,
                                            company.shares_outstanding_source or 'provider_estimated', True)
            return result
        source = company.shares_outstanding_source or 'provider_estimated'
        return market_cap_from_inputs(latest_price, shares, currency, source, price_stale)

from dataclasses import dataclass


@dataclass(frozen=True)
class MarketCapResult:
    value: float | None
    currency: str
    source: str
    estimated: bool
    stale: bool
    warning: str | None = None


def market_cap_from_inputs(price: float | None, shares_outstanding: float | None,
                           currency: str, source: str = 'provider_estimated', stale: bool = False) -> MarketCapResult:
    if price is None or shares_outstanding is None:
        return MarketCapResult(None, currency, source, True, stale, 'missing_price_or_shares_outstanding')
    if price <= 0 or shares_outstanding <= 0:
        return MarketCapResult(None, currency, source, True, stale, 'invalid_price_or_shares_outstanding')
    return MarketCapResult(price * shares_outstanding, currency, source, source != 'provider_reported', stale)

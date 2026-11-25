from app.market_data.providers.base import AsyncMarketDataProvider


class LicensedProviderNotConfigured(AsyncMarketDataProvider):
    """Safe placeholder adapter; no credentials or provider endpoints are invented."""

    async def connect(self) -> None:
        return None

    async def disconnect(self) -> None:
        return None

    async def subscribe(self, symbols: list[str]) -> None:
        return None

    async def unsubscribe(self, symbols: list[str]) -> None:
        return None

    async def get_quote(self, symbol: str) -> dict | None:
        return None

    async def get_quotes(self, symbols: list[str]) -> list[dict]:
        return []

    async def health_check(self) -> dict:
        return {'provider': 'licensed', 'configured': False, 'state': 'unavailable'}

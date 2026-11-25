from __future__ import annotations

from app.core.config import settings
from app.market_data.providers.base import AsyncMarketDataProvider
from app.market_data.providers.licensed_provider import LicensedProviderNotConfigured
from app.market_data.providers.yahoo_provider import YahooSnapshotProvider
from app.market_data.providers.eodhd_provider import EODHDProvider
from app.market_data.providers.twelve_data_provider import TwelveDataProvider
from app.market_data.providers.massive_provider import MassiveProvider


class FallbackMarketDataProvider(AsyncMarketDataProvider):
    """Try the primary provider, then configured fallbacks on request failures."""

    def __init__(self, providers: list[AsyncMarketDataProvider]):
        self.providers = providers

    async def connect(self) -> None:
        for provider in self.providers:
            await provider.connect()

    async def disconnect(self) -> None:
        for provider in self.providers:
            await provider.disconnect()

    async def subscribe(self, symbols: list[str]) -> None:
        raise NotImplementedError("Configured REST providers are snapshot-only")

    async def unsubscribe(self, symbols: list[str]) -> None:
        return None

    async def get_quote(self, symbol: str) -> dict | None:
        for provider in self.providers:
            try:
                quote = await provider.get_quote(symbol)
                if quote:
                    return quote
            except Exception:
                continue
        return None

    async def get_quotes(self, symbols: list[str]) -> list[dict]:
        quotes = []
        for symbol in symbols:
            quote = await self.get_quote(symbol)
            if quote:
                quotes.append(quote)
        return quotes

    async def get_history(self, symbol: str, *, start: str, end: str,
                          interval: str = "1day") -> list[dict]:
        for provider in self.providers:
            method = getattr(provider, "get_history", None)
            if method is None:
                continue
            try:
                rows = await method(symbol, start=start, end=end, interval=interval)
                if rows:
                    return rows
            except Exception:
                continue
        return []

    async def get_company(self, symbol: str) -> dict | None:
        for provider in self.providers:
            method = getattr(provider, "get_company", None)
            if method is None:
                continue
            try:
                company = await method(symbol)
                if company:
                    return company
            except Exception:
                continue
        return None

    async def health_check(self) -> dict:
        statuses = []
        for provider in self.providers:
            try:
                statuses.append(await provider.health_check())
            except Exception as exc:
                statuses.append({"state": "error", "error": str(exc)})
        return {"provider": "fallback-chain", "providers": statuses,
                "configured": bool(self.providers), "streaming": False}


class ProviderFactory:
    @staticmethod
    def create() -> AsyncMarketDataProvider:
        configured = {
            "eodhd": (settings.eodhd_api_key, EODHDProvider),
            "twelvedata": (settings.twelve_data_api_key, TwelveDataProvider),
            "massive": (settings.massive_api_key, MassiveProvider),
        }
        names = [settings.market_data_provider.strip().lower()]
        names.extend(name.strip().lower() for name in settings.market_data_fallback_providers.split(",") if name.strip())
        if names[0] in {"", "none"}:
            return LicensedProviderNotConfigured()
        providers = []
        seen = set()
        for name in names:
            if name in seen:
                continue
            seen.add(name)
            if name == "yahoo":
                providers.append(YahooSnapshotProvider())
                continue
            entry = configured.get(name)
            if entry and entry[0]:
                providers.append(entry[1](api_key=entry[0],
                    timeout=settings.market_data_provider_timeout_seconds,
                    retries=settings.market_data_provider_retries))
        return FallbackMarketDataProvider(providers) if providers else LicensedProviderNotConfigured()

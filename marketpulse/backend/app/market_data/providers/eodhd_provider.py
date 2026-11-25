from datetime import datetime, timezone
from typing import Any

from app.market_data.providers.rest_base import RestMarketDataProvider


class EODHDProvider(RestMarketDataProvider):
    provider_name = "eodhd"
    base_url = "https://eodhd.com/api"

    def _params(self, **kwargs: Any) -> dict[str, Any]:
        return {"api_token": self.api_key, "fmt": "json", **kwargs}

    @staticmethod
    def _symbol(symbol: str) -> str:
        return symbol.strip().upper()

    async def get_quote(self, symbol: str) -> dict | None:
        payload = await self._get(f"/real-time/{self._symbol(symbol)}",
                                  params=self._params())
        if not isinstance(payload, dict) or not payload:
            return None
        price = payload.get("close") or payload.get("price")
        if price is None:
            return None
        timestamp = payload.get("timestamp")
        market_time = (datetime.fromtimestamp(float(timestamp), timezone.utc)
                       if timestamp else datetime.now(timezone.utc))
        return {
            "symbol": payload.get("code") or self._symbol(symbol),
            "price": price,
            "previous_close": payload.get("previousClose"),
            "volume": payload.get("volume", 0),
            "currency": payload.get("currency") or "USD",
            "market_timestamp": market_time,
            "source": self.provider_name,
            "data_status": "DELAYED",
        }

    async def get_history(self, symbol: str, *, start: str, end: str,
                          interval: str = "1day") -> list[dict]:
        if interval not in {"1day", "daily"}:
            raise ValueError("EODHD historical adapter currently supports daily bars only")
        payload = await self._get(f"/eod/{self._symbol(symbol)}",
            params=self._params(**{"from": start, "to": end}))
        return [self._bar(row) for row in payload if isinstance(row, dict)] if isinstance(payload, list) else []

    @staticmethod
    def _bar(row: dict) -> dict:
        return {"timestamp": row.get("date"), "open": row.get("open"),
                "high": row.get("high"), "low": row.get("low"),
                "close": row.get("adjusted_close", row.get("close")),
                "volume": row.get("volume"), "source": "eodhd"}

    async def get_company(self, symbol: str) -> dict | None:
        payload = await self._get(f"/fundamentals/{self._symbol(symbol)}",
                                  params=self._params())
        if not isinstance(payload, dict):
            return None
        general = payload.get("General") or {}
        highlights = payload.get("Highlights") or {}
        return {"symbol": self._symbol(symbol), "name": general.get("Name"),
                "exchange": general.get("Exchange"), "currency": general.get("CurrencyCode"),
                "country": general.get("CountryName"), "sector": general.get("Sector"),
                "industry": general.get("Industry"), "market_cap": highlights.get("MarketCapitalization"),
                "source": self.provider_name}

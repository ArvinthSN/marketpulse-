from datetime import datetime, timezone
from app.market_data.providers.rest_base import RestMarketDataProvider


class MassiveProvider(RestMarketDataProvider):
    """Massive (formerly Polygon) adapter; current implementation targets US equities."""
    provider_name = "massive"
    base_url = "https://api.massive.com"

    def _auth(self) -> dict:
        return {"apiKey": self.api_key}

    async def get_quote(self, symbol: str) -> dict | None:
        payload = await self._get(
            f"/v2/snapshot/locale/us/markets/stocks/tickers/{symbol.upper()}",
            params=self._auth(),
        )
        ticker = payload.get("ticker", payload) if isinstance(payload, dict) else {}
        day = ticker.get("day") or {}
        last_trade = ticker.get("lastTrade") or {}
        price = last_trade.get("p") or day.get("c")
        if price is None:
            return None
        timestamp_ns = last_trade.get("t")
        market_time = (datetime.fromtimestamp(int(timestamp_ns) / 1_000_000_000, timezone.utc)
                       if timestamp_ns else datetime.now(timezone.utc))
        previous = (ticker.get("prevDay") or {}).get("c")
        return {"symbol": ticker.get("ticker", symbol.upper()), "price": price,
                "previous_close": previous, "volume": day.get("v", 0),
                "currency": "USD", "market_timestamp": market_time,
                "source": self.provider_name, "data_status": "SNAPSHOT"}

    async def get_history(self, symbol: str, *, start: str, end: str,
                          interval: str = "1day") -> list[dict]:
        interval_map = {"1min": (1, "minute"), "5min": (5, "minute"),
                        "15min": (15, "minute"), "1hour": (1, "hour"),
                        "1day": (1, "day"), "daily": (1, "day")}
        if interval not in interval_map:
            raise ValueError(f"Unsupported Massive interval: {interval}")
        multiplier, timespan = interval_map[interval]
        payload = await self._get(
            f"/v2/aggs/ticker/{symbol.upper()}/range/{multiplier}/{timespan}/{start}/{end}",
            params={**self._auth(), "adjusted": "true", "sort": "asc", "limit": 50000},
        )
        if not isinstance(payload, dict):
            return []
        return [{"timestamp": datetime.fromtimestamp(row["t"] / 1000, timezone.utc).isoformat(),
                 "open": row.get("o"), "high": row.get("h"), "low": row.get("l"),
                 "close": row.get("c"), "volume": row.get("v"), "source": self.provider_name}
                for row in payload.get("results", [])]

    async def get_company(self, symbol: str) -> dict | None:
        payload = await self._get(f"/v3/reference/tickers/{symbol.upper()}",
                                  params=self._auth())
        result = payload.get("results") if isinstance(payload, dict) else None
        if not isinstance(result, dict):
            return None
        return {"symbol": result.get("ticker", symbol.upper()),
                "name": result.get("name"), "exchange": result.get("primary_exchange"),
                "currency": result.get("currency_name"), "market": result.get("market"),
                "locale": result.get("locale"), "market_cap": result.get("market_cap"),
                "source": self.provider_name}

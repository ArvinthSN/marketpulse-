from datetime import datetime, timezone
from app.market_data.providers.rest_base import RestMarketDataProvider


class TwelveDataProvider(RestMarketDataProvider):
    provider_name = "twelvedata"
    base_url = "https://api.twelvedata.com"

    def _params(self, **kwargs):
        return {"symbol": kwargs.pop("symbol", None), **kwargs}

    async def get_quote(self, symbol: str) -> dict | None:
        payload = await self._get("/quote", params={"symbol": symbol, "apikey": self.api_key})
        if not isinstance(payload, dict) or payload.get("status") == "error":
            raise RuntimeError(str(payload.get("message", "Twelve Data quote failed")))
        price = payload.get("close") or payload.get("price")
        if price is None:
            return None
        timestamp = payload.get("timestamp")
        market_time = (datetime.fromtimestamp(float(timestamp), timezone.utc)
                       if timestamp else datetime.now(timezone.utc))
        return {"symbol": payload.get("symbol", symbol), "price": price,
                "previous_close": payload.get("previous_close"),
                "volume": payload.get("volume", 0), "currency": payload.get("currency") or "USD",
                "market_timestamp": market_time, "source": self.provider_name,
                "data_status": "SNAPSHOT"}

    async def get_history(self, symbol: str, *, start: str, end: str,
                          interval: str = "1day") -> list[dict]:
        payload = await self._get("/time_series", params={
            "symbol": symbol, "interval": interval, "start_date": start,
            "end_date": end, "outputsize": 5000, "apikey": self.api_key,
        })
        if not isinstance(payload, dict) or "values" not in payload:
            raise RuntimeError(str(payload.get("message", "Twelve Data time_series failed")))
        return [{"timestamp": row.get("datetime"), "open": row.get("open"),
                 "high": row.get("high"), "low": row.get("low"), "close": row.get("close"),
                 "volume": row.get("volume"), "source": self.provider_name}
                for row in payload["values"]]

    async def get_company(self, symbol: str) -> dict | None:
        payload = await self._get("/profile", params={"symbol": symbol, "apikey": self.api_key})
        if not isinstance(payload, dict) or payload.get("status") == "error":
            raise RuntimeError(str(payload.get("message", "Twelve Data profile failed")))
        return {"symbol": symbol, "name": payload.get("name"),
                "exchange": payload.get("exchange"), "currency": payload.get("currency"),
                "country": payload.get("country"), "sector": payload.get("sector"),
                "industry": payload.get("industry"), "source": self.provider_name}

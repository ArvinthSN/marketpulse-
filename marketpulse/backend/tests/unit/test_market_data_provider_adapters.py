import asyncio

from app.market_data.providers.eodhd_provider import EODHDProvider
from app.market_data.providers.twelve_data_provider import TwelveDataProvider
from app.market_data.providers.massive_provider import MassiveProvider
from app.market_data.providers.provider_factory import FallbackMarketDataProvider


def test_eodhd_quote_normalization(monkeypatch):
    provider = EODHDProvider("test-key")
    async def fake_get(path, params=None):
        assert path == "/real-time/AAPL.US"
        return {"code": "AAPL.US", "close": 190.5, "previousClose": 188,
                "volume": 1000, "currency": "USD", "timestamp": 1764000000}
    monkeypatch.setattr(provider, "_get", fake_get)
    quote = asyncio.run(provider.get_quote("AAPL.US"))
    assert quote["price"] == 190.5
    assert quote["previous_close"] == 188
    assert quote["source"] == "eodhd"


def test_twelve_data_time_series_maps_ohlcv(monkeypatch):
    provider = TwelveDataProvider("test-key")
    async def fake_get(path, params=None):
        assert path == "/time_series"
        return {"values": [{"datetime": "2026-11-24", "open": "1", "high": "2",
                            "low": "0.5", "close": "1.5", "volume": "12"}]}
    monkeypatch.setattr(provider, "_get", fake_get)
    rows = asyncio.run(provider.get_history("ABC", start="2026-11-01", end="2026-11-24"))
    assert rows[0]["close"] == "1.5"
    assert rows[0]["volume"] == "12"


def test_massive_aggregate_maps_ohlcv(monkeypatch):
    provider = MassiveProvider("test-key")
    async def fake_get(path, params=None):
        return {"results": [{"t": 1795507200000, "o": 10, "h": 12,
                             "l": 9, "c": 11, "v": 100}]}
    monkeypatch.setattr(provider, "_get", fake_get)
    rows = asyncio.run(provider.get_history("ABC", start="2026-11-01", end="2026-11-24"))
    assert rows[0]["open"] == 10
    assert rows[0]["close"] == 11


def test_fallback_uses_secondary_after_primary_failure():
    class Provider:
        def __init__(self, result=None, fail=False):
            self.result, self.fail = result, fail
        async def get_quote(self, symbol):
            if self.fail:
                raise RuntimeError("provider unavailable")
            return self.result
    fallback = FallbackMarketDataProvider([
        Provider(fail=True), Provider({"symbol": "ABC", "price": 10})
    ])
    quote = asyncio.run(fallback.get_quote("ABC"))
    assert quote["price"] == 10

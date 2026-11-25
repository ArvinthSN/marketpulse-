from datetime import datetime, timezone
from app.market_data.providers.base import AsyncMarketDataProvider


class YahooSnapshotProvider(AsyncMarketDataProvider):
    """Snapshot-only adapter. This class does not claim or implement streaming."""

    async def connect(self) -> None:
        return None

    async def disconnect(self) -> None:
        return None

    async def subscribe(self, symbols: list[str]) -> None:
        raise NotImplementedError('Yahoo snapshot provider does not implement streaming subscriptions')

    async def unsubscribe(self, symbols: list[str]) -> None:
        return None

    async def get_quote(self, symbol: str) -> dict | None:
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            fast = ticker.fast_info
            price = fast.get('last_price')
            currency = fast.get('currency')
            if price is None:
                return None
            return {'symbol': symbol, 'price': price, 'currency': currency or 'USD',
                    'market_timestamp': datetime.now(timezone.utc)}
        except Exception:
            return None

    async def get_quotes(self, symbols: list[str]) -> list[dict]:
        quotes = []
        for symbol in symbols:
            quote = await self.get_quote(symbol)
            if quote:
                quotes.append(quote)
        return quotes

    async def health_check(self) -> dict:
        return {'provider': 'yahoo', 'configured': True, 'streaming': False,
                'state': 'snapshot_only'}

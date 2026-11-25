from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.core.config import settings
from app.market_data.providers.provider_factory import ProviderFactory
from app.market_data.normalization.quote_normalizer import QuoteNormalizer
from app.market_data.schemas.quote import QuoteDataStatus
from app.market_data.repositories.live_quote_repository import LiveQuoteRepository


class LiveMarketService:
    def __init__(self, db: Session, quote_cache):
        self.db = db
        self.quote_cache = quote_cache
        self.provider = ProviderFactory.create()

    async def get_quote(self, symbol: str, exchange: str = 'NASDAQ'):
        cached = await self.quote_cache.get_quote(exchange, symbol)
        if cached:
            return cached
        raw = await self.provider.get_quote(symbol)
        if not raw:
            persisted = LiveQuoteRepository(self.db).latest_snapshot(symbol)
            if persisted:
                persisted['received_at'] = datetime.now(timezone.utc).isoformat()
                persisted['data_status'] = 'SNAPSHOT'
            return persisted
        raw.setdefault('exchange', exchange)
        raw.setdefault('received_at', datetime.now(timezone.utc))
        status = QuoteDataStatus.DELAYED if settings.market_data_delay_seconds > 0 else QuoteDataStatus.SNAPSHOT
        quote = QuoteNormalizer.normalize(raw, exchange=exchange,
                                          source=settings.market_data_provider or 'snapshot_provider',
                                          default_status=status,
                                          delay_seconds=settings.market_data_delay_seconds)
        await self.quote_cache.set_quote(quote, settings.market_data_cache_ttl)
        return quote.model_dump(mode='json')

    async def get_quotes(self, symbols: list[str], exchange: str = 'NASDAQ'):
        return [quote for symbol in symbols if (quote := await self.get_quote(symbol, exchange)) is not None]

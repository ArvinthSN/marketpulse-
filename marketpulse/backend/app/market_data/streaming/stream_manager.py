import asyncio
import logging
from collections import deque

from app.market_data.normalization.quote_normalizer import QuoteNormalizer
from app.market_data.normalization.market_event import quote_event

logger = logging.getLogger(__name__)


class LiveEventProcessor:
    def __init__(self, quote_cache, pubsub, connection_manager, queue_size: int = 10000):
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=queue_size)
        self.quote_cache = quote_cache
        self.pubsub = pubsub
        self.connection_manager = connection_manager
        self.seen: deque[str] = deque(maxlen=10000)
        self.metrics = {'received': 0, 'processed': 0, 'invalid': 0, 'duplicates': 0, 'out_of_order': 0, 'dropped': 0}
        self.latest_timestamps = {}

    async def submit(self, raw: dict) -> bool:
        self.metrics['received'] += 1
        try:
            self.queue.put_nowait(raw)
            return True
        except asyncio.QueueFull:
            self.metrics['dropped'] += 1
            return False

    async def run(self, ttl: int):
        while True:
            raw = await self.queue.get()
            try:
                quote = QuoteNormalizer.normalize(raw,
                    exchange=str(raw.get('exchange') or ''),
                    source=str(raw.get('source') or 'configured_provider'),
                    default_status=raw.get('data_status'))
                key = f"{quote.exchange}:{quote.symbol}:{quote.market_timestamp.isoformat()}"
                if key in self.seen:
                    self.metrics['duplicates'] += 1
                    continue
                self.seen.append(key)
                previous = self.latest_timestamps.get(f'{quote.exchange}:{quote.symbol}')
                if previous is not None and quote.market_timestamp < previous:
                    self.metrics['out_of_order'] += 1
                    continue
                await self.quote_cache.set_quote(quote, ttl)
                await self.pubsub.publish(quote)
                await self.connection_manager.broadcast_symbol(quote.symbol, quote_event(quote))
                self.metrics['processed'] += 1
                self.latest_timestamps[f'{quote.exchange}:{quote.symbol}'] = quote.market_timestamp
            except Exception:
                self.metrics['invalid'] += 1
            finally:
                self.queue.task_done()

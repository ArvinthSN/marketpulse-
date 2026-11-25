import json
from datetime import datetime, timezone
from typing import Any


class QuoteCache:
    SCHEMA_VERSION = 1

    def __init__(self, redis_manager):
        self.redis_manager = redis_manager

    @staticmethod
    def quote_key(exchange: str, symbol: str) -> str:
        return f'marketpulse:quote:{exchange.upper()}:{symbol.upper()}'

    async def set_quote(self, quote, ttl: int) -> bool:
        client = self.redis_manager.client
        if not client:
            return False
        payload = quote.model_dump(mode='json')
        payload['schema_version'] = QuoteCache.SCHEMA_VERSION
        try:
            await client.set(self.quote_key(quote.exchange, quote.symbol), json.dumps(payload), ex=ttl)
            return True
        except Exception:
            return False

    async def get_quote(self, exchange: str, symbol: str) -> dict | None:
        client = self.redis_manager.client
        if not client:
            return None
        try:
            value = await client.get(self.quote_key(exchange, symbol))
            return json.loads(value) if value else None
        except Exception:
            return None

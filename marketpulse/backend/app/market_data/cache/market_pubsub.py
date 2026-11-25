import json


class MarketPubSub:
    CHANNEL = 'marketpulse:live:quotes'

    def __init__(self, redis_manager):
        self.redis_manager = redis_manager

    async def publish(self, quote) -> bool:
        client = self.redis_manager.client
        if not client:
            return False
        try:
            payload = quote.model_dump(mode='json')
            await client.publish(self.CHANNEL, json.dumps(payload))
            return True
        except Exception:
            return False

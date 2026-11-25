import os
import pytest


@pytest.mark.skipif(not os.getenv('MARKETPULSE_REDIS_URL'), reason='opt-in Redis integration test')
def test_redis_ping():
    import asyncio
    from app.market_data.cache.redis_client import RedisConnectionManager

    async def verify():
        manager = RedisConnectionManager(os.environ['MARKETPULSE_REDIS_URL'])
        assert await manager.connect()
        await manager.disconnect()

    asyncio.run(verify())

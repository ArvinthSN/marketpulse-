import logging
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class RedisConnectionManager:
    def __init__(self, url: str):
        self.url = url
        self.client: Redis | None = None

    async def connect(self) -> bool:
        try:
            self.client = Redis.from_url(self.url, decode_responses=True, socket_connect_timeout=2, socket_timeout=2)
            await self.client.ping()
            return True
        except Exception as exc:
            logger.warning('Redis unavailable: %s', type(exc).__name__)
            self.client = None
            return False

    async def disconnect(self) -> None:
        if self.client:
            await self.client.aclose()
            self.client = None

    async def health_check(self) -> bool:
        if not self.client:
            return False
        try:
            return await self.client.ping()
        except Exception:
            return False

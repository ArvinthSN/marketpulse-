from app.market_data.cache.redis_client import RedisConnectionManager
from app.market_data.cache.quote_cache import QuoteCache
from app.market_data.cache.market_pubsub import MarketPubSub
from app.market_data.streaming.connection_manager import LiveConnectionManager
from app.market_data.streaming.stream_manager import LiveEventProcessor


redis_manager = None
quote_cache = None
market_pubsub = None
connection_manager = None
event_processor = None


def initialize(settings):
    global redis_manager, quote_cache, market_pubsub, connection_manager, event_processor
    redis_manager = RedisConnectionManager(settings.redis_url)
    quote_cache = QuoteCache(redis_manager)
    market_pubsub = MarketPubSub(redis_manager)
    connection_manager = LiveConnectionManager(settings.market_data_max_connections,
                                               settings.market_data_max_subscriptions)
    event_processor = LiveEventProcessor(quote_cache, market_pubsub, connection_manager)

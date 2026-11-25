from app.market_data.cache.quote_cache import QuoteCache


def test_redis_quote_key():
    assert QuoteCache.quote_key('nasdaq', 'aapl') == 'marketpulse:quote:NASDAQ:AAPL'

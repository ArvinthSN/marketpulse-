from datetime import datetime, timezone
from decimal import Decimal
import pytest
from app.market_data.normalization.quote_normalizer import QuoteNormalizer


def test_quote_normalization_calculates_change():
    quote = QuoteNormalizer.normalize({
        'symbol': 'aapl', 'price': '250.50', 'previous_close': '248.20',
        'volume': '1200000', 'currency': 'usd', 'market_timestamp': datetime(2026, 11, 25, tzinfo=timezone.utc),
        'received_at': datetime(2026, 11, 25, tzinfo=timezone.utc),
    }, exchange='NASDAQ', source='test')
    assert quote.symbol == 'AAPL'
    assert quote.currency == 'USD'
    assert quote.change == Decimal('2.30')


def test_quote_normalization_rejects_missing_price():
    with pytest.raises(ValueError):
        QuoteNormalizer.normalize({'symbol': 'AAPL', 'currency': 'USD',
            'market_timestamp': datetime.now(timezone.utc)}, exchange='NASDAQ', source='test')

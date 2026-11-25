from decimal import Decimal
from datetime import datetime
from app.ingestion.providers.schemas import OHLCVRecord
from app.utils.validation import validate_ohlcv


def test_valid_ohlcv():
    row = OHLCVRecord(timestamp=datetime.utcnow(), open=Decimal('10'), high=Decimal('12'), low=Decimal('9'), close=Decimal('11'), volume=100, currency='USD')
    assert validate_ohlcv(row) == []


def test_invalid_ohlc_relationship():
    row = OHLCVRecord(timestamp=datetime.utcnow(), open=Decimal('10'), high=Decimal('9'), low=Decimal('8'), close=Decimal('11'), volume=100, currency='USD')
    assert validate_ohlcv(row)

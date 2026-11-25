import math
from datetime import datetime
from decimal import Decimal
from app.ingestion.providers.schemas import OHLCVRecord


def validate_ohlcv(record: OHLCVRecord) -> list[str]:
    errors = []
    values = (record.open, record.high, record.low, record.close)
    if any(value is None or not value.is_finite() or value <= 0 for value in values): errors.append('Prices must be finite and positive')
    if record.high < max(record.open, record.close, record.low): errors.append('High is below one or more OHLC values')
    if record.low > min(record.open, record.close, record.high): errors.append('Low is above one or more OHLC values')
    if record.volume < 0: errors.append('Volume must be non-negative')
    if not isinstance(record.timestamp, datetime): errors.append('Timestamp is invalid')
    if len(record.currency) != 3 or not record.currency.isupper(): errors.append('Currency must be a three-letter uppercase code')
    return errors

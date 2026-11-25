from app.ingestion.providers.schemas import OHLCVRecord
from decimal import Decimal
from datetime import datetime


def test_provider_schema_normalizes_values():
    record = OHLCVRecord(timestamp=datetime.utcnow(), open=Decimal('10'), high=Decimal('11'), low=Decimal('9'), close=Decimal('10.5'), volume=100, currency='USD')
    assert record.currency == 'USD'

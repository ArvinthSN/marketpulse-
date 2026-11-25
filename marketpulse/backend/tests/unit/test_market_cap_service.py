from datetime import datetime, timezone
from app.models.entities import Company
from app.analytics.services.market_cap_service import MarketCapService


def test_market_cap_requires_shares():
    company = Company(name='Test', shares_outstanding=None)
    result = MarketCapService().calculate(company, 100, datetime.now(timezone.utc), 'USD')
    assert result.value is None
    assert result.warning == 'missing_price_or_shares_outstanding'


def test_market_cap_calculation_uses_provenance():
    company = Company(name='Test', shares_outstanding=1000,
                      shares_outstanding_source='provider_reported',
                      shares_outstanding_at=datetime.now(timezone.utc))
    result = MarketCapService().calculate(company, 25, datetime.now(timezone.utc), 'USD')
    assert result.value == 25000
    assert result.source == 'provider_reported'

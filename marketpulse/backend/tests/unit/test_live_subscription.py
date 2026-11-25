import pytest
from app.market_data.services.subscription_service import SubscriptionService


def test_subscription_validation_deduplicates():
    assert SubscriptionService.validate(['aapl', 'AAPL', 'msft']) == ['AAPL', 'MSFT']


def test_subscription_validation_rejects_malformed_symbol():
    with pytest.raises(ValueError):
        SubscriptionService.validate(['bad symbol'])

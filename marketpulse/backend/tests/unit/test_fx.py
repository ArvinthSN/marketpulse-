from app.analytics.utils.currency import NullFXRateProvider


def test_identity_fx_rate():
    assert NullFXRateProvider().get_rate('USD', 'USD', __import__('datetime').datetime.utcnow()) == 1.0


def test_missing_fx_rate_is_null():
    from datetime import datetime
    assert NullFXRateProvider().get_rate('INR', 'USD', datetime.utcnow()) is None

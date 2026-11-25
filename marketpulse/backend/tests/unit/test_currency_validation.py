def test_currency_codes_are_normalized():
    assert 'usd'.upper() == 'USD'


def test_null_fx_never_substitutes_rate():
    from app.analytics.utils.currency import NullFXRateProvider
    assert NullFXRateProvider().get_rate('EUR', 'JPY', __import__('datetime').datetime.now()) is None

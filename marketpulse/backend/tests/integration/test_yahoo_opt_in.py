import os
import pytest


@pytest.mark.skipif(os.getenv('MARKETPULSE_YAHOO_INTEGRATION') != '1', reason='opt-in Yahoo connectivity test')
def test_yahoo_can_return_a_quote():
    from app.ingestion.providers.yahoo_provider import YahooProvider
    quote = YahooProvider().get_latest_quote('MSFT')
    assert quote.symbol == 'MSFT'

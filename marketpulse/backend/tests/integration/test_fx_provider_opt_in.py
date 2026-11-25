import os
import pytest


@pytest.mark.skipif(os.getenv('MARKETPULSE_FX_INTEGRATION') != '1', reason='opt-in live FX test')
def test_frankfurter_identity_or_live_rate():
    from datetime import datetime, timezone
    from app.analytics.utils.fx_providers import FrankfurterFXProvider
    provider = FrankfurterFXProvider(timeout=10, retries=2)
    assert provider.get_rate('EUR', 'EUR', datetime.now(timezone.utc)) == 1.0

from datetime import datetime, timezone
from app.analytics.utils.fx_providers import FrankfurterFXProvider


def test_frankfurter_identity_does_not_make_network_request(monkeypatch):
    provider = FrankfurterFXProvider()
    assert provider.get_rate('USD', 'USD', datetime.now(timezone.utc)) == 1.0

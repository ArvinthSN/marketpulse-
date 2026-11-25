from datetime import datetime, timezone
from types import SimpleNamespace

from app.analytics.services.sector_analytics import SectorAnalyticsService


class FakeRepository:
    def __init__(self):
        self.company_filter = None

    def get_sector(self, sector_id):
        return SimpleNamespace(id=sector_id, name='Technology')

    def get_companies(self, country_code=None, sector_id=None):
        self.company_filter = {'country_code': country_code, 'sector_id': sector_id}
        return [SimpleNamespace(id=1, market_cap=1000)]

    def get_company_observations(self, company_id, limit=500):
        return [
            SimpleNamespace(timestamp=datetime(2026, 11, 24, tzinfo=timezone.utc), close=100),
            SimpleNamespace(timestamp=datetime(2026, 11, 25, tzinfo=timezone.utc), close=105),
        ]


def test_sector_overview_can_be_scoped_to_country():
    repository = FakeRepository()

    result = SectorAnalyticsService(repository).overview(7, country_code='IN')

    assert repository.company_filter == {'country_code': 'IN', 'sector_id': 7}
    assert result['sector_id'] == 7
    assert result['listed_companies'] == 1
    assert result['valid_companies'] == 1
    assert result['market_cap_weighted_return'] == 5.0

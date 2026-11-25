from datetime import datetime, timezone
from types import SimpleNamespace

from app.analytics.services.country_analytics import CountryAnalyticsService


class FakeRepository:
    def __init__(self, companies, observations):
        self.companies = companies
        self.observations = observations

    def get_country(self, code):
        return SimpleNamespace(code=code, name='Test Country')

    def get_companies(self, country_code=None):
        return self.companies

    def get_company_observations(self, company_id, limit=500):
        return self.observations.get(company_id, [])


def observation(day, close):
    return SimpleNamespace(
        timestamp=datetime(2026, 11, day, tzinfo=timezone.utc),
        close=close,
    )


def test_country_overview_exposes_coverage_and_latest_observation():
    companies = [
        SimpleNamespace(id=1, market_cap=1000),
        SimpleNamespace(id=2, market_cap=500),
    ]
    repository = FakeRepository(
        companies,
        {
            1: [observation(24, 100), observation(25, 105)],
            2: [observation(25, 50)],
        },
    )

    result = CountryAnalyticsService(repository).overview('TC')

    assert result['data_status'] == 'PARTIAL'
    assert result['coverage'] == {'expected': 2, 'available': 1, 'missing': 1}
    assert result['source_observation_at'] == '2026-11-25T00:00:00+00:00'
    assert result['tracked_companies'] == 2


def test_country_overview_marks_empty_observation_set_unavailable():
    companies = [SimpleNamespace(id=1, market_cap=None)]
    repository = FakeRepository(companies, {})

    result = CountryAnalyticsService(repository).overview('TC')

    assert result['data_status'] == 'UNAVAILABLE'
    assert result['coverage'] == {'expected': 1, 'available': 0, 'missing': 1}
    assert result['source_observation_at'] is None

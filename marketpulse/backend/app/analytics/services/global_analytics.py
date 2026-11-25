from datetime import datetime, timezone
from sqlalchemy import select
from app.models.entities import CompanySymbol
from app.analytics.calculations.breadth import breadth


class GlobalAnalyticsService:
    def __init__(self, repository):
        self.repository = repository

    def overview(self, period: str = '1D', reporting_currency: str = 'USD'):
        companies = self.repository.get_companies(limit=10000)
        returns = []
        active_exchange_ids = set()
        for company in companies:
            observations = self.repository.get_company_observations(company.id, limit=500)
            if len(observations) >= 2:
                current = float(observations[-1].close)
                reference = float(observations[-2].close)
                returns.append(((current - reference) / reference * 100) if reference else None)
            else:
                returns.append(None)
            if company.country_code:
                exchange_ids = self.repository.db.scalars(select(CompanySymbol.exchange_id).where(CompanySymbol.company_id == company.id)).all()
                active_exchange_ids.update(exchange_ids)
        breadth_result = breadth(returns)
        status = 'AVAILABLE' if breadth_result['valid_observation_count'] else 'UNAVAILABLE'
        if 0 < breadth_result['valid_observation_count'] < len(companies):
            status = 'PARTIAL'
        return {
            'market': 'global',
            'period': period,
            'reporting_currency': reporting_currency,
            'calculated_at': datetime.now(timezone.utc),
            'data_status': status,
            'tracked_companies': len(companies),
            'active_exchanges': len(active_exchange_ids),
            'market_breadth': breadth_result,
        }

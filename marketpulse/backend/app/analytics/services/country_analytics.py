from app.analytics.aggregations.country_aggregation import country_returns
from app.analytics.calculations.breadth import breadth


class CountryAnalyticsService:
    def __init__(self, repository):
        self.repository = repository

    def overview(self, country_code: str, period: str = '1D', reporting_currency: str = 'USD'):
        country = self.repository.get_country(country_code)
        if country is None:
            return None
        companies = self.repository.get_companies(country_code=country_code)
        items = []
        for company in companies:
            observations = self.repository.get_company_observations(company.id, limit=500)
            value = None
            if len(observations) >= 2:
                current = float(observations[-1].close)
                reference = float(observations[-2].close)
                value = ((current - reference) / reference * 100) if reference else None
            items.append({'company_id': company.id, 'return_percentage': value, 'market_cap': float(company.market_cap) if company.market_cap is not None else None})
        aggregate = country_returns(items)
        return {
            'country_code': country.code,
            'country_name': country.name,
            'reporting_currency': reporting_currency,
            'market_cap_weighted_return': aggregate['market_cap_weighted'],
            'equal_weighted_return': aggregate['equal_weighted'],
            'total_market_cap': sum(item['market_cap'] for item in items if item['market_cap'] is not None),
            'tracked_companies': len(companies),
            'breadth': breadth([item['return_percentage'] for item in items]),
        }

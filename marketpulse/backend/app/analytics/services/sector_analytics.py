from app.analytics.aggregations.sector_aggregation import weighted_average, equal_weighted
from app.analytics.calculations.breadth import breadth


class SectorAnalyticsService:
    def __init__(self, repository):
        self.repository = repository

    def overview(self, sector_id: int, period: str = '1D', reporting_currency: str = 'USD'):
        sector = self.repository.get_sector(sector_id)
        if sector is None:
            return None
        companies = self.repository.get_companies(sector_id=sector_id)
        items = []
        values = []
        for company in companies:
            observations = self.repository.get_company_observations(company.id, limit=500)
            if not observations:
                continue
            latest = float(observations[-1].close)
            reference = float(observations[-2].close) if len(observations) > 1 else None
            value = ((latest - reference) / reference * 100.0) if reference else None
            if value is not None:
                values.append(value)
            market_cap = float(company.market_cap) if company.market_cap is not None else None
            items.append({'company_id': company.id, 'return_percentage': value, 'market_cap': market_cap})
        valid = [item for item in items if item['return_percentage'] is not None]
        return {
            'sector_id': sector.id,
            'sector_name': sector.name,
            'reporting_currency': reporting_currency,
            'market_cap_weighted_return': weighted_average([(item['market_cap'], item['return_percentage']) for item in items]),
            'equal_weighted_return': equal_weighted(values),
            'total_market_cap': sum(item['market_cap'] for item in valid if item['market_cap'] is not None),
            'total_volume': None,
            'listed_companies': len(companies),
            'valid_companies': len(valid),
            'breadth': breadth([item['return_percentage'] for item in items]),
        }

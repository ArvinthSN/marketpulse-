from datetime import datetime, timezone
from sqlalchemy import select
from app.models.entities import CompanySymbol
from app.analytics.repositories.analytics_repository import AnalyticsRepository
from app.analytics.calculations.returns import performance_for_period
from app.analytics.calculations.volatility import historical_volatility
from app.analytics.calculations.volume import relative_volume


PERIODS = ('1D', '1W', '1M', '3M', '6M', 'YTD', '1Y', '3Y', '5Y', 'ALL')


class CompanyAnalyticsService:
    def __init__(self, repository: AnalyticsRepository):
        self.repository = repository

    def performance(self, company_id: int, reporting_currency: str = 'USD', period: str = '1D', adjusted: bool = True):
        company = self.repository.get_company(company_id)
        if company is None:
            return None
        observations = self.repository.get_company_observations(company_id, adjusted=adjusted)
        symbol = 'UNKNOWN'
        currency = reporting_currency
        if observations:
            symbol_row = self.repository.db.scalar(select(CompanySymbol.symbol).where(CompanySymbol.company_id == company_id).order_by(CompanySymbol.is_primary.desc(), CompanySymbol.id).limit(1))
            if symbol_row:
                symbol = symbol_row
            currency = observations[-1].currency
        calculated_at = datetime.now(timezone.utc)
        now = calculated_at.replace(tzinfo=None)
        records = []
        for row in observations:
            ts = row.timestamp
            if ts.tzinfo is not None:
                ts = ts.replace(tzinfo=None)
            price = row.adjusted_close if adjusted and row.adjusted_close is not None else row.close
            records.append((ts, float(price)))
        if adjusted and observations and all(row.adjusted_close is None for row in observations):
            adjusted = False
        if period != 'ALL' and period not in PERIODS:
            raise ValueError('Unsupported performance period')
        performance = performance_for_period(records, period, now)
        last = observations[-1].timestamp if observations else None
        warnings = [] if observations else ['no_historical_observations']
        available = 1 if performance is not None else 0
        status = 'AVAILABLE' if performance is not None else 'UNAVAILABLE'
        if observations and performance is None:
            status = 'PARTIAL'
            warnings.append('reference_price_unavailable')
        return {
            'company_id': company.id,
            'symbol': symbol,
            'currency': currency,
            'reporting_currency': reporting_currency,
            'performance': {period: performance},
            'price_basis': 'adjusted' if adjusted and records else 'unadjusted',
            'data_quality': {
                'data_status': status,
                'source': 'persisted_historical_data',
                'last_market_observation': last,
                'calculated_at': calculated_at,
                'is_stale': False,
                'coverage': {'expected': 1, 'available': available, 'missing': 1 - available},
                'warnings': warnings,
            },
        }

    def metrics(self, company_id: int, volatility_window: int = 20, volume_window: int = 20):
        company = self.repository.get_company(company_id)
        if company is None:
            return None
        observations = self.repository.get_company_observations(company_id)
        closes = [float(row.close) for row in observations]
        volumes = [float(row.volume) for row in observations]
        historical_volume = volumes[-(volume_window + 1):-1] if len(volumes) > 1 else []
        return {
            'company_id': company_id,
            'current_volume': volumes[-1] if volumes else None,
            'relative_volume': relative_volume(volumes[-1] if volumes else None, historical_volume),
            'volatility_20d': historical_volatility(closes, 20) if volatility_window == 20 else None,
            'volatility_30d': historical_volatility(closes, 30) if volatility_window >= 30 else None,
            'historical_volatility': historical_volatility(closes, volatility_window),
            'annualization_factor': 252.0,
            'price_basis': 'unadjusted',
        }

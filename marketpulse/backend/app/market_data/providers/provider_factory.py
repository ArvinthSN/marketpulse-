from app.core.config import settings
from app.market_data.providers.base import AsyncMarketDataProvider
from app.market_data.providers.licensed_provider import LicensedProviderNotConfigured
from app.market_data.providers.yahoo_provider import YahooSnapshotProvider


class ProviderFactory:
    @staticmethod
    def create() -> AsyncMarketDataProvider:
        provider = settings.market_data_provider.strip().lower()
        if not provider or provider == 'none':
            return LicensedProviderNotConfigured()
        if provider == 'licensed':
            if not settings.market_data_api_key:
                return LicensedProviderNotConfigured()
            return LicensedProviderNotConfigured()
        if provider == 'yahoo':
            return YahooSnapshotProvider()
        return LicensedProviderNotConfigured()

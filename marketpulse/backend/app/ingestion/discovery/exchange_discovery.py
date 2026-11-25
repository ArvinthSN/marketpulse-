import re
from app.ingestion.discovery.schemas import DiscoveredInstrument


class ExchangeInstrumentNormalizer:
    @staticmethod
    def normalize(symbol: str, yahoo_suffix: str | None) -> str:
        cleaned = symbol.strip().upper().replace(' ', '')
        cleaned = re.sub(r'[^A-Z0-9.&/^_-]', '', cleaned)
        if not cleaned:
            raise ValueError('Symbol is empty')
        if yahoo_suffix:
            base = cleaned.split('.')[0]
            return f'{base}.{yahoo_suffix}'
        return cleaned


class ExchangeDiscovery:
    @staticmethod
    def validate(item: DiscoveredInstrument, registry_country_codes: set[str], registry_exchange_codes: set[str]) -> list[str]:
        errors = []
        if len(item.country_code) != 2 or item.country_code not in registry_country_codes:
            errors.append('country_code is invalid or not in registry')
        if item.exchange_code not in registry_exchange_codes:
            errors.append('exchange_code is invalid or not in registry')
        if not item.symbol:
            errors.append('symbol is required')
        if not item.company_name:
            errors.append('company_name is required')
        if item.currency is not None and (len(item.currency) != 3 or not item.currency.isupper()):
            errors.append('currency must be a three-letter uppercase code')
        if item.instrument_type not in {'equity', 'common_stock', 'preferred_stock', 'etf', 'adr'}:
            errors.append('instrument_type is unsupported')
        return errors

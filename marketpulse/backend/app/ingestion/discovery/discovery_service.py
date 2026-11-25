from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.entities import Country, Exchange, InstrumentUniverse
from app.ingestion.discovery.instrument_loader import InstrumentLoader
from app.ingestion.discovery.exchange_discovery import ExchangeDiscovery, ExchangeInstrumentNormalizer
from app.ingestion.discovery.schemas import DiscoveryReport


class DiscoveryService:
    def __init__(self, db: Session):
        self.db = db

    def import_instruments(self, path: str, country_code: str | None = None, exchange_code: str | None = None) -> DiscoveryReport:
        instruments = InstrumentLoader.load(path, country_code, exchange_code)
        countries = set(self.db.scalars(select(Country.code)).all())
        exchanges = self.db.scalars(select(Exchange)).all()
        exchange_by_code = {exchange.code: exchange for exchange in exchanges}
        exchange_codes = set(exchange_by_code)

        report = DiscoveryReport(source=path, exchange_code=exchange_code, country_code=country_code,
                                 generated_at=datetime.now(timezone.utc), completeness='complete_only_for_imported_source')
        report.total_discovered = len(instruments)
        seen = set()

        for item in instruments:
            item.original_symbol = item.symbol.strip()
            exchange = exchange_by_code.get(item.exchange_code)
            if exchange is not None:
                try:
                    item.normalized_symbol = ExchangeInstrumentNormalizer.normalize(item.symbol, exchange.yahoo_suffix)
                except ValueError:
                    item.normalized_symbol = item.symbol

            errors = ExchangeDiscovery.validate(item, countries, exchange_codes)
            if exchange is not None and exchange.country_code != item.country_code:
                errors.append('exchange does not belong to country')
            if errors:
                report.rejected += 1
                continue
            key = (item.exchange_code, item.normalized_symbol)
            if key in seen:
                report.duplicates += 1
                continue
            if not item.active:
                report.rejected += 1
                continue
            seen.add(key)
            existing = self.db.scalar(select(InstrumentUniverse).where(
                InstrumentUniverse.provider == 'import',
                InstrumentUniverse.exchange_id == exchange.id,
                InstrumentUniverse.normalized_symbol == item.normalized_symbol,
            ))
            if existing is None:
                self.db.add(InstrumentUniverse(exchange_id=exchange.id, provider='import',
                    original_symbol=item.original_symbol, normalized_symbol=item.normalized_symbol,
                    company_name=item.company_name, currency=item.currency,
                    instrument_type=item.instrument_type, active=item.active,
                    source=item.source, completeness='partial'))
            else:
                existing.original_symbol = item.original_symbol
                existing.company_name = item.company_name
                existing.currency = item.currency
                existing.instrument_type = item.instrument_type
                existing.active = item.active
                existing.source = item.source
            report.validated += 1
            report.exchange_coverage[item.exchange_code] = report.exchange_coverage.get(item.exchange_code, 0) + 1

        report.completeness = 'partial' if report.validated else 'no_validated_instruments'
        self.db.commit()
        return report

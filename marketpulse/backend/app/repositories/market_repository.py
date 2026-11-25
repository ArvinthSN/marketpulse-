from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.entities import Country, Exchange, Sector, Company, CompanySymbol, HistoricalPrice, IngestionRun, DataQualityEvent


class MarketRepository:
    def __init__(self, db: Session): self.db = db

    def get_sector(self, name: str) -> Sector:
        sector = self.db.scalar(select(Sector).where(Sector.name == name))
        if sector is None:
            sector = Sector(name=name); self.db.add(sector); self.db.flush()
        return sector

    def upsert_company_symbol(self, exchange: Exchange, provider: str, symbol: str, profile_name: str, country_code: str, sector_name: str | None = None) -> tuple[Company, CompanySymbol, bool]:
        existing = self.db.scalar(select(CompanySymbol).join(Exchange).where(CompanySymbol.provider == provider, CompanySymbol.exchange_id == exchange.id, CompanySymbol.symbol == symbol))
        if existing:
            company = self.db.get(Company, existing.company_id)
            if company:
                company.name = profile_name or company.name
                return company, existing, False
        sector = self.get_sector(sector_name) if sector_name else None
        company = Company(name=profile_name, country_code=country_code, sector_id=sector.id if sector else None)
        self.db.add(company); self.db.flush()
        company_symbol = CompanySymbol(company_id=company.id, exchange_id=exchange.id, provider=provider, symbol=symbol, is_primary=True)
        self.db.add(company_symbol); self.db.flush()
        return company, company_symbol, True

    def upsert_history(self, company_symbol: CompanySymbol, records, interval: str, source: str) -> tuple[int, int]:
        inserted = updated = 0
        for record in records:
            existing = self.db.scalar(select(HistoricalPrice).where(HistoricalPrice.company_symbol_id == company_symbol.id,
                HistoricalPrice.timestamp == record.timestamp, HistoricalPrice.interval == interval))
            values = dict(open=record.open, high=record.high, low=record.low, close=record.close, volume=record.volume,
                          currency=record.currency or 'USD', interval=interval, source=source)
            if existing:
                for key, value in values.items(): setattr(existing, key, value)
                updated += 1
            else:
                self.db.add(HistoricalPrice(company_symbol_id=company_symbol.id, timestamp=record.timestamp, **values)); inserted += 1
        return inserted, updated

    def create_run(self, scope_type: str, scope_value: str | None, period: str, interval: str) -> IngestionRun:
        run = IngestionRun(scope_type=scope_type, scope_value=scope_value, period=period, interval=interval)
        self.db.add(run); self.db.flush(); return run

    def latest_history_timestamp(self, company_symbol: CompanySymbol, interval: str):
        return self.db.scalar(select(HistoricalPrice.timestamp).where(
            HistoricalPrice.company_symbol_id == company_symbol.id,
            HistoricalPrice.interval == interval,
        ).order_by(HistoricalPrice.timestamp.desc()).limit(1))

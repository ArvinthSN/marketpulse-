from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.entities import Company, CompanySymbol, HistoricalPrice, Sector, Country, Exchange, FXRateSnapshot


class AnalyticsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_company(self, company_id: int) -> Company | None:
        return self.db.get(Company, company_id)

    def get_company_observations(self, company_id: int, start: datetime | None = None, limit: int = 5000, adjusted: bool = False):
        stmt = (select(HistoricalPrice).join(CompanySymbol, CompanySymbol.id == HistoricalPrice.company_symbol_id)
                .where(CompanySymbol.company_id == company_id)
                .where(HistoricalPrice.interval == '1d')
                .order_by(HistoricalPrice.timestamp.desc()).limit(limit))
        if start is not None:
            stmt = stmt.where(HistoricalPrice.timestamp >= start)
        rows = list(self.db.scalars(stmt).all())
        return list(reversed(rows))

    def get_companies(self, country_code: str | None = None, sector_id: int | None = None, exchange_code: str | None = None, limit: int = 1000, offset: int = 0):
        stmt = select(Company)
        if country_code:
            stmt = stmt.where(Company.country_code == country_code.upper())
        if sector_id:
            stmt = stmt.where(Company.sector_id == sector_id)
        if exchange_code:
            stmt = stmt.join(CompanySymbol, CompanySymbol.company_id == Company.id).join(Exchange, Exchange.id == CompanySymbol.exchange_id).where(Exchange.code == exchange_code.upper()).distinct()
        return list(self.db.scalars(stmt.order_by(Company.id).limit(limit).offset(offset)).all())

    def get_sector(self, sector_id: int):
        return self.db.get(Sector, sector_id)

    def get_country(self, country_code: str):
        return self.db.scalar(select(Country).where(Country.code == country_code.upper()))

    def latest_fx_rate(self, base_currency: str, quote_currency: str, as_of: datetime):
        if base_currency == quote_currency:
            return 1.0
        return self.db.scalar(select(FXRateSnapshot.rate).where(
            FXRateSnapshot.base_currency == base_currency,
            FXRateSnapshot.quote_currency == quote_currency,
            FXRateSnapshot.observed_at <= as_of,
        ).order_by(FXRateSnapshot.observed_at.desc()).limit(1))

    def get_batch_observations(self, company_ids: list[int], limit_per_company: int = 500):
        if not company_ids:
            return {}
        stmt = (select(HistoricalPrice, CompanySymbol.company_id).join(CompanySymbol, CompanySymbol.id == HistoricalPrice.company_symbol_id)
                .where(CompanySymbol.company_id.in_(company_ids), HistoricalPrice.interval == '1d')
                .order_by(HistoricalPrice.timestamp.desc()))
        rows = list(self.db.execute(stmt).all())
        grouped: dict[int, list] = {company_id: [] for company_id in company_ids}
        for row, company_id in rows:
            if len(grouped[company_id]) < limit_per_company:
                grouped[company_id].append(row)
        return {company_id: list(reversed(observations)) for company_id, observations in grouped.items()}

    def get_exchange_ids_batch(self, company_ids: list[int]) -> dict[int, list[int]]:
        if not company_ids:
            return {}
        rows = self.db.execute(select(CompanySymbol.company_id, CompanySymbol.exchange_id).where(
            CompanySymbol.company_id.in_(company_ids)
        ).distinct()).all()
        grouped = {company_id: [] for company_id in company_ids}
        for company_id, exchange_id in rows:
            grouped[company_id].append(exchange_id)
        return grouped

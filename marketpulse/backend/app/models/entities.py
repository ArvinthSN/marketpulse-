from datetime import datetime
from decimal import Decimal
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base


def utcnow() -> datetime:
    return datetime.utcnow()


class Country(Base):
    __tablename__ = 'countries'
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(2), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), nullable=False)
    exchanges: Mapped[list['Exchange']] = relationship(back_populates='country')


class Exchange(Base):
    __tablename__ = 'exchanges'
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    country_code: Mapped[str] = mapped_column(ForeignKey('countries.code', onupdate='CASCADE'), index=True)
    yahoo_suffix: Mapped[str | None] = mapped_column(String(20))
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    country: Mapped[Country] = relationship(back_populates='exchanges')


class Sector(Base):
    __tablename__ = 'sectors'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)


class Company(Base):
    __tablename__ = 'companies'
    id: Mapped[int] = mapped_column(primary_key=True)
    country_code: Mapped[str | None] = mapped_column(ForeignKey('countries.code'), index=True)
    sector_id: Mapped[int | None] = mapped_column(ForeignKey('sectors.id'), index=True)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    short_name: Mapped[str | None] = mapped_column(String(300))
    website: Mapped[str | None] = mapped_column(String(500))
    market_cap: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    isin: Mapped[str | None] = mapped_column(String(20), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)


class CompanySymbol(Base):
    __tablename__ = 'company_symbols'
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey('companies.id', ondelete='CASCADE'), index=True)
    exchange_id: Mapped[int] = mapped_column(ForeignKey('exchanges.id', ondelete='CASCADE'), index=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    symbol: Mapped[str] = mapped_column(String(50), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    __table_args__ = (UniqueConstraint('provider', 'exchange_id', 'symbol', name='uq_provider_exchange_symbol'),)


class HistoricalPrice(Base):
    __tablename__ = 'historical_prices'
    id: Mapped[int] = mapped_column(primary_key=True)
    company_symbol_id: Mapped[int] = mapped_column(ForeignKey('company_symbols.id', ondelete='CASCADE'), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    open: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    high: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    low: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    close: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    volume: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    interval: Mapped[str] = mapped_column(String(20), nullable=False)
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    __table_args__ = (UniqueConstraint('company_symbol_id', 'timestamp', 'interval', name='uq_symbol_timestamp_interval'), Index('ix_history_symbol_timestamp', 'company_symbol_id', 'timestamp'))


class MarketSnapshot(Base):
    __tablename__ = 'market_snapshots'
    id: Mapped[int] = mapped_column(primary_key=True)
    exchange_id: Mapped[int] = mapped_column(ForeignKey('exchanges.id', ondelete='CASCADE'), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    metadata_json: Mapped[str | None] = mapped_column(Text)


class IngestionRun(Base):
    __tablename__ = 'ingestion_runs'
    id: Mapped[int] = mapped_column(primary_key=True)
    scope_type: Mapped[str] = mapped_column(String(20), nullable=False)
    scope_value: Mapped[str | None] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default='running', index=True)
    period: Mapped[str | None] = mapped_column(String(20))
    interval: Mapped[str | None] = mapped_column(String(20))
    successful: Mapped[int] = mapped_column(Integer, default=0)
    failed: Mapped[int] = mapped_column(Integer, default=0)
    inserted: Mapped[int] = mapped_column(Integer, default=0)
    updated: Mapped[int] = mapped_column(Integer, default=0)
    rejected: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
    error_summary: Mapped[str | None] = mapped_column(Text)


class DataQualityEvent(Base):
    __tablename__ = 'data_quality_events'
    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[int | None] = mapped_column(ForeignKey('ingestion_runs.id', ondelete='SET NULL'), index=True)
    company_symbol_id: Mapped[int | None] = mapped_column(ForeignKey('company_symbols.id', ondelete='SET NULL'))
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class InstrumentUniverse(Base):
    __tablename__ = 'instrument_universes'
    id: Mapped[int] = mapped_column(primary_key=True)
    exchange_id: Mapped[int] = mapped_column(ForeignKey('exchanges.id', ondelete='CASCADE'), index=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    original_symbol: Mapped[str] = mapped_column(String(50), nullable=False)
    normalized_symbol: Mapped[str] = mapped_column(String(50), nullable=False)
    company_name: Mapped[str] = mapped_column(String(300), nullable=False)
    currency: Mapped[str | None] = mapped_column(String(3))
    instrument_type: Mapped[str] = mapped_column(String(30), default='equity', nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    source: Mapped[str] = mapped_column(String(500), nullable=False)
    discovered_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    completeness: Mapped[str] = mapped_column(String(30), default='partial', nullable=False)
    __table_args__ = (UniqueConstraint('provider', 'exchange_id', 'normalized_symbol', name='uq_universe_provider_exchange_symbol'),)


class IngestionItem(Base):
    __tablename__ = 'ingestion_items'
    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey('ingestion_runs.id', ondelete='CASCADE'), index=True)
    company_symbol_id: Mapped[int | None] = mapped_column(ForeignKey('company_symbols.id', ondelete='SET NULL'), index=True)
    symbol: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default='pending', index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    next_attempt_at: Mapped[datetime | None] = mapped_column(DateTime)
    last_error: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
    __table_args__ = (UniqueConstraint('run_id', 'symbol', name='uq_ingestion_run_symbol'),)

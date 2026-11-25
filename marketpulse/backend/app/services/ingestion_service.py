from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Exchange, DataQualityEvent, InstrumentUniverse, IngestionItem, IngestionRun
from app.registry.synchronizer import sync_registry
from app.ingestion.providers.base import MarketDataProvider
from app.ingestion.providers.exceptions import ProviderError
from app.repositories.market_repository import MarketRepository
from app.utils.validation import validate_ohlcv
from app.utils.retry import retry_with_backoff


class IngestionService:
    def __init__(self, db: Session, provider: MarketDataProvider, max_attempts: int = 3):
        self.db = db
        self.provider = provider
        self.repo = MarketRepository(db)
        self.max_attempts = max_attempts

    def run_exchange(self, exchange_code: str, limit: int = 100, period: str = '1y', interval: str = '1d'):
        sync_registry(self.db)
        exchange = self.db.scalar(select(Exchange).where(
            Exchange.code == exchange_code.upper(), Exchange.enabled.is_(True)
        ))
        if exchange is None:
            raise ValueError(f'Unknown or disabled exchange: {exchange_code}')
        run = self.repo.create_run('exchange', exchange.code, period, interval)
        self.db.commit()
        return self._process_run(run, exchange, limit, period, interval)

    def resume_run(self, run_id: int):
        run = self.db.get(IngestionRun, run_id)
        if run is None:
            raise ValueError(f'Ingestion run not found: {run_id}')
        if run.scope_type != 'exchange' or not run.scope_value:
            raise ValueError('Only exchange-scoped interrupted runs can be resumed')
        exchange = self.db.scalar(select(Exchange).where(Exchange.code == run.scope_value))
        if exchange is None:
            raise ValueError(f'Exchange not found: {run.scope_value}')
        run.status = 'running'
        run.finished_at = None
        self.db.commit()
        return self._process_run(run, exchange, 10000, run.period or '1y', run.interval or '1d')

    def _process_run(self, run, exchange, limit, period, interval):
        try:
            universes = self.db.scalars(select(InstrumentUniverse).where(
                InstrumentUniverse.exchange_id == exchange.id,
                InstrumentUniverse.active.is_(True),
            ).order_by(InstrumentUniverse.normalized_symbol).limit(limit)).all()
            if not universes:
                raise ProviderError('No maintained instrument universe is configured for this exchange')

            for universe in universes:
                symbol = universe.normalized_symbol
                item = self.db.scalar(select(IngestionItem).where(
                    IngestionItem.run_id == run.id, IngestionItem.symbol == symbol
                ))
                if item is None:
                    item = IngestionItem(run_id=run.id, symbol=symbol, status='pending')
                    self.db.add(item)
                    self.db.flush()
                if item.status == 'success':
                    continue

                item.status = 'running'
                item.started_at = datetime.utcnow()
                item.attempts += 1
                self.db.commit()

                try:
                    profile, records = retry_with_backoff(
                        lambda: (
                            self.provider.get_company_profile(symbol),
                            self.provider.get_history(symbol, period, interval),
                        ),
                        max_attempts=self.max_attempts,
                        base_delay=0.5,
                        jitter_ratio=0.25,
                        retryable_exceptions=(ProviderError,),
                    )
                    _, company_symbol, _ = self.repo.upsert_company_symbol(
                        exchange, 'yahoo', symbol, profile.name,
                        exchange.country_code, profile.sector,
                    )
                    item.company_symbol_id = company_symbol.id

                    latest = self.repo.latest_history_timestamp(company_symbol, interval)
                    accepted = []
                    for record in records:
                        if latest is not None and record.timestamp <= latest:
                            continue
                        errors = validate_ohlcv(record)
                        if errors:
                            run.rejected += 1
                            self.db.add(DataQualityEvent(
                                run_id=run.id, company_symbol_id=company_symbol.id,
                                event_type='ohlcv_validation', severity='warning',
                                message='; '.join(errors), payload=str(record.model_dump()),
                            ))
                        else:
                            accepted.append(record)

                    inserted, updated = self.repo.upsert_history(
                        company_symbol, accepted, interval, 'yahoo'
                    )
                    run.inserted += inserted
                    run.updated += updated
                    run.successful += 1
                    item.status = 'success'
                    item.finished_at = datetime.utcnow()
                    item.last_error = None
                    item.next_attempt_at = None
                except ProviderError as exc:
                    run.failed += 1
                    item.status = 'failed'
                    item.finished_at = datetime.utcnow()
                    item.last_error = str(exc)
                    self.db.add(DataQualityEvent(
                        run_id=run.id, company_symbol_id=item.company_symbol_id,
                        event_type='provider_error', severity='error',
                        message=str(exc), payload=f'attempts={item.attempts}',
                    ))
                self.db.commit()

            run.status = 'completed' if run.failed == 0 else 'partial'
            run.finished_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(run)
            return run
        except Exception as exc:
            run.status = 'failed'
            run.error_summary = str(exc)
            run.finished_at = datetime.utcnow()
            self.db.commit()
            raise

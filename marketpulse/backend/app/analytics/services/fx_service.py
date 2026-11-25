from datetime import datetime, timedelta, timezone
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import FXRateSnapshot
from app.analytics.utils.currency import FXRateProvider


class FXService:
    def __init__(self, db: Session, provider: FXRateProvider, stale_days: int = 7):
        self.db = db
        self.provider = provider
        self.stale_days = stale_days

    def get_rate(self, base_currency: str, quote_currency: str, timestamp: datetime):
        base = base_currency.upper()
        quote = quote_currency.upper()
        if base == quote:
            return Decimal('1'), timestamp, 'identity', False

        observed_at = timestamp.replace(tzinfo=timezone.utc) if timestamp.tzinfo is None else timestamp.astimezone(timezone.utc)
        persisted = self.db.scalar(select(FXRateSnapshot).where(
            FXRateSnapshot.base_currency == base,
            FXRateSnapshot.quote_currency == quote,
            FXRateSnapshot.observed_at <= observed_at,
        ).order_by(FXRateSnapshot.observed_at.desc()).limit(1))

        if persisted:
            stale = observed_at - persisted.observed_at.replace(tzinfo=timezone.utc) > timedelta(days=self.stale_days)
            return persisted.rate, persisted.observed_at, persisted.source, stale

        live_rate = self.provider.get_rate(base, quote, observed_at)
        if live_rate is None:
            return None, None, None, True
        rate = Decimal(str(live_rate))
        snapshot = FXRateSnapshot(base_currency=base, quote_currency=quote, rate=rate,
                                  observed_at=observed_at, source='frankfurter')
        self.db.add(snapshot)
        self.db.commit()
        return rate, observed_at, 'frankfurter', False

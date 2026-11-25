from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from math import isfinite

from app.market_data.schemas.quote import NormalizedQuote, QuoteDataStatus


class QuoteNormalizer:
    @staticmethod
    def normalize(raw: dict, exchange: str, source: str, company_id: int | None = None,
                  default_status: QuoteDataStatus = QuoteDataStatus.SNAPSHOT,
                  delay_seconds: int = 0) -> NormalizedQuote:
        symbol = str(raw.get('symbol') or '').strip().upper()
        currency = str(raw.get('currency') or '').strip().upper()
        if not symbol or len(currency) != 3:
            raise ValueError('symbol and three-letter currency are required')

        def decimal_value(value):
            if value is None:
                return None
            try:
                parsed = Decimal(str(value))
            except (InvalidOperation, ValueError, TypeError):
                return None
            if not parsed.is_finite() or parsed <= 0:
                return None
            return parsed

        price = decimal_value(raw.get('price'))
        previous_close = decimal_value(raw.get('previous_close'))
        if price is None:
            raise ValueError('valid positive price is required')

        change = None
        change_percentage = None
        if previous_close is not None:
            change = price - previous_close
            if previous_close != 0:
                change_percentage = change / previous_close * Decimal('100')

        market_timestamp = raw.get('market_timestamp')
        if isinstance(market_timestamp, datetime):
            timestamp = market_timestamp
        elif isinstance(market_timestamp, str):
            timestamp = datetime.fromisoformat(market_timestamp.replace('Z', '+00:00'))
        else:
            raise ValueError('market_timestamp is required')
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        timestamp = timestamp.astimezone(timezone.utc)

        received_at = raw.get('received_at')
        if not isinstance(received_at, datetime):
            received_at = datetime.now(timezone.utc)
        elif received_at.tzinfo is None:
            received_at = received_at.replace(tzinfo=timezone.utc)
        else:
            received_at = received_at.astimezone(timezone.utc)

        try:
            volume = max(0, int(raw.get('volume') or 0))
        except (TypeError, ValueError):
            volume = 0

        return NormalizedQuote(symbol=symbol, company_id=company_id, exchange=exchange.upper(),
            price=price, previous_close=previous_close, change=change,
            change_percentage=change_percentage, volume=volume, currency=currency,
            source=source, market_timestamp=timestamp, received_at=received_at,
            data_delay_seconds=max(0, delay_seconds), data_status=default_status)

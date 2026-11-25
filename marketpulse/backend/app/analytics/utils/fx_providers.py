import random
import time
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import httpx

from app.analytics.utils.currency import FXRateProvider


class FrankfurterFXProvider(FXRateProvider):
    """Public ECB reference-rate provider via Frankfurter API.

    The API is suitable for reference/corporate analytics, not guaranteed live
    trading FX. Availability and terms are provider responsibility.
    """

    def __init__(self, timeout: float = 10.0, retries: int = 3, base_url: str = 'https://api.frankfurter.app'):
        self.timeout = timeout
        self.retries = retries
        self.base_url = base_url.rstrip('/')

    def get_rate(self, base_currency: str, quote_currency: str, timestamp: datetime) -> float | None:
        base = base_currency.upper()
        quote = quote_currency.upper()
        if base == quote:
            return 1.0
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        date = timestamp.astimezone(timezone.utc).date().isoformat()
        url = f'{self.base_url}/{date}'

        last_error: Exception | None = None
        for attempt in range(self.retries):
            try:
                response = httpx.get(url, params={'from': base, 'to': quote}, timeout=self.timeout)
                response.raise_for_status()
                payload = response.json()
                rate = payload.get('rates', {}).get(quote)
                if rate is None:
                    return None
                try:
                    decimal_rate = Decimal(str(rate))
                except (InvalidOperation, ValueError):
                    return None
                if decimal_rate <= 0:
                    return None
                return float(decimal_rate)
            except (httpx.TimeoutException, httpx.HTTPError) as exc:
                last_error = exc
                if attempt + 1 < self.retries:
                    delay = min(8.0, 0.5 * (2 ** attempt))
                    time.sleep(delay * random.uniform(0.75, 1.25))
        raise RuntimeError(f'FX provider request failed after {self.retries} attempts') from last_error

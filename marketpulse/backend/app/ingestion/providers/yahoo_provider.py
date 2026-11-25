import math
import time
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import pandas as pd
import yfinance as yf
from app.core.config import settings
from app.ingestion.providers.base import MarketDataProvider
from app.ingestion.providers.exceptions import ProviderError, ProviderTimeoutError, UnsupportedSymbolError, RateLimitError
from app.ingestion.providers.schemas import CompanyProfile, OHLCVRecord, QuoteRecord


class YahooProvider(MarketDataProvider):
    def __init__(self):
        self.timeout = settings.yahoo_timeout_seconds
        self.retries = settings.yahoo_retries

    def discover_companies(self, exchange_code: str, limit: int) -> list[str]:
        raise ProviderError('Exchange discovery is not guaranteed for Yahoo Finance; provide a maintained instrument list or use supported screener/search data')

    def get_company_profile(self, symbol: str) -> CompanyProfile:
        ticker = yf.Ticker(symbol)
        try:
            info = ticker.get_info(timeout=self.timeout)
        except Exception as exc:
            if '429' in str(exc): raise RateLimitError(str(exc))
            raise ProviderError(f'Unable to retrieve profile for {symbol}: {exc}') from exc
        if not info:
            raise UnsupportedSymbolError(f'No profile data returned for {symbol}')
        market_cap = info.get('marketCap')
        try:
            market_cap = Decimal(str(market_cap)) if market_cap is not None and math.isfinite(float(market_cap)) else None
        except (InvalidOperation, ValueError, TypeError): market_cap = None
        return CompanyProfile(name=str(info.get('longName') or info.get('shortName') or symbol), short_name=info.get('shortName'),
                              sector=info.get('sector'), website=info.get('website'), market_cap=market_cap)

    def get_history(self, symbol: str, period: str = '1y', interval: str = '1d') -> list[OHLCVRecord]:
        last_error = None
        for attempt in range(self.retries):
            try:
                frame = yf.Ticker(symbol).history(period=period, interval=interval, timeout=self.timeout, auto_adjust=False)
                if frame is None or frame.empty:
                    raise UnsupportedSymbolError(f'No historical data returned for {symbol}')
                records = []
                for ts, row in frame.iterrows():
                    try:
                        values = [float(row[c]) for c in ('Open','High','Low','Close')]
                        volume = float(row.get('Volume', 0) or 0)
                        if not all(math.isfinite(v) for v in values) or not math.isfinite(volume):
                            continue
                        timestamp = ts.to_pydatetime()
                        if timestamp.tzinfo is not None: timestamp = timestamp.astimezone(timezone.utc).replace(tzinfo=None)
                        adjusted_close = None
                        if 'Adj Close' in frame.columns:
                            adjusted_value = row.get('Adj Close')
                            if adjusted_value is not None:
                                try:
                                    adjusted_close = Decimal(str(adjusted_value))
                                    if adjusted_close <= 0:
                                        adjusted_close = None
                                except (InvalidOperation, ValueError):
                                    adjusted_close = None
                        records.append(OHLCVRecord(timestamp=timestamp, open=Decimal(str(row['Open'])), high=Decimal(str(row['High'])),
                            low=Decimal(str(row['Low'])), close=Decimal(str(row['Close'])), adjusted_close=adjusted_close,
                            volume=int(max(volume, 0)), currency=''))
                    except (KeyError, ValueError, InvalidOperation):
                        continue
                if not records:
                    raise ProviderError(f'All rows for {symbol} were malformed or missing')
                currency = records_currency = None
                try:
                    records_currency = yf.Ticker(symbol).fast_info.get('currency')
                except Exception:
                    pass
                for record in records:
                    record.currency = records_currency or 'USD'
                return records
            except (UnsupportedSymbolError, ProviderError) as exc:
                last_error = exc
                if attempt + 1 < self.retries: time.sleep(settings.yahoo_rate_limit_delay_seconds * (attempt + 1))
        raise last_error or ProviderError(f'History retrieval failed for {symbol}')

    def get_latest_quote(self, symbol: str) -> QuoteRecord:
        ticker = yf.Ticker(symbol)
        price = None
        currency = None
        timestamp = None
        try:
            fast_info = ticker.fast_info
            price = fast_info.get('last_price')
            currency = fast_info.get('currency')
        except Exception:
            pass
        if price is None:
            try:
                frame = ticker.history(period='5d', interval='1d', timeout=self.timeout, auto_adjust=False)
                if frame is not None and not frame.empty:
                    price = frame.iloc[-1]['Close']
                    timestamp = frame.index[-1].to_pydatetime()
            except Exception as exc:
                raise ProviderError(f'Unable to retrieve quote for {symbol}: {exc}') from exc
        if price is None:
            raise UnsupportedSymbolError(f'No latest quote for {symbol}')
        try:
            price = Decimal(str(price))
        except (InvalidOperation, ValueError, TypeError) as exc:
            raise ProviderError(f'Malformed latest quote for {symbol}') from exc
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        return QuoteRecord(symbol=symbol, price=price, currency=currency, timestamp=timestamp)

    def get_batch_quotes(self, symbols: list[str]) -> list[QuoteRecord]:
        quotes = []
        for symbol in symbols:
            try:
                quotes.append(self.get_latest_quote(symbol))
            except ProviderError:
                continue
        return quotes

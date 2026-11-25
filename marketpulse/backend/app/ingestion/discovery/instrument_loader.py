import csv
import json
from pathlib import Path
from app.ingestion.discovery.schemas import DiscoveredInstrument


class InstrumentLoader:
    @staticmethod
    def load(path: str, default_country: str | None = None, default_exchange: str | None = None) -> list[DiscoveredInstrument]:
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f'Instrument universe file not found: {path}')
        if file_path.suffix.lower() == '.json':
            with file_path.open('r', encoding='utf-8') as handle:
                rows = json.load(handle)
            if isinstance(rows, dict):
                rows = rows.get('instruments') or rows.get('symbols') or []
        elif file_path.suffix.lower() == '.csv':
            with file_path.open('r', encoding='utf-8-sig', newline='') as handle:
                rows = list(csv.DictReader(handle))
        else:
            raise ValueError('Instrument universe must be CSV or JSON')

        instruments = []
        for row in rows:
            country = str(row.get('country_code') or default_country or '').strip().upper()
            exchange = str(row.get('exchange_code') or default_exchange or '').strip().upper()
            symbol = str(row.get('symbol') or row.get('ticker') or '').strip()
            name = str(row.get('company_name') or row.get('name') or '').strip()
            currency = str(row.get('currency') or '').strip().upper() or None
            instrument_type = str(row.get('instrument_type') or 'equity').strip().lower()
            active_value = row.get('active', True)
            active = not str(active_value).strip().lower() in {'0', 'false', 'no', 'inactive'}
            instruments.append(DiscoveredInstrument(
                country_code=country,
                exchange_code=exchange,
                symbol=symbol,
                original_symbol=symbol,
                normalized_symbol=symbol,
                company_name=name,
                currency=currency,
                instrument_type=instrument_type,
                active=active,
                source=str(row.get('source') or file_path.name),
            ))
        return instruments

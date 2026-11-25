from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.entities import HistoricalPrice, CompanySymbol


class LiveQuoteRepository:
    def __init__(self, db: Session):
        self.db = db

    def latest_snapshot(self, symbol: str):
        row = self.db.scalar(select(HistoricalPrice).join(CompanySymbol, CompanySymbol.id == HistoricalPrice.company_symbol_id)
            .where(CompanySymbol.symbol == symbol.upper(), HistoricalPrice.interval == '1d')
            .order_by(HistoricalPrice.timestamp.desc()).limit(1))
        if row is None:
            return None
        return {'symbol': symbol.upper(), 'price': float(row.close), 'currency': row.currency,
                'volume': row.volume, 'market_timestamp': row.timestamp,
                'source': 'persisted_historical_snapshot', 'data_status': 'SNAPSHOT'}

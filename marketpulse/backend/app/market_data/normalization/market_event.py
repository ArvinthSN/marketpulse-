from datetime import datetime
from app.market_data.schemas.quote import NormalizedQuote


def quote_event(quote: NormalizedQuote) -> dict:
    return {'event': 'quote_update', 'data': quote.model_dump(mode='json')}

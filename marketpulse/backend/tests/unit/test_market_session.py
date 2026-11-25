from datetime import datetime, time
from app.market_data.services.market_session_service import MarketSessionService


def test_market_session_open():
    session = MarketSessionService.classify(datetime(2026, 11, 25, 12, 0), time(9, 30), time(16, 0))
    assert session == 'OPEN'


def test_market_session_weekend_closed():
    session = MarketSessionService.classify(datetime(2026, 11, 28, 12, 0), time(9, 30), time(16, 0))
    assert session == 'CLOSED'

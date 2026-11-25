from app.registry.synchronizer import sync_registry
from app.models.entities import Exchange
from app.repositories.market_repository import MarketRepository


def test_company_symbol_upsert_is_duplicate_safe(db_session):
    sync_registry(db_session)
    exchange = db_session.query(Exchange).filter_by(code='NSE').one()
    repo = MarketRepository(db_session)
    company, symbol, created = repo.upsert_company_symbol(exchange, 'yahoo', 'RELIANCE.NS', 'Reliance Industries', 'IN', 'Energy')
    db_session.commit()
    company2, symbol2, created2 = repo.upsert_company_symbol(exchange, 'yahoo', 'RELIANCE.NS', 'Reliance Industries', 'IN', 'Energy')
    db_session.commit()
    assert created is True and created2 is False
    assert company.id == company2.id
    assert symbol.id == symbol2.id

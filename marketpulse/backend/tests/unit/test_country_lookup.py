from fastapi.testclient import TestClient
from sqlalchemy import select


def test_country_exchange_lookup(db_session):
    from app.registry.synchronizer import sync_registry
    sync_registry(db_session)
    from app.models.entities import Country
    country = db_session.scalar(select(Country).where(Country.code == 'IN'))
    assert country is not None

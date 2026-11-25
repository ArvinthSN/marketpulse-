from app.registry.definitions import COUNTRIES, EXCHANGES
from app.registry.synchronizer import validate_registry, sync_registry


def test_registry_has_twenty_countries():
    assert len(COUNTRIES) == 20


def test_registry_validates():
    validate_registry()


def test_registry_sync_is_idempotent(db_session):
    first = sync_registry(db_session)
    second = sync_registry(db_session)
    assert first[0] == 20
    assert second == (0, 0)

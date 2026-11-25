from fastapi.testclient import TestClient


def test_websocket_ping_and_disconnect(db_session):
    from app.main import app
    from app.database.session import get_db

    def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)
    with client.websocket_connect('/api/v1/market/live') as websocket:
        websocket.send_json({'action': 'ping'})
        assert websocket.receive_json() == {'event': 'pong'}
    app.dependency_overrides.clear()

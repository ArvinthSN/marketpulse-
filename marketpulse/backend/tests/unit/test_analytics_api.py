from fastapi.testclient import TestClient
from app.database.session import get_db, Base


def test_analytics_health_routes_exist(db_session):
    from app.main import app

    Base.metadata.create_all(db_session.bind)

    def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)
    response = client.get('/api/v1/analytics/global/overview')
    app.dependency_overrides.clear()
    assert response.status_code == 200


def test_invalid_ranking_metric_is_validated(db_session):
    from app.main import app

    def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)
    response = client.get('/api/v1/analytics/global/top-companies?metric=unknown')
    app.dependency_overrides.clear()
    assert response.status_code == 422

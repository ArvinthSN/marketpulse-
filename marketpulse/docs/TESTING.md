# Testing

## Phase 2 analytics tests

```bash
cd backend
pytest tests/unit/test_analytics_returns.py tests/unit/test_analytics_aggregations.py tests/unit/test_fx.py tests/unit/test_analytics_api.py
pytest
alembic upgrade head
alembic heads
```

Normal CI only uses synthetic fixtures and in-memory SQLite unit tests. It does not depend on Yahoo Finance or PostgreSQL.

## Isolated PostgreSQL integration database

Set `MARKETPULSE_TEST_DATABASE_URL` to a dedicated disposable PostgreSQL database, then run:

```bash
pytest tests/integration/test_postgres_migration.py
alembic upgrade head
alembic downgrade base
alembic upgrade head
```

The integration database must never be production data.

## Docker verification

On a machine with Docker Engine or Docker Desktop:

```bash
cp .env.example .env
docker compose up --build -d
docker compose ps
docker compose exec postgres pg_isready -U marketpulse -d marketpulse
curl http://localhost:8000/health/database
docker compose down
```

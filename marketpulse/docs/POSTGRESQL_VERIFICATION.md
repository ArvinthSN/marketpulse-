# PostgreSQL Verification Guide

Use only a disposable PostgreSQL database for integration tests.

```bash
cd backend
set MARKETPULSE_TEST_DATABASE_URL=postgresql+psycopg://marketpulse:test@localhost:5433/marketpulse_test
alembic upgrade head
pytest tests/integration/test_postgres_phase21.py tests/integration/test_postgres_transactions.py
alembic downgrade base
alembic upgrade head
```

Docker Compose verification:

```bash
cd marketpulse
copy .env.example .env
docker compose up --build -d
docker compose ps
docker compose exec postgres pg_isready -U marketpulse -d marketpulse
curl http://localhost:8000/health/database
docker compose down
```

Docker and PostgreSQL tests must not use production credentials or the production database.

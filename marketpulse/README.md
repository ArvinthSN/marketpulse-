# MARKETPULSE

MARKETPULSE is a Python/FastAPI market intelligence platform for global exchange metadata and market data ingestion.

## Local development (SQLite)

SQLite is the default for local development, so you can run the backend without installing PostgreSQL or Docker.

```powershell
cd marketpulse
Copy-Item .env.example .env
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload
```

The SQLite database file is created at `backend/marketpulse.db` when you run the backend from the `backend` directory.

API: http://localhost:8000/docs

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

## PostgreSQL with Docker (production-like local environment)

```bash
cd marketpulse
cp .env.example .env
docker compose up --build
```

Docker Compose overrides `DATABASE_URL` and runs PostgreSQL plus Redis. For production deployments, use PostgreSQL rather than the local SQLite database.

## CLI

```bash
python -m app.cli sync-registry
python -m app.cli import-universe --file instrument-universe.csv --country IN --exchange NSE
python -m app.cli ingest --exchange NSE --limit 100
python -m app.cli resume-ingestion --run-id 1
python -m app.cli show-ingestion-status
```

Country ingestion is deliberately not claimed until a maintained instrument list is configured. The provider has no guaranteed exchange-wide Yahoo Finance discovery API.

## Important limitations

- SQLite is intended for local development and single-user workflows; PostgreSQL remains the production database.
- Data is not necessarily real-time and no streaming is implemented.
- Yahoo Finance coverage and fields vary by symbol.
- Sector and market capitalization can be missing.
- Exchange discovery requires separate supported search/screener functionality or a maintained instrument list.
- Unit tests use synthetic data and do not require network access.

## Phase 3 live market infrastructure

Live infrastructure supports snapshot-only providers and Redis cache/PubSub. Real-time streaming requires an officially licensed provider. Redis is optional and live endpoints degrade when unavailable.

Use `MARKET_DATA_PROVIDER=none` for normal startup without credentials.

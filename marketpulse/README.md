# MARKETPULSE

MARKETPULSE is a Python/FastAPI/PostgreSQL platform for global exchange metadata and Yahoo Finance market data ingestion.

## Quick start

```bash
cd marketpulse
cp .env.example .env
docker compose up --build
```

API: http://localhost:8000/docs

## Local backend setup

```bash
cd backend
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload
pytest
```

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

- Data is not necessarily real-time and no streaming is implemented.
- Yahoo Finance coverage and fields vary by symbol.
- Sector and market capitalization can be missing.
- Exchange discovery requires separate supported search/screener functionality or a maintained instrument list.
- Unit tests use synthetic data and do not require network access.

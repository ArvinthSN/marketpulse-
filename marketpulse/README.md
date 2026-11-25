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

API: http://localhost:8000/docs

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

## Multi-provider market data

The market-data provider factory supports three licensed REST adapters:

- **EODHD** — global-oriented EOD, delayed quote, and company fundamentals endpoints.
- **Twelve Data** — multi-market quote, time-series, and company profile endpoints.
- **Massive** — US-equity snapshot, aggregate bars, and ticker reference endpoints.

Set credentials in the untracked local `.env` file. Never commit real keys.

```env
EODHD_API_KEY=...
TWELVE_DATA_API_KEY=...
MASSIVE_API_KEY=...
MARKET_DATA_PROVIDER=eodhd
MARKET_DATA_FALLBACK_PROVIDERS=twelvedata,massive
```

The configured primary is tried first; fallback providers are attempted in order when a request fails or returns no quote. REST adapters do not implement WebSocket streaming. Provider entitlements, exchange coverage, delayed/live status, and rate limits depend on each vendor plan. Massive is implemented here for US-equity endpoints and must not be treated as a global-equity provider.

Retries cover network/timeouts, HTTP 429 and 5xx responses with bounded exponential backoff. Historical bars are returned in a common OHLCV dictionary shape; company metadata remains provider-sourced and may have missing fields.

## Important limitations

- SQLite is intended for local development and single-user workflows; PostgreSQL remains the production database.
- Data is not necessarily real-time and no streaming is implemented by these REST adapters.
- Yahoo Finance coverage and fields vary by symbol.
- Sector and market capitalization can be missing.
- Exchange discovery requires supported search/screener functionality or a maintained instrument list.
- Unit tests use mocked provider responses and do not require network access.
- Vendor API plans can restrict endpoint access; a valid key does not guarantee every endpoint is enabled.

Use `MARKET_DATA_PROVIDER=none` for normal startup without credentials.

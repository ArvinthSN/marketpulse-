# MARKETPULSE Frontend

Phase 4 React + TypeScript application.

## Requirements

- Node.js 20.19+ or 22.12+
- MARKETPULSE FastAPI backend running on port 8000

## Local development

```bash
cd marketpulse/frontend
cp .env.example .env
npm install
npm run dev
```

Vite serves the application at http://localhost:5173 and proxies `/api` and `/health` to `http://localhost:8000`.

To use a different backend, set `VITE_API_PROXY_TARGET` in `.env`.

## Production build

```bash
npm run build
npm run preview
```

## Data integrity

The frontend uses the existing FastAPI endpoints. It does not contain production market prices or instrument fixtures. Analytics are labelled as persisted historical observations; live quotes are not implied. Missing or unavailable backend data is shown as unavailable instead of being replaced with fabricated values.

## Current Phase 4 scope

- Frontend foundation, routing, responsive application shell and dark design tokens.
- Typed API client and query hooks.
- Global overview with tracked-company/exchange metrics, market breadth, country registry and sector analytics.
- Explicit loading, error, empty and data-status states.

World map, dedicated country/sector/company drill-down pages and live UI subscriptions are subsequent Phase 4 milestones.

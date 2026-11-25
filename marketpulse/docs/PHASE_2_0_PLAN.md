# Phase 2.0 Implementation Plan

## Existing architecture inspected

- SQLAlchemy synchronous persistence and PostgreSQL-compatible models are used throughout.
- Historical prices are persisted per exchange-specific company symbol, with close, OHLC, volume, currency, interval, and source.
- Companies have country and sector relationships; company symbols separate company identity from exchange/provider symbols.
- Instrument universes support maintained exchange listings and Phase 1.1 discovery source attribution.
- Analytics must consume persisted observations only; Yahoo provider calls remain ingestion responsibilities.
- Existing models do not contain adjusted close, shares outstanding provenance, FX rates, or analytics snapshots.

## Implementation boundaries

1. Add a new Alembic migration for adjusted-close data, shares-outstanding provenance, FX snapshots, analytics snapshots, and analytics job runs.
2. Add pure calculation modules for performance, market cap, volume, volatility, breadth, and weighted/equal aggregations.
3. Add a bounded analytics repository that retrieves only required symbols and observation windows.
4. Add company, sector, country, global, ranking, and breadth services with Pydantic quality metadata.
5. Add `/api/v1/analytics` routes plus authenticated analytics job execution.
6. Add CLI analytics execution/status commands.
7. Add deterministic unit/API tests and a PostgreSQL opt-in integration test. Existing 1.1 tests remain intact.
8. Document formulas, stale/partial behavior, missing FX handling, and production gaps.

## Financial definitions

- Performance uses the latest close and the closest observation on or before the target session date within a configurable tolerance.
- YTD uses the latest session in the prior calendar year as the reference.
- Adjusted close is preferred only when explicitly available; unadjusted close remains the fallback and is reported as price basis.
- Missing observations and missing FX rates are excluded or unavailable, never zero.
- Sector/country weighted returns use valid positive market-cap weights. Equal-weighted returns use valid company observations only.
- Breadth divides valid observations into advancing, declining, and unchanged groups.
- Volatility uses percentage returns and annualization by 252 or a configurable factor.

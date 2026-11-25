# Phase 2.0 Analytics Architecture

Analytics calculations are pure Python modules independent of FastAPI. SQLAlchemy repositories retrieve bounded historical windows and never call market-data providers. Services aggregate company, sector, country, and global views. Pydantic schemas describe stable API contracts.

## Calculation definitions

- 1D: latest close versus prior available close.
- 1W/1M/3M/6M/1Y/3Y/5Y: closest persisted observation on or before the target trading-date minus calendar window, within configurable tolerance.
- YTD: latest persisted close in or closest to December 31 of the prior year.
- ALL: oldest and latest persisted close.
- Adjusted close is used only when the requested basis is adjusted and adjusted observations exist. Unadjusted close is explicitly reported otherwise.

Missing, non-finite, and zero reference prices return `null`; they are never substituted with zero.

## Aggregation definitions

- Equal weighted: sum valid company returns divided by valid company count.
- Market-cap weighted: sum valid company market-cap × return divided by valid market-cap denominator.
- Breadth: advances, declines, and unchanged over valid observations only.
- Relative volume: current volume divided by historical average volume.
- Volatility: population sample standard deviation of daily returns × sqrt(252) × 100, configurable for other calendars.

## FX and freshness

A provider-independent `FXRateProvider` interface must supply persisted or external rates. Different currencies are not summed without conversion. The default null provider only converts identity currencies and returns unavailable for other pairs. Responses include reporting currency, source, observation freshness, coverage, and warnings.

## FX provider implementation

Frankfurter is implemented behind `FXRateProvider`. It uses ECB reference rates, requires no API key, has configurable timeout/retries, and persists successful rates in `exchange_rate_snapshots`. Identity currencies return 1.0. Missing or invalid rates return unavailable. Persisted rates older than the configured stale window are marked stale and are not silently substituted.

## Persistence

The `003_phase20` migration adds adjusted close and shares-outstanding provenance, FX snapshots, analytics snapshots, and analytics job runs. Analytics snapshots should be refreshed or retired through a documented retention job; no automatic retention policy is assumed in this implementation.

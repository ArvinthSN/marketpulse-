# Live Market Data Infrastructure

## Architecture

Live provider events use an asynchronous provider interface, normalized Pydantic quotes, a bounded event queue, Redis cache/PubSub, and WebSocket fan-out. Redis is a transient/latest-state layer; PostgreSQL remains authoritative for persisted snapshots and historical data.

## Provider configuration

- `MARKET_DATA_PROVIDER=none`: live provider unavailable; application still starts.
- `MARKET_DATA_PROVIDER=yahoo`: snapshot-only adapter with no streaming guarantee.
- Licensed provider: configure only against an official provider contract. This repository does not invent credentials or streaming endpoints.

No provider API key is logged or returned through health APIs.

## Redis fallback

If Redis is unavailable, quote cache and Pub/Sub calls fail closed. REST snapshots fall back to persisted `historical_prices` rows where available. WebSocket clients remain informed only through explicit snapshot/status events and are not promised missed Pub/Sub replay.

## Persistence

The default mode is `latest-state-only`. Individual quote events are not written to OHLCV tables. Periodic snapshot and OHLCV aggregation require an explicit future implementation and migration.

## WebSocket

Connect to `/api/v1/market/live`. Optional signed/administrative token support is not enabled unless the provider API key is configured. Subscribe and unsubscribe with `{"action":"subscribe","symbols":["AAPL"]}`. Ping with `{"action":"ping"}`.

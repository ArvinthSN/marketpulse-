# Phase 3.0 Architecture Gap Analysis

## Existing reusable capabilities

- FastAPI application and versioned `/api/v1` route architecture.
- Synchronous SQLAlchemy/PostgreSQL session and repository patterns.
- Country, exchange, company, sector, company-symbol, historical-price, and instrument-universe models.
- Exchange metadata includes timezone and enabled state.
- Existing synchronous Yahoo market-data methods for profiles, history, quotes, and batch quotes.
- Pydantic v2 schemas and provider exception types.
- Analytics services consume persisted historical data without provider calls.
- Administrative X-API-Key authentication mechanism.
- Docker Compose with PostgreSQL and backend services.
- Deterministic unit tests and opt-in provider/PostgreSQL test patterns.

## Missing live infrastructure

- No asynchronous provider interface or provider lifecycle.
- No live quote normalization independent of the historical Yahoo provider.
- No Redis dependency or cache/Pub/Sub abstraction.
- No bounded live event queue or event processor.
- No WebSocket connection/subscription registry.
- No market-session/holiday engine.
- No live REST quote or provider-health endpoints.
- No live health/readiness endpoints.
- No periodic snapshot or live OHLCV persistence policy.
- No live-provider credentials in configuration or secret-safe startup behavior.
- No Redis service in Docker Compose.
- No duplicate/out-of-order event protection in production infrastructure.

## Critical implementation decisions

1. Preserve the existing synchronous ingestion and analytics providers; add a separate asynchronous `market_data` package.
2. Yahoo research snapshots will implement `get_quote/get_quotes/health_check` only unless official streaming capabilities are configured. It is not advertised as real-time streaming.
3. Redis is optional at runtime: cache and Pub/Sub failures must degrade to unavailable or database snapshot fallback, not corrupt PostgreSQL.
4. PostgreSQL remains authoritative for historical snapshots and fallback recovery.
5. Redis Pub/Sub is transient; clients receive only a Redis snapshot and explicit reconnect snapshot behavior.
6. Provider-specific quote formats are isolated behind provider adapters and normalized once.
7. Individual live events are not automatically written to `historical_prices`; only provider-backed snapshot persistence is enabled if configured.

## Design risks

- FastAPI startup currently uses deprecated lifecycle events and has no live component shutdown management.
- Provider streaming cannot be guaranteed without an official licensed provider credential.
- Synchronous SQLAlchemy queries must not run inside provider receive loops or WebSocket delivery loops.
- Redis keys require versioned JSON and TTL to avoid stale payload ambiguity.
- Exchange holidays and sessions require a configurable calendar source; no static global trading calendar should be invented.
- Pydantic/Redis payload timestamps must remain timezone-aware UTC internally.

## Implementation plan

1. Add market-data provider, normalization, cache, streaming, subscription, and session packages.
2. Add Redis configuration and Docker service.
3. Implement a deterministic in-process snapshot provider for contract testing and a Yahoo snapshot provider adapter that clearly reports snapshot/delayed status.
4. Implement Redis quote cache and Pub/Sub through a soft-fallback interface.
5. Implement bounded quote event processing with duplicate and timestamp checks.
6. Implement WebSocket connection/subscription registry with heartbeat, bounded outbound queues, auth token support, and Redis/PostgreSQL snapshot fallback.
7. Implement live REST endpoints and health/readiness checks.
8. Add schema migration only for live snapshot/persistence records if required.
9. Add unit and opt-in Redis/provider/WebSocket/PostgreSQL tests.
10. Update deployment and operational documentation.

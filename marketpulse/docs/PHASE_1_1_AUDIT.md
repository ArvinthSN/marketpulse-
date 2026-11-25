# MARKETPULSE Phase 1.1 Repository Audit

## Existing capabilities

- FastAPI application exposes health, registry, company, history, and ingestion endpoints.
- SQLAlchemy 2.x models cover countries, exchanges, sectors, companies, company symbols, historical prices, snapshots, ingestion runs, and data-quality events.
- An Alembic initial migration creates the core schema.
- A 20-country and 23-exchange registry is synchronized transactionally and is intended to be idempotent.
- A provider interface abstracts profile, history, and quote operations.
- Yahoo Finance integration normalizes profiles and OHLCV values, with basic retries and quote fallback.
- The ingestion service creates audit runs, upserts companies and symbols, validates OHLCV records, and persists history.
- Company and provider-symbol identities are separated in the database.
- Docker Compose and a backend Dockerfile provide a PostgreSQL/API startup path.
- CLI commands exist for registry synchronization and ingestion status.
- Synthetic unit tests and an opt-in Yahoo connectivity test exist.

## Missing functionality

- No configurable, persisted global company universe discovery subsystem.
- CSV/JSON import, source attribution, discovery completeness, and rejection/duplicate reporting are absent.
- Yahoo exchange discovery is an explicit unsupported operation.
- Country ingestion does not resolve a maintained instrument list.
- Retry policy lacks exponential backoff, jitter, typed attempt state, and retry result tracking.
- Ingestion has no resumable item ledger or checkpoint cursor.
- Incremental history ingestion is not based on the latest persisted timestamp.
- Period and interval parsing are not validated centrally.
- Historical ingestion can update all returned rows rather than only a date-window delta.
- Discovery and ingestion outputs are not exposed in dedicated API endpoints.
- PostgreSQL integration tests and migration smoke tests are absent.
- Docker runtime verification has not been performed.
- Operational metrics and alerting guidance are incomplete.

## Critical bugs and incomplete functions

1. `GET /countries/{country_code}/exchanges` uses `db.get(Country, code)`, but `Country.id` is the primary key and `code` is only unique. A valid country lookup can therefore incorrectly return 404.
2. Registry synchronization currently returns only newly inserted counts. It does not report updated or unchanged rows.
3. The ingestion service does not catch unexpected database/provider exceptions per symbol, so one malformed response can turn the run into a global failure and roll back all work.
4. `IngestionService.run_exchange()` cannot use a discovery service or instrument universe, making country/exchange coverage incomplete.
5. Provider `discover_companies()` is a deliberate exception rather than a working provider discovery implementation.
6. CLI ingestion with a country prints a limitation instead of selecting instrument lists for that country.
7. The migration marks `isin` as a unique column through a potentially invalid `sa.Column(..., sa.UniqueConstraint())` construction. The model and migration should explicitly agree on constraint syntax.
8. Several timestamps are naive UTC values. Migration and application code need timezone-aware UTC design or a documented UTC-naive convention.
9. `main.py` uses deprecated FastAPI startup events, though this is not currently a runtime blocker.
10. The CLI status branch has been repaired, but it has no pagination or filtering.

## Database risks

- The migration does not enable or declare all timezone semantics explicitly.
- No migration model for discovery imports or resumable symbol state exists.
- Ingestion counters are mutable aggregate fields only; individual symbol retry history is not persisted.
- A run marked `running` can remain incomplete indefinitely after process interruption.
- Data-quality events are not constrained to unique event identities and can become large without retention controls.
- Batch persistence is row-at-a-time rather than bulk PostgreSQL upsert.
- `Company.name` is not company-identity unique, and cross-provider identity deduplication depends on external import identity rules rather than a durable discovery key.
- SQLite unit tests do not exercise PostgreSQL-specific behavior or transaction semantics.

## Provider limitations

- Yahoo Finance is unofficial and fields or endpoints can change.
- It does not guarantee complete exchange-wide universes.
- Profile data, sector, market capitalization, and history can be missing or delayed.
- Quote fallback can return recent close rather than a real-time quote.
- No real-time streaming is implemented or implied.
- Yahoo screener coverage is not guaranteed to represent every listed instrument.
- Existing retry handling uses linear fixed delays and no jitter or persisted retry count.

## Testing gaps

- Normal CI executes only synthetic SQLite tests.
- There is no isolated PostgreSQL database fixture.
- No migration upgrade/downgrade smoke test exists.
- API country-exchange lookup is untested and currently defective.
- No tests cover discovery CSV/JSON validation, duplicate handling, or source attribution.
- No tests cover retry backoff, partial failure, per-symbol resume, or transaction rollback.
- No test verifies historical price deduplication across repeated runs.
- Docker and PostgreSQL startup/health checks are not automated locally.
- Provider tests do not use a fake provider for deterministic partial failure.

## Implementation plan

1. Fix repository-level correctness defects, beginning with country lookup and migration alignment.
2. Add discovery schemas and provider/loader abstractions for CSV, JSON, Yahoo screener hooks, normalization, ownership validation, de-duplication, and coverage reporting.
3. Add discovery persistence fields or a dedicated discovery audit model so source and completeness are durable.
4. Introduce exponential backoff with capped attempts and jitter, and persist resumable symbol items for interrupted runs.
5. Extend ingestion to calculate incremental periods from the latest stored timestamp and `start/end` windows where supported.
6. Add fake and integration tests for discovery, retries, partial failures, resume behavior, duplicate history, and API lookup.
7. Configure an opt-in PostgreSQL test database and Docker Compose migration smoke verification.
8. Update operational documentation and expose discovery/run observability where practical.

## Phase 1.1 acceptance boundary

Phase 1.1 is complete when discovery is explicit and source-attributed, instrument imports are validated, failed symbols are retryable/resumable, incremental ingestion is deterministic and duplicate-safe, and PostgreSQL/Docker behavior is verified or clearly reported as unavailable in the runtime environment.

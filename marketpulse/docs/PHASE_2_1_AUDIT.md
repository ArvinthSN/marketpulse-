# Phase 2.1 Financial Accuracy and Production Audit

## Scope

Audited Phase 1.1 ingestion/discovery, Phase 2.0 analytics, models, migration 003, API routes, jobs, and tests.

## Critical bugs found

1. Period performance only filters valid positive prices, but duplicate dates and mixed timezone values can be sorted/compared inconsistently.
2. 1D is computed from the final two observations without explicitly suppressing duplicate sessions. This is not guaranteed to be wrong, but duplicate data is not deduplicated.
3. 1W uses seven calendar days rather than a prior available trading session and therefore is not trading-session-accurate.
4. 1M/3M/6M/1Y/3Y/5Y use approximate calendar-day target offsets. The closest prior observation logic exists, but tolerance behavior and timezone handling are not complete or well-covered.
5. YTD finds the closest observation within 31 days of prior December 31, but it may choose a post-year-end observation rather than a session in the prior calendar year. This violates the requirement to use the final prior-year session.
6. ALL uses the oldest and latest observation but has no explicit minimum-history status and can return a result for only two observations.
7. Adjusted and unadjusted price handling is inconsistent: adjusted close is added as a field, but Yahoo ingestion does not populate it. The service silently falls back per row, potentially mixing adjusted and unadjusted observations without a row-level series basis.
8. Sector and country services ignore the requested period and always calculate a one-session return.
9. Sector and country return aggregation accept market-cap values but do not verify local currency or FX normalization.
10. Sector/country total market capitalization sums values without checking currency identity, creating invalid cross-currency totals.
11. Global analytics has no currency normalization and N+1 exchange-symbol queries.
12. Company symbol lookup in company analytics is separate and N+1-prone for aggregate APIs.
13. No stale-price detection is implemented: data-quality metadata always marks `is_stale=false`.
14. `market_cap` and shares fields exist, but no service validates latest price freshness, share timestamp, or stale share counts before calculating market capitalization.
15. The FX abstraction has no real provider, persistence integration, stale rule, retries, timeouts, or reverse-rate support.
16. Analytics snapshots are modeled but no service writes them transactionally.
17. Analytics job endpoint marks a job completed after merely counting companies; it does not calculate analytics or create snapshots and no failure/rollback path exists.
18. Analytics job records have no idempotency key or locking/concurrency protection.
19. Migration 003 is not verified against PostgreSQL and the unique snapshot constraint prevents only exact duplicates, not stale snapshot refresh semantics.
20. API country gainers/losers, country sectors, and global country/sector endpoints perform full nested loops and may create N+1 queries.
21. API global top companies represents country code as currency and does not validate/normalize market capitalization.
22. Analytics API does not validate `period` consistently across all endpoints or validate ISO currency codes.

## Correct assumptions retained

- Historical close is persisted independently by symbol and interval.
- Missing observations must not be transformed into zero.
- Breadth correctly separates only valid observations.
- Provider data is not fetched at API request time.
- Adjusted close must not be mixed silently with unadjusted close.

## Required Phase 2.1 implementation plan

1. Replace approximate period logic with deterministic, deduplicated trading-session selection and explicit YTD prior-year final-session logic.
2. Introduce a price-series mode that requires an entirely adjusted or entirely unadjusted series; expose partial fallback as unavailable or explicit mixed-series warning.
3. Add currency/FX conversion at repository/service boundaries, but never fabricate missing rates.
4. Implement a real HTTP FX provider behind `FXRateProvider`, persist snapshots, retry with backoff, and detect stale observations.
5. Implement a market-cap calculation service that requires positive price, positive shares, matching currency, and freshness metadata.
6. Implement repository batch queries for observations and exchange symbols.
7. Upgrade job service with state transitions, duplicate/in-progress prevention, transaction rollback, and snapshot persistence.
8. Add deterministic reference tests and opt-in PostgreSQL/live FX/Docker checks.

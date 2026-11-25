# Data ingestion

## Phase 1.1 reliability

Exchange symbols are loaded from source-attributed, validated `InstrumentUniverse` records. CSV and JSON imports can be repeated safely. Discovery deduplicates by provider, exchange, and normalized symbol. Coverage is explicitly reported as partial for Yahoo-derived discovery and complete only for the imported source itself.

Failed symbols receive persisted ingestion-item state. Runs can be resumed by the `/api/v1/ingestion/runs/{run_id}/resume` administrative endpoint or `python -m app.cli resume-ingestion --run-id <id>`.

Retries use exponential backoff with random jitter. Historical ingestion filters rows at or before the latest persisted timestamp for the symbol and interval, while the uniqueness constraint prevents duplicate records even if an overlapping window is returned.

Exchange ingestion discovers symbols only when discovery is implemented for that exchange. The Yahoo provider currently expects a separately maintained or future discovery source; it does not fabricate a company universe.

Each run tracks success, failure, inserted, updated, and rejected counts. Invalid OHLCV records generate data-quality events. Corporate actions and gaps are not automatically rejected beyond explicit structural validation.

# Database schema

Core tables: countries, exchanges, sectors, companies, company_symbols, historical_prices, market_snapshots, ingestion_runs, and data_quality_events.

Company identity is separate from exchange-specific provider symbols. Historical uniqueness is `(company_symbol_id, timestamp, interval)`. Financial prices use fixed-scale decimal columns. Repeated upserts update existing values without duplicating records.

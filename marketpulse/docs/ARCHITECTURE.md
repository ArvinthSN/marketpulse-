# Architecture

The pipeline is: Exchange Registry → Provider Interface → Normalization → OHLCV Validation → Idempotent Repository → PostgreSQL → Ingestion Audit.

FastAPI is isolated behind Pydantic request/response schemas. SQLAlchemy owns persistence. Providers implement a provider-independent interface. PostgreSQL stores UTC naive timestamps for normalized data; source timezone semantics are documented by exchange configuration.

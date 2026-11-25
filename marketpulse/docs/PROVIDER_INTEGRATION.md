# Provider integration

`MarketDataProvider` is the provider-independent interface. `YahooProvider` normalizes yfinance fields into Pydantic schemas and implements timeout/retry/rate-limit handling.

Yahoo Finance is an unofficial/public source and may change. It does not guarantee complete exchange symbols, profile fields, update latency, or historical availability. Additional licensed providers can implement the same interface.

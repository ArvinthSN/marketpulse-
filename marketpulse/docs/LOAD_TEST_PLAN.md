# Live Market Load Test Plan

Load testing is not claimed without infrastructure and execution.

1. Start PostgreSQL and Redis through Docker Compose.
2. Run 100, 1,000, and 10,000 concurrent WebSocket clients if host capacity permits.
3. Subscribe each client to a bounded synthetic/provider-fixture symbol set.
4. Submit 1,000/10,000/100,000 events per second through the deterministic event processor.
5. Measure end-to-end receipt-to-WebSocket latency, Redis round-trip latency, queue depth, dropped events, invalid events, memory, and slow-client disconnects.
6. Record database CPU/memory and PostgreSQL write volume; do not enable live OHLCV persistence unless the persistence mode is periodic snapshot.
7. Repeat provider disconnection and Redis disconnection tests.

No successful load result should be reported until commands and output are recorded.

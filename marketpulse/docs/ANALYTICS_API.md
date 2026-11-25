# Analytics API

Analytics endpoints are mounted under `/api/v1/analytics`.

## Company

- `GET /api/v1/analytics/companies/{company_id}/performance?period=1D&reporting_currency=USD&adjusted=true`
- `GET /api/v1/analytics/companies/{company_id}/metrics?volatility_window=20&volume_window=20`

## Sector

- `GET /api/v1/analytics/sectors/{sector_id}/overview`
- `GET /api/v1/analytics/sectors/{sector_id}/companies`
- `GET /api/v1/analytics/sectors/{sector_id}/performance`

## Country

- `GET /api/v1/analytics/countries/{country_code}/overview`
- `GET /api/v1/analytics/countries/{country_code}/performance`
- `GET /api/v1/analytics/countries/{country_code}/sectors`
- `GET /api/v1/analytics/countries/{country_code}/companies`
- `GET /api/v1/analytics/countries/{country_code}/gainers`
- `GET /api/v1/analytics/countries/{country_code}/losers`

## Global and breadth

- `GET /api/v1/analytics/global/overview`
- `GET /api/v1/analytics/global/performance`
- `GET /api/v1/analytics/global/countries`
- `GET /api/v1/analytics/global/sectors`
- `GET /api/v1/analytics/global/top-companies?metric=market_cap`
- `GET /api/v1/analytics/global/market-breadth`
- `GET /api/v1/analytics/market-breadth`

## Administrative jobs

`POST /api/v1/analytics/jobs/run` requires `X-API-Key` and accepts `scope_type`, optional `scope_value`, and comma-separated `periods`.

`GET /api/v1/analytics/jobs/{job_id}` retrieves job status.

## Phase 2.1 response rules

Performance periods use deduplicated positive persisted observations. YTD uses the final valid prior-calendar-year observation. 1W/1M/3M/6M/1Y/3Y/5Y use a target date and the latest valid session on or before it, subject to tolerance. Missing references produce `null`, not zero.

Adjusted close is explicit. If adjusted values are missing, the service reports unadjusted or unavailable rather than silently mixing one series. Reporting currency and FX availability are always exposed.

# API

OpenAPI: `/docs`.

Public read endpoints include countries, exchanges, companies, company history, and ingestion run status.

`POST /api/v1/ingestion/run` requires `X-API-Key`. Set `ADMIN_API_KEY` in configuration.

Example:

```bash
curl -H "X-API-Key: change-me" \
  -H "Content-Type: application/json" \
  -d '{"exchange_code":"NSE","limit":100,"period":"1y","interval":"1d"}' \
  http://localhost:8000/api/v1/ingestion/run
```

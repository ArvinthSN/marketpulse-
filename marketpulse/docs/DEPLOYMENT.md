# Deployment

Copy `.env.example` to `.env`, replace `POSTGRES_PASSWORD` and `ADMIN_API_KEY`, then run `docker compose up --build`. PostgreSQL migrations run before the API container starts.

PostgreSQL data persists in the `postgres_data` Docker volume. Use a managed PostgreSQL service and secret manager for production deployment. This Phase 1 implementation is not a production-readiness claim.

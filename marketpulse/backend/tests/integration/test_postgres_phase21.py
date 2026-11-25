import os
import pytest


@pytest.mark.skipif(not os.getenv('MARKETPULSE_TEST_DATABASE_URL'), reason='isolated PostgreSQL test database not configured')
def test_postgres_phase21_schema():
    from sqlalchemy import create_engine, inspect, text
    url = os.environ['MARKETPULSE_TEST_DATABASE_URL']
    engine = create_engine(url)
    with engine.connect() as connection:
        assert connection.execute(text('SELECT 1')).scalar_one() == 1
    inspector = inspect(engine)
    required = {'exchange_rate_snapshots', 'analytics_snapshots', 'analytics_job_runs', 'historical_prices'}
    assert required.issubset(set(inspector.get_table_names()))

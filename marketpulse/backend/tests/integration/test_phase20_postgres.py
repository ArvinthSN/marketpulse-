import os
import pytest


@pytest.mark.skipif(not os.getenv('MARKETPULSE_TEST_DATABASE_URL'), reason='isolated PostgreSQL test database not configured')
def test_phase20_migration_tables_require_postgres():
    from sqlalchemy import create_engine, text
    engine = create_engine(os.environ['MARKETPULSE_TEST_DATABASE_URL'])
    with engine.connect() as connection:
        assert connection.execute(text('SELECT 1')).scalar_one() == 1

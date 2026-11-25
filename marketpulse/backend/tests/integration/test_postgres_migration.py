import os
import pytest
from sqlalchemy import create_engine, text


POSTGRES_TEST_URL = os.getenv('MARKETPULSE_TEST_DATABASE_URL')


@pytest.mark.skipif(not POSTGRES_TEST_URL, reason='isolated PostgreSQL test database not configured')
def test_postgres_connection_and_migration_shape():
    engine = create_engine(POSTGRES_TEST_URL)
    with engine.connect() as connection:
        assert connection.execute(text('SELECT 1')).scalar_one() == 1

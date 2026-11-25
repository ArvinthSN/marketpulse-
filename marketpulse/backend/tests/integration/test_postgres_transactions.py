import os
import pytest


@pytest.mark.skipif(not os.getenv('MARKETPULSE_TEST_DATABASE_URL'), reason='isolated PostgreSQL test database not configured')
def test_postgres_transaction_rollback():
    from sqlalchemy import create_engine, text
    engine = create_engine(os.environ['MARKETPULSE_TEST_DATABASE_URL'])
    connection = engine.connect()
    transaction = connection.begin()
    connection.execute(text("CREATE TEMP TABLE marketpulse_rollback_check (id integer)"))
    connection.execute(text("INSERT INTO marketpulse_rollback_check VALUES (1)"))
    transaction.rollback()
    connection.close()

import os
import pytest


@pytest.mark.skipif(not os.getenv('MARKETPULSE_TEST_DATABASE_URL'), reason='isolated PostgreSQL test database not configured')
def test_alembic_migration_helpers_are_available():
    from alembic.config import Config
    config = Config('alembic.ini')
    assert config.get_main_option('script_location') == 'migrations'

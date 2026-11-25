from sqlalchemy import text
from app.database.session import engine


def database_health() -> bool:
    try:
        with engine.connect() as connection: connection.execute(text('SELECT 1'))
        return True
    except Exception:
        return False

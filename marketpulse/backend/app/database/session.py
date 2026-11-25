from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings


class Base(DeclarativeBase):
    pass


def create_database_engine(database_url: str) -> Engine:
    """Create a database engine with dialect-specific local settings."""
    if database_url.startswith('sqlite'):
        engine = create_engine(
            database_url,
            connect_args={'check_same_thread': False},
            pool_pre_ping=True,
        )

        # SQLite disables foreign-key enforcement by default. Enable it for
        # every connection so local behavior matches the relational schema.
        @event.listens_for(engine, 'connect')
        def enable_sqlite_foreign_keys(dbapi_connection, _connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute('PRAGMA foreign_keys=ON')
            cursor.close()

        return engine

    return create_engine(database_url, pool_pre_ping=True)


engine = create_database_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

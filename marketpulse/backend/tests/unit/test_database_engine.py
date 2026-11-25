import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.core.config import BACKEND_ROOT, Settings
from app.database.session import create_database_engine


def test_sqlite_engine_enables_foreign_keys(tmp_path):
    database_path = tmp_path / "marketpulse-test.db"
    engine = create_database_engine(f"sqlite:///{database_path.as_posix()}")

    try:
        with engine.begin() as connection:
            connection.execute(text("CREATE TABLE parent (id INTEGER PRIMARY KEY)"))
            connection.execute(text(
                "CREATE TABLE child (id INTEGER PRIMARY KEY, "
                "parent_id INTEGER REFERENCES parent(id))"
            ))

        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
                connection.execute(
                    text("INSERT INTO child (id, parent_id) VALUES (1, 999)")
                )
    finally:
        engine.dispose()


def test_relative_sqlite_url_is_anchored_to_backend_directory():
    settings = Settings(database_url="sqlite:///./marketpulse.db")

    assert settings.database_url == (
        f"sqlite:///{(BACKEND_ROOT / 'marketpulse.db').resolve().as_posix()}"
    )


def test_absolute_sqlite_url_is_preserved(tmp_path):
    database_path = (tmp_path / "custom.db").resolve()
    settings = Settings(database_url=f"sqlite:///{database_path.as_posix()}")

    assert settings.database_url == f"sqlite:///{database_path.as_posix()}"

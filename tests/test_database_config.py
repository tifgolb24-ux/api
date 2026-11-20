import pytest
from pydantic import ValidationError

from app import database
from app.config import Settings


def test_remote_database_connection_failure_does_not_fall_back_to_sqlite(monkeypatch):
    attempted_urls = []

    class UnavailableEngine:
        def connect(self):
            raise ConnectionError("database unavailable")

    def create_engine(url, **kwargs):
        attempted_urls.append(url)
        return UnavailableEngine()

    monkeypatch.setattr(database, "engine", None)
    monkeypatch.setattr(database, "create_engine", create_engine)

    with pytest.raises(ConnectionError, match="database unavailable"):
        database.configure_database("mysql://user:password@mysql.internal:3306/gym")

    assert attempted_urls == [
        "mysql+pymysql://user:password@mysql.internal:3306/gym"
    ]


def test_production_rejects_sqlite_database():
    with pytest.raises(ValidationError, match="persistent database"):
        Settings(app_env="production", database_url="sqlite:///./bisagym.db")

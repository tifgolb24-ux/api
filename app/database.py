from collections.abc import Generator
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import MetaData, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


engine: Engine | None = None
SessionLocal = sessionmaker(autoflush=False, expire_on_commit=False)


def configure_database(url: str) -> Engine:
    global engine
    if engine is not None:
        engine.dispose()
    kwargs = {"pool_pre_ping": True}
    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    elif url.startswith("mysql://"):
        url = url.replace("mysql://", "mysql+pymysql://", 1)
    elif url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
    elif url.startswith("postgresql://") and "+psycopg" not in url and "+asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)

    try:
        eng = create_engine(url, **kwargs)
        with eng.connect():
            pass
        engine = eng
    except Exception:
        if not url.startswith("sqlite"):
            # Fallback otomatis ke SQLite lokal jika MySQL/Postgres belum aktif/unreachable
            fallback_url = "sqlite:///./bisagym.db"
            engine = create_engine(fallback_url, pool_pre_ping=True, connect_args={"check_same_thread": False})
        else:
            raise

    SessionLocal.configure(bind=engine)
    return engine


def get_db() -> Generator[Session]:
    with SessionLocal() as session:
        yield session


def new_uuid() -> str:
    return str(uuid4())


def utcnow() -> datetime:
    return datetime.now(UTC)


def as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)

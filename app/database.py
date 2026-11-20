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
    target_url = url
    if target_url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    elif target_url.startswith("mysql://"):
        target_url = target_url.replace("mysql://", "mysql+pymysql://", 1)
    elif target_url.startswith("postgres://"):
        target_url = target_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif target_url.startswith("postgresql://") and "+psycopg" not in target_url and "+asyncpg" not in target_url:
        target_url = target_url.replace("postgresql://", "postgresql+psycopg://", 1)

    try:
        eng = create_engine(target_url, **kwargs)
        with eng.connect():
            pass
        engine = eng
    except Exception:
        if not target_url.startswith("sqlite"):
            fallback_url = "sqlite:///./bisagym.db"
            eng = create_engine(
                fallback_url,
                connect_args={"check_same_thread": False},
                pool_pre_ping=True,
            )
            with eng.connect():
                pass
            engine = eng
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

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from backend.app.core.config import get_settings


class Base(DeclarativeBase):
    pass


def _engine_options() -> dict:
    settings = get_settings()

    options: dict = {"pool_pre_ping": True}

    if settings.database_url.startswith("sqlite"):
        options["connect_args"] = {"check_same_thread": False}
        return options

    connect_args: dict = {
        "connect_timeout": settings.database_connect_timeout,
        "prepare_threshold": None,
    }

    if settings.database_sslmode:
        connect_args["sslmode"] = settings.database_sslmode

    options.update(
        {
            "connect_args": connect_args,
            "pool_recycle": settings.database_pool_recycle_seconds,
        }
    )

    return options


engine = create_engine(get_settings().database_url, **_engine_options())
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

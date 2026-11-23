import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from core.models import Base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5433/"
    "utility_monitor_db",
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    class_=Session,
)


def get_session() -> Session:
  """Возвращает новую сессию работы с базой данных."""
  return SessionLocal()


def init_db() -> None:
  """Создаёт все таблицы по моделям"""
  Base.metadata.create_all(bind=engine)

  with engine.begin() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb;"))
    conn.execute(
        text(
            "SELECT create_hypertable('measurements', 'time', if_not_exists =>"
            " TRUE);"
        )
    )
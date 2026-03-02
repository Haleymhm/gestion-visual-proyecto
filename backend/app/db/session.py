from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, declarative_base

from app.core.config import settings


engine = create_engine(settings.database_url, echo=False, future=True)

SessionLocal = sessionmaker(
  autocommit=False,
  autoflush=False,
  bind=engine,
  class_=Session,
)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()


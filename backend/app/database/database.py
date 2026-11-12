from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.database.models import Base


# SQLAlchemy controls the six application tables.
database_url = settings.DATABASE_URL or "postgresql://localhost/zipro"
database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

engine = create_engine(database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def initialize_database():
    if not settings.DATABASE_URL:
        raise RuntimeError("DATABASE_URL is missing in backend/.env")

    Base.metadata.create_all(engine)


def fetch_all(query, parameters=()):
    # SQL text comes only from our own code, never directly from the LLM.
    with engine.connect() as connection:
        rows = connection.exec_driver_sql(query, parameters)
        return [dict(row._mapping) for row in rows]


def fetch_one(query, parameters=()):
    rows = fetch_all(query, parameters)
    return rows[0] if rows else None

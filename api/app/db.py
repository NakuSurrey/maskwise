"""
db.py - SQLAlchemy engine, session, and Base for all models.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# one engine for the whole app - manages the pool of postgres connections
engine = create_engine(settings.database_url, pool_pre_ping=True)

# session factory - each request gets its own short-lived session
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# every model (User, ApiKey) inherits from this - it tracks the tables
Base = declarative_base()


def get_db():
    """FastAPI dependency - yields a session, always closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

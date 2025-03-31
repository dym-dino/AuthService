"""
PostgreSQL Connection

Connects to PostgreSQL database using SQLAlchemy.
"""

# --------------------------------------------------------------------------------
# IMPORT LIBRARIES

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# --------------------------------------------------------------------------------
# DATABASE CONFIGURATION

engine = create_engine(settings.POSTGRES_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Base class for models
Base = declarative_base()


# --------------------------------------------------------------------------------
# HELPER FUNCTIONS

# Dependency for route injection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

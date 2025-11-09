"""
Database configuration and session management.

This module provides SQLAlchemy engine, session factory, and dependency injection
for database sessions throughout the application.
"""

import os
from typing import Generator

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase


# Database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@db:5432/frame1_db"
)

# Naming convention for constraints
# This ensures consistent naming across the database schema
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# Create metadata with naming convention
metadata = MetaData(naming_convention=convention)


# Declarative Base class for all models
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    metadata = metadata


# Create SQLAlchemy engine
# echo=True enables SQL query logging (useful for development)
engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=5,  # Connection pool size
    max_overflow=10  # Maximum overflow connections
)

# Create session factory
# autocommit=False: Transactions must be explicitly committed
# autoflush=False: Changes are not automatically flushed to the database
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency injection function for database sessions.
    
    Yields a database session and ensures it's closed after use.
    This function is designed to be used with FastAPI's Depends().
    
    Usage:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Create all tables in the database.
    
    This function should be called during application startup
    to ensure all tables exist. In production, use Alembic migrations instead.
    """
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """
    Drop all tables from the database.
    
    WARNING: This will delete all data. Use with caution.
    Primarily intended for testing and development.
    """
    Base.metadata.drop_all(bind=engine)

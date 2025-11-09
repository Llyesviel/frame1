"""
Base model configuration for all SQLAlchemy models.

This module re-exports the Base class from database.py to provide
a centralized import location for all models.
"""

from app.database import Base

__all__ = ["Base"]

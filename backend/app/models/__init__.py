"""
Models package for the defect management system.

This package contains all SQLAlchemy models for the application.
"""

from app.models.base import Base
from app.models.user import Role, User

__all__ = [
    "Base",
    "Role",
    "User",
]

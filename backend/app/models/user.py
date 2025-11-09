"""
User and Role models for the defect management system.

This module defines the Role and User models with their relationships,
constraints, and indexes as specified in the requirements.
"""

from datetime import datetime, timezone
from typing import List

from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Role(Base):
    """
    Role model representing user roles in the system.
    
    Predefined roles: Engineer, Manager, Observer, Admin
    
    Requirements: 2.1
    """
    __tablename__ = "roles"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Role name (unique)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    
    # Role description
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Relationships
    users: Mapped[List["User"]] = relationship(
        "User",
        back_populates="role",
        lazy="select"
    )
    
    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name='{self.name}')>"


class User(Base):
    """
    User model representing system users.
    
    Each user has a role that determines their permissions in the system.
    
    Requirements: 1.1-1.5, 11.1, 11.2
    """
    __tablename__ = "users"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # User information
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Role relationship
    role_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("roles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=True
    )
    
    # Relationships
    role: Mapped["Role"] = relationship(
        "Role",
        back_populates="users",
        lazy="select"
    )
    
    # Relationships with other models (forward references)
    # These will be populated when other models are created
    created_defects: Mapped[List["Defect"]] = relationship(
        "Defect",
        back_populates="creator",
        foreign_keys="[Defect.created_by]",
        lazy="select"
    )
    
    assigned_defects: Mapped[List["Defect"]] = relationship(
        "Defect",
        back_populates="assignee",
        foreign_keys="[Defect.assigned_to]",
        lazy="select"
    )
    
    comments: Mapped[List["Comment"]] = relationship(
        "Comment",
        back_populates="user",
        lazy="select"
    )
    
    attachments: Mapped[List["Attachment"]] = relationship(
        "Attachment",
        back_populates="uploader",
        lazy="select"
    )
    
    history_logs: Mapped[List["HistoryLog"]] = relationship(
        "HistoryLog",
        back_populates="user",
        lazy="select"
    )
    
    managed_projects: Mapped[List["Project"]] = relationship(
        "Project",
        back_populates="manager",
        lazy="select"
    )
    
    generated_reports: Mapped[List["Report"]] = relationship(
        "Report",
        back_populates="generator",
        lazy="select"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role_id={self.role_id})>"

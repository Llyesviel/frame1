"""
Defect and DefectStatus models for the defect management system.

This module defines the DefectStatus and Defect models with their relationships,
constraints, indexes, and enum types as specified in the requirements.
"""

import enum
from datetime import datetime, timezone, date
from typing import List

from sqlalchemy import String, Integer, Date, DateTime, ForeignKey, Text, Enum, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class PriorityEnum(str, enum.Enum):
    """
    Priority levels for defects.
    
    Requirements: 5.3
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActionTypeEnum(str, enum.Enum):
    """
    Action types for history log entries.
    
    Requirements: 9.3
    """
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    STATUS_CHANGE = "STATUS_CHANGE"
    COMMENT_ADDED = "COMMENT_ADDED"


class DefectStatus(Base):
    """
    DefectStatus model representing possible states of a defect.
    
    Predefined statuses: New, In Progress, Review, Closed, Canceled
    
    Requirements: 6.1-6.2
    """
    __tablename__ = "defect_statuses"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Status name (unique)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    
    # Status description
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Relationships
    defects: Mapped[List["Defect"]] = relationship(
        "Defect",
        back_populates="status",
        lazy="select"
    )
    
    def __repr__(self) -> str:
        return f"<DefectStatus(id={self.id}, name='{self.name}')>"


class Defect(Base):
    """
    Defect model representing issues found in construction projects.
    
    Each defect is associated with a project, optionally with a project stage,
    has a status, priority, creator, and can be assigned to a user.
    
    Requirements: 5.1-5.6, 6.3-6.4, 11.2, 11.4-11.6, 11.9
    """
    __tablename__ = "defects"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Project and stage relationships
    project_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("projects.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    
    stage_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("project_stages.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Defect information
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Priority
    priority: Mapped[PriorityEnum] = mapped_column(
        Enum(PriorityEnum, name="priority_enum", native_enum=False),
        nullable=False,
        index=True
    )
    
    # Status relationship
    status_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("defect_statuses.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    
    # User relationships
    created_by: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    
    assigned_to: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Due date
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    
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
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="defects",
        lazy="select"
    )
    
    stage: Mapped["ProjectStage"] = relationship(
        "ProjectStage",
        back_populates="defects",
        lazy="select"
    )
    
    status: Mapped["DefectStatus"] = relationship(
        "DefectStatus",
        back_populates="defects",
        lazy="select"
    )
    
    creator: Mapped["User"] = relationship(
        "User",
        back_populates="created_defects",
        foreign_keys=[created_by],
        lazy="select"
    )
    
    assignee: Mapped["User"] = relationship(
        "User",
        back_populates="assigned_defects",
        foreign_keys=[assigned_to],
        lazy="select"
    )
    
    comments: Mapped[List["Comment"]] = relationship(
        "Comment",
        back_populates="defect",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    attachments: Mapped[List["Attachment"]] = relationship(
        "Attachment",
        back_populates="defect",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    history_logs: Mapped[List["HistoryLog"]] = relationship(
        "HistoryLog",
        back_populates="defect",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    # Table constraints and indexes
    __table_args__ = (
        # CHECK constraint for title length (max 255 characters)
        CheckConstraint("LENGTH(title) <= 255", name="title_length"),
        # Composite index on (project_id, status_id)
        Index("ix_defects_project_id_status_id", "project_id", "status_id"),
    )
    
    def __repr__(self) -> str:
        return f"<Defect(id={self.id}, title='{self.title}', priority={self.priority.value}, status_id={self.status_id})>"

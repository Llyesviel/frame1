"""
Project and ProjectStage models for the defect management system.

This module defines the Project and ProjectStage models with their relationships,
constraints, and indexes as specified in the requirements.
"""

from datetime import datetime, timezone, date
from typing import List

from sqlalchemy import String, Integer, Date, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Project(Base):
    """
    Project model representing construction projects.
    
    Each project is managed by a single user (manager) and can contain
    multiple stages and defects.
    
    Requirements: 3.1-3.5, 11.3, 11.4
    """
    __tablename__ = "projects"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Project information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Manager relationship
    manager_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    
    # Project dates
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    
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
    manager: Mapped["User"] = relationship(
        "User",
        back_populates="managed_projects",
        lazy="select"
    )
    
    stages: Mapped[List["ProjectStage"]] = relationship(
        "ProjectStage",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    defects: Mapped[List["Defect"]] = relationship(
        "Defect",
        back_populates="project",
        lazy="select"
    )
    
    reports: Mapped[List["Report"]] = relationship(
        "Report",
        back_populates="project",
        lazy="select"
    )
    
    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name='{self.name}', manager_id={self.manager_id})>"


class ProjectStage(Base):
    """
    ProjectStage model representing stages within a construction project.
    
    Each stage belongs to a single project and can contain multiple defects.
    Examples: foundation, framing, finishing, etc.
    
    Requirements: 4.1-4.4, 11.3, 11.4
    """
    __tablename__ = "project_stages"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Project relationship
    project_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Stage information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Stage dates
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    
    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="stages",
        lazy="select"
    )
    
    defects: Mapped[List["Defect"]] = relationship(
        "Defect",
        back_populates="stage",
        lazy="select"
    )
    
    # Composite index on (project_id, name)
    __table_args__ = (
        Index("ix_project_stages_project_id_name", "project_id", "name"),
    )
    
    def __repr__(self) -> str:
        return f"<ProjectStage(id={self.id}, project_id={self.project_id}, name='{self.name}')>"

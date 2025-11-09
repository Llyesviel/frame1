"""
Comment model for the defect management system.

This module defines the Comment model with its relationships,
constraints, and indexes as specified in the requirements.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.defect import Defect
    from app.models.user import User


class Comment(Base):
    """
    Comment model representing user comments on defects.
    
    Each comment is associated with a defect and a user who created it.
    Comments are automatically deleted when the associated defect is deleted.
    
    Requirements: 7.1-7.4, 11.6, 11.10
    """
    __tablename__ = "comments"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    defect_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("defects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    
    # Comment content
    text: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
    
    # Relationships
    defect: Mapped["Defect"] = relationship(
        "Defect",
        back_populates="comments",
        lazy="select"
    )
    
    user: Mapped["User"] = relationship(
        "User",
        back_populates="comments",
        lazy="select"
    )
    
    def __repr__(self) -> str:
        return f"<Comment(id={self.id}, defect_id={self.defect_id}, user_id={self.user_id})>"

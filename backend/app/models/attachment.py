"""
Attachment model for the defect management system.

This module defines the Attachment model with its relationships,
constraints, and indexes as specified in the requirements.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.defect import Defect
    from app.models.user import User


class Attachment(Base):
    """
    Attachment model representing files attached to defects.
    
    Each attachment is associated with a defect and a user who uploaded it.
    Attachments support soft delete functionality through the is_deleted flag.
    Attachments are automatically deleted when the associated defect is deleted.
    
    Requirements: 8.1-8.5, 11.7
    """
    __tablename__ = "attachments"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    defect_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("defects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    uploaded_by: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    
    # File information
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    
    # Soft delete flag
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    
    # Timestamp
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Relationships
    defect: Mapped["Defect"] = relationship(
        "Defect",
        back_populates="attachments",
        lazy="select"
    )
    
    uploader: Mapped["User"] = relationship(
        "User",
        back_populates="attachments",
        lazy="select"
    )
    
    def __repr__(self) -> str:
        return f"<Attachment(id={self.id}, defect_id={self.defect_id}, file_name='{self.file_name}', is_deleted={self.is_deleted})>"

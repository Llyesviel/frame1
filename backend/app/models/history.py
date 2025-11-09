"""
HistoryLog model for the defect management system.

This module defines the HistoryLog model with its relationships,
constraints, and indexes as specified in the requirements.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Integer, DateTime, ForeignKey, Text, Enum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.defect import ActionTypeEnum

if TYPE_CHECKING:
    from app.models.defect import Defect
    from app.models.user import User


class HistoryLog(Base):
    """
    HistoryLog model representing the history of changes to defects.
    
    Each history log entry records an action performed on a defect by a user,
    including the old and new values for the changed field.
    History logs are automatically deleted when the associated defect is deleted.
    
    Requirements: 9.1-9.5, 11.8, 11.11
    """
    __tablename__ = "history_logs"
    
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
    
    # Action information
    action_type: Mapped[ActionTypeEnum] = mapped_column(
        Enum(ActionTypeEnum, name="action_type_enum", native_enum=False),
        nullable=False,
        index=True
    )
    
    # Old and new values (stored as text for flexibility)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Timestamp
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
    
    # Relationships
    defect: Mapped["Defect"] = relationship(
        "Defect",
        back_populates="history_logs",
        lazy="select"
    )
    
    user: Mapped["User"] = relationship(
        "User",
        back_populates="history_logs",
        lazy="select"
    )
    
    # Table constraints and indexes
    __table_args__ = (
        # Composite index on (defect_id, timestamp)
        Index("ix_history_logs_defect_id_timestamp", "defect_id", "timestamp"),
    )
    
    def __repr__(self) -> str:
        return f"<HistoryLog(id={self.id}, defect_id={self.defect_id}, action_type={self.action_type.value})>"

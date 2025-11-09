"""
Models package for the defect management system.

This module exports all model classes, the Base class, and enum types
for convenient importing throughout the application.

Requirements: All model requirements
"""

# Base class
from app.models.base import Base

# User and Role models
from app.models.user import Role, User

# Project models
from app.models.project import Project, ProjectStage

# Defect models and enums
from app.models.defect import DefectStatus, Defect, PriorityEnum, ActionTypeEnum

# Comment model
from app.models.comment import Comment

# Attachment model
from app.models.attachment import Attachment

# History model
from app.models.history import HistoryLog

# Report model
from app.models.report import Report

__all__ = [
    # Base
    "Base",
    # User and Role
    "Role",
    "User",
    # Project
    "Project",
    "ProjectStage",
    # Defect
    "DefectStatus",
    "Defect",
    # Comment
    "Comment",
    # Attachment
    "Attachment",
    # History
    "HistoryLog",
    # Report
    "Report",
    # Enums
    "PriorityEnum",
    "ActionTypeEnum",
]

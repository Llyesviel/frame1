"""
Main FastAPI application entry point.

This module initializes the FastAPI application, sets up database connections,
and configures startup/shutdown event handlers.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

# Import database configuration and session dependency
from app.database import create_tables, get_db

# Import all models to ensure they are registered with SQLAlchemy
from app.models import (
    Base,
    Role,
    User,
    Project,
    ProjectStage,
    DefectStatus,
    Defect,
    Comment,
    Attachment,
    HistoryLog,
    Report,
    PriorityEnum,
    ActionTypeEnum,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for application startup and shutdown events.
    
    On startup:
    - Creates all database tables (for development)
    - In production, use Alembic migrations instead
    
    On shutdown:
    - Cleanup operations can be added here if needed
    """
    # Startup: Create all tables
    create_tables()
    print("Database tables created successfully")
    
    yield
    
    # Shutdown: Add cleanup operations here if needed
    print("Application shutdown")


# Initialize FastAPI application with lifespan handler
app = FastAPI(
    title="Defect Management System",
    description="Centralized defect management system for construction projects",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def read_root():
    """
    Root endpoint for health check.
    
    Returns:
        dict: Simple message indicating the API is operational
    """
    return {"message": "Defect Management System API is running"}


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint that verifies database connectivity.
    
    Args:
        db: Database session (injected via dependency)
    
    Returns:
        dict: Health status of the application and database
    """
    try:
        # Simple query to verify database connection
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

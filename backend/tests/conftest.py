"""
Pytest configuration and fixtures for testing.

This module provides test database setup and common fixtures
for all test modules.
"""

import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.database import Base
from app.models import (
    Role, User, Project, ProjectStage, DefectStatus, Defect,
    Comment, Attachment, HistoryLog, Report, PriorityEnum, ActionTypeEnum
)

# Disable .pgpass and other config files reading to avoid Unicode issues on Windows
os.environ['PGPASSFILE'] = 'nul'
os.environ['PGSERVICEFILE'] = 'nul'
os.environ['PGSYSCONFDIR'] = 'nul'


# Use a test database URL with psycopg (version 3) driver
# Try to connect to localhost first, fallback to 'db' service name for Docker
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/test_frame1_db"
)

# Alternative: use in-memory SQLite for testing if PostgreSQL is not available
# TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def engine():
    """Create a test database engine."""
    test_engine = create_engine(TEST_DATABASE_URL, echo=False)
    
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    yield test_engine
    
    # Drop all tables after test
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


@pytest.fixture(scope="function")
def db_session(engine):
    """Create a test database session."""
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestSessionLocal()
    
    yield session
    
    session.close()


@pytest.fixture(scope="function")
def sample_role(db_session: Session):
    """Create a sample role for testing."""
    role = Role(name="Engineer", description="Engineering role")
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)
    return role


@pytest.fixture(scope="function")
def sample_user(db_session: Session, sample_role: Role):
    """Create a sample user for testing."""
    user = User(
        full_name="John Doe",
        email="john.doe@example.com",
        password_hash="hashed_password_123",
        role_id=sample_role.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def sample_project(db_session: Session, sample_user: User):
    """Create a sample project for testing."""
    project = Project(
        name="Test Construction Project",
        description="A test project",
        manager_id=sample_user.id
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


@pytest.fixture(scope="function")
def sample_defect_status(db_session: Session):
    """Create a sample defect status for testing."""
    status = DefectStatus(name="New", description="Newly created defect")
    db_session.add(status)
    db_session.commit()
    db_session.refresh(status)
    return status


@pytest.fixture(scope="function")
def sample_defect(db_session: Session, sample_project: Project, sample_defect_status: DefectStatus, sample_user: User):
    """Create a sample defect for testing."""
    defect = Defect(
        project_id=sample_project.id,
        title="Test Defect",
        description="A test defect",
        priority=PriorityEnum.HIGH,
        status_id=sample_defect_status.id,
        created_by=sample_user.id
    )
    db_session.add(defect)
    db_session.commit()
    db_session.refresh(defect)
    return defect

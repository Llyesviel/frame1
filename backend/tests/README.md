# Model Unit Tests

This directory contains comprehensive unit tests for all models in the defect management system.

## Prerequisites

### 1. Database Setup

The tests require a PostgreSQL database. You have two options:

#### Option A: Use Docker (Recommended)

Start the PostgreSQL container:
```bash
docker-compose up -d db
```

Create a test database:
```bash
docker exec -it frame1_db psql -U postgres -c "CREATE DATABASE test_frame1_db;"
```

#### Option B: Local PostgreSQL

If you have PostgreSQL installed locally, create a test database:
```bash
psql -U postgres -c "CREATE DATABASE test_frame1_db;"
```

### 2. Install Dependencies

**Note**: If you're using Python 3.13, you may encounter issues with psycopg2-binary. Consider using Python 3.11 or 3.12 instead.

```bash
cd backend
pip install -r requirements.txt
```

If you encounter issues with psycopg2-binary, try:
```bash
pip install psycopg2-binary --no-binary psycopg2-binary
```

Or use the pure Python implementation:
```bash
pip uninstall psycopg2-binary
pip install psycopg2
```

### 3. Configure Test Database URL

Set the test database URL environment variable (optional):
```bash
export TEST_DATABASE_URL="postgresql://postgres:postgres@localhost:5432/test_frame1_db"
```

On Windows:
```cmd
set TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/test_frame1_db
```

## Running Tests

### Run all model tests:
```bash
pytest tests/test_models.py -v
```

### Run specific test class:
```bash
pytest tests/test_models.py::TestUserModel -v
```

### Run specific test:
```bash
pytest tests/test_models.py::TestUserModel::test_user_creation -v
```

### Run with coverage:
```bash
pytest tests/test_models.py --cov=app.models --cov-report=html
```

## Test Structure

The test file `test_models.py` contains the following test classes:

- **TestRoleModel**: Tests for Role model creation, unique constraints, and relationships
- **TestUserModel**: Tests for User model creation, email uniqueness, and role relationships
- **TestProjectModel**: Tests for Project model and manager relationships
- **TestProjectStageModel**: Tests for ProjectStage model and cascade delete behavior
- **TestDefectStatusModel**: Tests for DefectStatus model and unique constraints
- **TestDefectModel**: Tests for Defect model, priority enum, and relationships
- **TestCommentModel**: Tests for Comment model and cascade delete
- **TestAttachmentModel**: Tests for Attachment model and soft delete functionality
- **TestHistoryLogModel**: Tests for HistoryLog model and action types
- **TestReportModel**: Tests for Report model and relationships
- **TestModelIntegration**: Integration tests for complete workflows

## Test Coverage

The tests cover:

- ✅ Model instantiation and field validation
- ✅ Unique constraints (email, role name, status name)
- ✅ Foreign key relationships
- ✅ One-to-many and many-to-one relationships
- ✅ Cascade delete behaviors
- ✅ Enum types (PriorityEnum, ActionTypeEnum)
- ✅ Soft delete functionality (Attachment model)
- ✅ Timestamp fields (created_at, updated_at)
- ✅ Complex integration workflows

## Troubleshooting

### Database Connection Errors

If you see connection errors, ensure:
1. PostgreSQL is running (check with `docker ps` or `pg_isready`)
2. The test database exists
3. The DATABASE_URL is correct

### Import Errors

If you see import errors, ensure you're running pytest from the `backend` directory:
```bash
cd backend
pytest tests/test_models.py -v
```

### Fixture Errors

The tests use pytest fixtures defined in `conftest.py`. These fixtures:
- Create a fresh database schema for each test
- Provide sample data (roles, users, projects, etc.)
- Clean up after each test

## Requirements Covered

These tests validate all model requirements from the specification:
- Requirements 1.1-1.5: User management
- Requirements 2.1-2.6: Role management
- Requirements 3.1-3.5: Project management
- Requirements 4.1-4.4: Project stages
- Requirements 5.1-5.6: Defect management
- Requirements 6.1-6.4: Defect statuses
- Requirements 7.1-7.4: Comments
- Requirements 8.1-8.5: Attachments
- Requirements 9.1-9.5: History logs
- Requirements 10.1-10.5: Reports
- Requirements 11.1-11.12: Database relationships

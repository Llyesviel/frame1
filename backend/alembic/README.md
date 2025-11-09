# Alembic Database Migrations

This directory contains Alembic database migrations for the defect management system.

## Overview

Alembic is used to manage database schema changes and data migrations. All migrations are version-controlled and can be applied or rolled back as needed.

## Migration Files

- `001_initial_schema.py` - Creates all database tables with proper constraints, indexes, and relationships
- `002_seed_predefined_data.py` - Inserts predefined roles and defect statuses

## Running Migrations

### Inside Docker Container

The recommended way to run migrations is inside the Docker container:

```bash
# Start the containers
docker-compose up -d

# Run migrations inside the backend container
docker-compose exec backend alembic upgrade head

# Check current migration version
docker-compose exec backend alembic current

# View migration history
docker-compose exec backend alembic history
```

### Locally (if psycopg2 is installed)

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run migrations
alembic upgrade head

# Check current version
alembic current

# Rollback one migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision>
```

## Creating New Migrations

### Auto-generate from model changes

```bash
# Inside Docker container
docker-compose exec backend alembic revision --autogenerate -m "description of changes"

# Locally
alembic revision --autogenerate -m "description of changes"
```

### Create empty migration

```bash
# Inside Docker container
docker-compose exec backend alembic revision -m "description of changes"

# Locally
alembic revision -m "description of changes"
```

## Migration Structure

Each migration file contains:
- `revision`: Unique identifier for this migration
- `down_revision`: Previous migration this one depends on
- `upgrade()`: Function to apply the migration
- `downgrade()`: Function to rollback the migration

## Database Schema

The migrations create the following tables:

1. **roles** - User roles (Engineer, Manager, Observer, Admin)
2. **users** - System users with authentication
3. **projects** - Construction projects
4. **project_stages** - Stages within projects
5. **defect_statuses** - Defect status types (New, In Progress, Review, Closed, Canceled)
6. **defects** - Defect records with priority and status
7. **comments** - Comments on defects
8. **attachments** - File attachments for defects
9. **history_logs** - Audit trail of defect changes
10. **reports** - Generated reports

## Environment Variables

The database connection is configured via the `DATABASE_URL` environment variable:

```
DATABASE_URL=postgresql://postgres:postgres@db:5432/frame1_db
```

This is set in:
- `docker-compose.yml` for Docker environments
- `.env` file for local development
- `backend/.env.example` as a template

## Troubleshooting

### Migration fails with "relation already exists"

If tables already exist, you may need to stamp the database with the current version:

```bash
# Mark database as being at a specific version without running migrations
alembic stamp head
```

### Reset database completely

```bash
# Drop all tables and re-run migrations
docker-compose down -v
docker-compose up -d
docker-compose exec backend alembic upgrade head
```

### Check migration status

```bash
# View current version
alembic current

# View all migrations and their status
alembic history --verbose
```

## Best Practices

1. Always review auto-generated migrations before applying them
2. Test migrations on a development database first
3. Create a database backup before running migrations in production
4. Keep migrations small and focused on a single change
5. Never modify existing migration files after they've been applied
6. Always provide both upgrade() and downgrade() functions

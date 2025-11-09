# Database Migrations Quick Reference

## Quick Start

To set up the database with all tables and initial data:

```bash
# Start Docker containers
docker-compose up -d

# Wait for database to be ready, then run migrations
docker-compose exec backend alembic upgrade head
```

That's it! Your database is now ready with:
- All 10 tables created
- 4 predefined roles (Engineer, Manager, Observer, Admin)
- 5 predefined defect statuses (New, In Progress, Review, Closed, Canceled)

## Common Commands

```bash
# Check current migration version
docker-compose exec backend alembic current

# View migration history
docker-compose exec backend alembic history

# Rollback last migration
docker-compose exec backend alembic downgrade -1

# Rollback all migrations
docker-compose exec backend alembic downgrade base

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "your message"
```

## Verifying the Setup

After running migrations, you can verify the setup:

```bash
# Connect to PostgreSQL
docker-compose exec db psql -U postgres -d frame1_db

# List all tables
\dt

# View roles
SELECT * FROM roles;

# View defect statuses
SELECT * FROM defect_statuses;

# Exit psql
\q
```

## Troubleshooting

If you encounter issues:

```bash
# Reset everything
docker-compose down -v
docker-compose up -d
docker-compose exec backend alembic upgrade head
```

For more detailed information, see `backend/alembic/README.md`.

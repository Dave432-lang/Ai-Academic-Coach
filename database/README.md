# Database Setup & Migrations

This directory contains database migration scripts, seed files, and setup documentation for PostgreSQL 17 with `pgvector`.

## Structure

- `migrations/`: Raw SQL migration files (if executing manually outside Alembic).
- `seeds/`: Seed datasets for initial development data (to be added in future phases).

## Alembic Integration

Alembic migrations are configured inside `backend/`. To apply migrations:

```bash
cd backend
alembic upgrade head
```

To rollback the last migration:

```bash
cd backend
alembic downgrade -1
```

## Enabled Extensions

- `vector`: Enabeled via Alembic initial migration `001_initial_pgvector.py`.

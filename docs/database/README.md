# Database Architecture Specification

## Database Engine
- Engine: PostgreSQL 17
- Extension: `pgvector`
- ORM: SQLAlchemy 2.x

## Configuration
- Database Name: `ai_academic_coach`
- Default User: `academic_coach`
- Port: `5432`

## Schema Migrations
Managed via Alembic in `backend/alembic/`. Initial migration enables `vector` extension.

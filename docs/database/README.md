# PostgreSQL Database Core Specification

## 1. Executive Summary & Migration Authority

> [!IMPORTANT]
> **Alembic is the authoritative executable schema migration source of truth.**
> All database table creations, enum definitions, constraints, indexes, triggers, and extensions are managed exclusively via Alembic revisions located in `backend/alembic/versions/`.

- **Database Engine**: PostgreSQL 17
- **Vector Search Extension**: `pgvector` (`vector`)
- **ORM & Driver**: SQLAlchemy 2.x, `psycopg` (v3)
- **Primary Key Strategy**: UUID v4 via `gen_random_uuid()`
- **Timestamps**: Timezone-aware UTC (`TIMESTAMPTZ`), with local timezone stored per student profile
- **Updated At Automation**: PostgreSQL PL/pgSQL function `update_updated_at_column()` and `BEFORE UPDATE` triggers

---

## 2. Table Specifications (18 Tables)

| # | Table Name | Description | Primary Key | Foreign Keys |
|---|---|---|---|---|
| 1 | `users` | User credentials & account status | `id` UUID | None |
| 2 | `universities` | Academic institution directory | `id` UUID | None |
| 3 | `student_profiles` | Student profile info & preferences | `id` UUID | `user_id` -> `users(id)`, `university_id` -> `universities(id)` |
| 4 | `courses` | Academic course catalog | `id` UUID | `university_id` -> `universities(id)` |
| 5 | `course_enrollments` | Student course registrations | `id` UUID | `student_id` -> `student_profiles(id)`, `course_id` -> `courses(id)` |
| 6 | `academic_events` | Exams, assignments, projects | `id` UUID | `student_id` -> `student_profiles(id)`, `course_id` -> `courses(id)` |
| 7 | `tasks` | Actionable task breakdown | `id` UUID | `academic_event_id` -> `academic_events(id)`, `student_id` -> `student_profiles(id)` |
| 8 | `study_sessions` | Scheduled & completed study sessions | `id` UUID | `task_id` -> `tasks(id)`, `student_id` -> `student_profiles(id)` |
| 9 | `goals` | Academic target milestones | `id` UUID | `student_id` -> `student_profiles(id)`, `course_id` -> `courses(id)` |
| 10 | `grades` | Assessment scores & grades | `id` UUID | `student_id` -> `student_profiles(id)`, `course_id` -> `courses(id)` |
| 11 | `course_materials` | Uploaded syllabus, slides, docs | `id` UUID | `student_id` -> `student_profiles(id)`, `course_id` -> `courses(id)` |
| 12 | `document_chunks` | RAG document chunks & embeddings | `id` UUID | `material_id` -> `course_materials(id)` |
| 13 | `conversations` | AI companion conversation threads | `id` UUID | `student_id` -> `student_profiles(id)` |
| 14 | `messages` | Dialogue message records | `id` UUID | `conversation_id` -> `conversations(id)` |
| 15 | `memories` | Student memory context & patterns | `id` UUID | `student_id` -> `student_profiles(id)` |
| 16 | `permissions` | AI agent execution permissions | `id` UUID | `student_id` -> `student_profiles(id)` |
| 17 | `agent_actions` | Autonomous AI agent action log | `id` UUID | `student_id` -> `student_profiles(id)` |
| 18 | `notifications` | System & academic reminder queue | `id` UUID | `student_id` -> `student_profiles(id)` |

---

## 3. PostgreSQL Enums (13 Enums)

- `account_status`: `active`, `suspended`, `pending`, `deleted`
- `enrollment_status`: `active`, `completed`, `dropped`, `withdrawn`
- `event_type`: `assignment`, `quiz`, `exam`, `project`, `presentation`, `other`
- `priority_level`: `low`, `medium`, `high`, `critical`
- `academic_status`: `pending`, `in_progress`, `completed`, `cancelled`, `missed`
- `goal_status`: `active`, `achieved`, `paused`, `cancelled`
- `material_processing_status`: `pending`, `processing`, `completed`, `failed`
- `message_role`: `user`, `assistant`, `system`
- `memory_type`: `preference`, `goal`, `academic_context`, `learning_pattern`
- `agent_type`: `coordinator`, `planner`, `study`, `progress`
- `action_status`: `pending`, `awaiting_approval`, `approved`, `rejected`, `executing`, `completed`, `failed`, `cancelled`
- `permission_mode`: `allow`, `require_approval`, `require_confirmation`, `deny`
- `notification_status`: `scheduled`, `sent`, `read`, `dismissed`, `failed`, `cancelled`

---

## 4. Indexing & Vector Search Strategy

### Explicit Performance Indexes
- `idx_student_profiles_university_id`: `student_profiles(university_id)`
- `idx_course_enrollments_student_id`: `course_enrollments(student_id)`
- `idx_course_enrollments_course_id`: `course_enrollments(course_id)`
- `idx_academic_events_student_due_at`: `academic_events(student_id, due_at)`
- `idx_academic_events_course_id`: `academic_events(course_id)`
- `idx_tasks_student_status`: `tasks(student_id, status)`
- `idx_study_sessions_student_scheduled_start`: `study_sessions(student_id, scheduled_start)`
- `idx_study_sessions_task_id`: `study_sessions(task_id)`
- `idx_goals_student_status`: `goals(student_id, status)`
- `idx_grades_student_course`: `grades(student_id, course_id)`
- `idx_course_materials_student_course`: `course_materials(student_id, course_id)`
- `idx_messages_conversation_created_at`: `messages(conversation_id, created_at)`
- `idx_memories_student_is_active`: `memories(student_id, is_active)`
- `idx_agent_actions_student_created_at`: `agent_actions(student_id, created_at)`
- `idx_notifications_student_status`: `notifications(student_id, status)`

### Partial Index
- `idx_notifications_scheduled_for`: `notifications(scheduled_for)` WHERE `status = 'scheduled'`

### `pgvector` HNSW Index
- `idx_document_chunks_embedding_hnsw`: `document_chunks USING hnsw (embedding vector_cosine_ops)`

---

## 5. Automatic `updated_at` Triggers

PostgreSQL function `update_updated_at_column()` sets `NEW.updated_at = NOW()` before any `UPDATE` operation.
Attached via `BEFORE UPDATE` triggers (`trg_<table_name>_updated_at`) to:
`users`, `universities`, `student_profiles`, `courses`, `course_enrollments`, `academic_events`, `tasks`, `study_sessions`, `goals`, `grades`, `course_materials`, `conversations`, `memories`, `permissions`.

---

## 6. Migration & Development Seed Workflow

### Executing Migrations
From `backend/` directory:
```bash
# Apply all migrations to head
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# Show migration history
alembic history
```

### Development Seed Data Strategy
Fictional seed data is provided in `database/seeds/development.sql` (contains test university, courses, sample student).
Run seeds manually using `psql`:
```bash
psql -U academic_coach -d ai_academic_coach -f database/seeds/development.sql
```

### Inspecting Database Schema
```bash
psql -U academic_coach -d ai_academic_coach -c "\dt"
```

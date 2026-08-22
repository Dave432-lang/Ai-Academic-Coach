# AI Academic Coach Architecture Overview

## System Data Flow Architecture

The Phase 1 system foundation establishes a decoupled, modular layer architecture:

```
+-------------------------------------------------------------------+
|                        Flutter Mobile App                         |
|   (UI Screens, Widgets, ApiService, Multi-platform API Config)    |
+-------------------------------------------------------------------+
                                  |
                                  | HTTP / JSON (GET /health)
                                  v
+-------------------------------------------------------------------+
|                        FastAPI Backend Engine                     |
|    (Main App Entry, CORS Middleware, Router, Structured Logging)   |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                      Services Layer (Phase 1 Base)                |
|      (Pydantic Schemas, Connection Helpers, Error Handlers)       |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                SQLAlchemy 2.x Database Connection                 |
|   (Engine Pool, Session Factory, Declarative Base, Migration Ext)  |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                      PostgreSQL 17 + pgvector                      |
|                  (Docker Container, Persistent Data)              |
+-------------------------------------------------------------------+
```

---

## Component Status (Phase 1 vs Planned)

### Implemented in Phase 1 (Foundation):
- **Flutter UI & API Service**: Basic app initialization and environment-aware API configuration.
- **FastAPI Core**: Application factory, health endpoints, CORS middleware, Pydantic settings.
- **SQLAlchemy 2.x Layer**: Session lifecycle management, declarative base, connectivity checks.
- **Alembic Infrastructure**: Database migrations setup and pgvector extension initialization.
- **Docker Compose Setup**: PostgreSQL 17 with pgvector containerization and persistent storage.

---

### Planned Architecture Components (Future Phases - NOT Implemented Yet):

| Component | Status | Target Phase | Description |
|---|---|---|---|
| **AI Coordinator** | 🔮 Planned | Phase 2+ | Central orchestration agent managing sub-agent workflows. |
| **Planner Agent** | 🔮 Planned | Phase 2+ | Study schedule, assignment tracking, and task decomposition engine. |
| **Study Agent** | 🔮 Planned | Phase 2+ | Interactive academic tutoring and concepts explanation module. |
| **Progress Agent** | 🔮 Planned | Phase 2+ | Analytics and academic performance tracker. |
| **Memory Manager** | 🔮 Planned | Phase 3 | Short-term and long-term conversation context management. |
| **RAG Engine** | 🔮 Planned | Phase 3 | Retrieval-Augmented Generation using pgvector embeddings. |
| **Permission Manager**| 🔮 Planned | Phase 2 | User authorization, course access control, and tenant security. |
| **Tools & Plugins** | 🔮 Planned | Phase 3+ | External integrations (Canvas, Blackboard, Google Calendar). |

> **Note**: Phase 1 deliberately excludes all AI models, agent abstractions, vector search logic, and user authentication to maintain a clean foundation.

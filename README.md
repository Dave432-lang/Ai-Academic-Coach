# AI Academic Coach (Phase 1 Foundation)

Production-oriented AI academic companion for university students worldwide. 
This repository represents **PHASE 1 ONLY** focused on building a clean, scalable, maintainable foundation.

---

## 1. Project Purpose

The **AI Academic Coach** is designed to assist university students with study planning, course comprehension, task breakdown, and academic performance tracking. Phase 1 establishes the core structural foundation, backend API, database containerization, migration pipeline, and cross-platform mobile app client.

---

## 2. Technology Stack

- **Mobile**: Flutter, Dart
- **Backend**: Python 3.11+, FastAPI, Pydantic (v2), SQLAlchemy 2.x, Alembic
- **Database**: PostgreSQL 17 + `pgvector`
- **Development**: Docker, Docker Compose, Git
- **Testing**: Pytest, HTTPX, Flutter Test

---

## 3. Folder Structure

```
ai-academic-coach/
│
├── mobile/                 # Flutter mobile application
│   ├── lib/
│   │   ├── main.dart
│   │   ├── core/           # Config & theme
│   │   ├── models/         # Data models
│   │   ├── services/       # API client service
│   │   ├── features/       # Screens & UI features
│   │   ├── widgets/        # Shared components
│   │   └── routes/         # App navigation routes
│   └── test/               # Widget tests
│
├── backend/                # FastAPI backend application
│   ├── app/
│   │   ├── main.py         # Application entry point
│   │   ├── core/           # Config, security, logging
│   │   ├── database/       # Connection, models, repositories
│   │   ├── api/            # Route controllers (health.py)
│   │   ├── services/       # Business domain logic
│   │   └── schemas/        # Pydantic validation schemas
│   ├── tests/              # Pytest suite
│   ├── alembic/            # DB migrations
│   ├── alembic.ini         # Alembic configuration
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment template
│
├── database/               # SQL scripts & seeds
│   ├── migrations/
│   ├── seeds/
│   └── README.md
│
├── docs/                   # Architecture & API documentation
│   ├── architecture/
│   ├── api/
│   ├── database/
│   └── project/
│
├── tests/                  # Cross-platform integration tests
├── docker/                 # Container configs
├── .gitignore              # Git ignore rules
├── README.md               # Main project guide
└── docker-compose.yml      # Local Docker PostgreSQL setup
```

---

## 4. Prerequisites

- **Python**: 3.11+ (Python 3.13 supported)
- **Flutter**: 3.20+
- **Docker Desktop** (or Docker engine with Docker Compose)
- **Git**

---

## 5. How to Start PostgreSQL

Ensure Docker is running, then execute from the root directory:

```bash
docker-compose up -d postgres
```

Verify container status:
```bash
docker-compose ps
```

---

## 6. How to Configure `.env`

Copy the environment example file in the `backend/` directory:

```bash
cd backend
cp .env.example .env
```

On Windows PowerShell:
```powershell
cd backend
Copy-Item .env.example .env
```

*Note: Never commit `.env` to Git repository.*

---

## 7. How to Start FastAPI

1. Create and activate a Python virtual environment:
```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Verify backend health at: [http://localhost:8000/health](http://localhost:8000/health)

---

## 8. How to Start Flutter

1. Navigate to `mobile/` directory:
```bash
cd mobile
```

2. Install dependencies:
```bash
flutter pub get
```

3. Run application (Targeting Chrome, Windows Desktop, or Emulator):
```bash
flutter run
```

### Platform Target API Configurations:
- **Windows Desktop / Web**: `http://localhost:8000`
- **iOS Simulator**: `http://localhost:8000`
- **Android Emulator**: `http://10.0.2.2:8000`
- **Physical Android Device**: `http://<YOUR_LAN_IP>:8000`

---

## 9. How to Run Migrations

From the `backend/` directory with virtual environment activated and database running:

```bash
# Apply migrations to head
alembic upgrade head

# Rollback single migration
alembic downgrade -1
```

---

## 10. How to Run Tests

### Backend Pytest Suite:
```bash
cd backend
pytest
```

### Flutter Test Suite:
```bash
cd mobile
flutter test
```

---

## 11. How to Stop Docker

To stop the database service:

```bash
docker-compose stop postgres
```

To stop and remove containers & networks:
```bash
docker-compose down
```

To clear volume data:
```bash
docker-compose down -v
```

---

## 12. Development Workflow

1. Start PostgreSQL via Docker Compose (`docker-compose up -d`).
2. Run database migrations (`alembic upgrade head`).
3. Start FastAPI server (`uvicorn app.main:app --reload`).
4. Launch Flutter mobile client (`flutter run`).
5. Run automated test suites before committing changes.

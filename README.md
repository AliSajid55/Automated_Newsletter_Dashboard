# The CTO's Morning Brief - Automated Newsletter Dashboard

An intelligent system that collects tech news from 50+ RSS sources every 2 hours, uses **Gemini AI** for smart categorization & summarization, and presents it in a **Tinder-style React dashboard** for quick consumption.

---

## Architecture Overview

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Celery Beat  │────▶│ Celery Worker │────▶│  Gemini AI   │
│  (Scheduler)  │     │ (RSS Fetch)  │     │  (Summaries) │
└──────────────┘     └──────┬───────┘     └──────────────┘
                            │
                    ┌───────▼───────┐
                    │  PostgreSQL   │
                    │  (Articles)   │
                    └───────┬───────┘
                            │
                    ┌───────▼───────┐     ┌──────────────┐
                    │   FastAPI     │────▶│  React App   │
                    │   (REST API)  │     │ (Swipe Cards)│
                    └───────────────┘     └──────────────┘
```

## Tech Stack

| Layer       | Technology                                      |
| ----------- | ----------------------------------------------- |
| Backend API | FastAPI, SQLAlchemy, Alembic                     |
| Task Queue  | Celery + Redis (Broker)                          |
| AI          | Google Gemini API                                |
| Database    | PostgreSQL                                       |
| Frontend    | React, Vite, Tailwind CSS, Framer Motion         |
| Swiping     | react-tinder-card                                |
| Data Fetch  | TanStack Query (React Query)                     |
| Icons       | Lucide React                                     |

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Settings & environment
│   │   ├── database.py          # DB session & engine
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── api/routes/          # API endpoints
│   │   ├── services/            # Business logic
│   │   ├── core/                # Taxonomy, constants
│   │   └── worker/              # Celery app & tasks
│   ├── alembic/                 # Database migrations
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── hooks/               # Custom hooks
│   │   ├── api/                 # API client
│   │   └── utils/               # Constants & helpers
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml
└── README.md
```

## Quick Start

### 1. Environment Setup

```bash
# Clone and setup
cp .env.example .env
# Fill in your GEMINI_API_KEY, DATABASE_URL, REDIS_URL
```

### 2. Run with Docker

```bash
docker-compose up --build
```

### 3. Run Manually

**Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

**Celery Worker:**
```bash
celery -A app.worker.celery_app worker --loglevel=info
celery -A app.worker.celery_app beat --loglevel=info
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

| Method | Endpoint                  | Description                      |
| ------ | ------------------------- | -------------------------------- |
| GET    | `/feed`                   | Paginated news cards             |
| GET    | `/article/{id}`           | Full article + AI summary        |
| GET    | `/tags`                   | All tags with article counts     |
| POST   | `/article/{id}/save`      | Bookmark article                 |
| POST   | `/article/{id}/dismiss`   | Dismiss (left-swipe)             |

## License

MIT

## Author

Ali Sajid
AI Engineer | Deep Learning | Computer Vision | GEN AI

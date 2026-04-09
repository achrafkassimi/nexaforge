# NexaForge — AI Agency Management Platform

> A complete company management platform where every employee is an AI Agent.

![NexaForge](https://img.shields.io/badge/NexaForge-v1.0-8b5cf6?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-gray?style=flat-square)

---

## What is NexaForge?

NexaForge simulates a real software company where AI Agents work as specialized developers. Each agent has a role, skills, and works autonomously on assigned tasks using an LLM (Claude API or Ollama locally).

```
Super Admin → Chef de Manager → Chef de Projet → AI Agents
                                                  ├── Backend Agent
                                                  ├── Frontend Agent
                                                  ├── Database Agent
                                                  └── DevOps Agent
```

---

## Features

- **AI Agents** — Each agent works autonomously on tasks using LLM
- **Heartbeat protocol** — Agents check for tasks every 10 minutes
- **Peer review** — Agents review each other's work before delivery
- **Agile / Scrum** — Sprints, backlog, burndown charts
- **Real-time dashboard** — WebSockets for live updates
- **Hybrid LLM** — Claude API or Ollama (local, free, offline)
- **Full hierarchy** — Super Admin → Manager → Chef Projet → Agent

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11 + FastAPI |
| Database | PostgreSQL 15 |
| Cache | Redis 7 |
| Auth | JWT + bcrypt |
| Real-time | WebSockets |
| Frontend | HTML / CSS / JS |
| AI (cloud) | Claude API (Anthropic) |
| AI (local) | Ollama + llama3.2 |
| Infra | Docker + Docker Compose |

---

## Project Structure

```
nexaforge/
├── backend/
│   ├── models/          # SQLAlchemy models (User, Project, Task, Sprint, Agent)
│   ├── schemas/         # Pydantic schemas
│   ├── routers/         # FastAPI endpoints (auth, projects, tasks, agents, sprints, users)
│   ├── services/        # Business logic (auth_service)
│   ├── ws_manager/      # WebSocket connection manager
│   ├── migrations/      # Alembic migrations
│   ├── tests/           # pytest tests
│   ├── main.py          # FastAPI app entry point
│   └── requirements.txt
├── agents/
│   ├── base_agent.py    # Base class with heartbeat loop
│   ├── backend_agent.py # Backend AI Agent (Nova)
│   ├── frontend_agent.py
│   ├── database_agent.py
│   ├── devops_agent.py
│   └── orchestrator.py
├── frontend/
│   ├── pages/           # HTML pages
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── projects.html
│   │   ├── agents.html
│   │   ├── users.html
│   │   ├── logs.html
│   │   └── settings.html
│   └── styles/
│       └── globals.css
├── infra/
│   └── docker-compose.yml
├── .env.example
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Docker Desktop
- Git
- Ollama (for local AI) or Anthropic API key

### 1 — Clone the repo

```bash
git clone https://github.com/achrafkassimi/nexaforge.git
cd nexaforge
```

### 2 — Start database

```bash
cd infra
docker compose up -d
```

### 3 — Setup backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4 — Configure environment

Copy `.env.example` to `backend/.env` and fill in:

```env
DATABASE_URL=postgresql://nexaforge:nexaforge123@localhost:5432/nexaforge
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-here

# Choose one:
ANTHROPIC_API_KEY=sk-ant-...   # Cloud AI
# OR use Ollama for free local AI (no key needed)
```

### 5 — Run migrations

```bash
cd backend
alembic upgrade head
```

### 6 — Start the server

```bash
uvicorn main:app --reload
```

API running at: `http://localhost:8000`
Swagger docs: `http://localhost:8000/docs`

### 7 — Open the frontend

Open `frontend/pages/login.html` in your browser.

Default credentials after first register:
- Email: `admin@nexaforge.com`
- Password: `admin123`

---

## Running AI Agents

### Option A — Ollama (free, local, no API key)

```bash
# Terminal 1 — start Ollama
ollama serve

# Terminal 2 — pull model (first time only)
ollama pull llama3.2

# Terminal 3 — run agent
cd agents
python backend_agent.py
```

### Option B — Claude API

Add your key to `.env`:
```env
ANTHROPIC_API_KEY=sk-ant-...
```

Then run the agent:
```bash
cd agents
python backend_agent.py
```

---

## How Agents Work

```
1. Agent authenticates → gets JWT token
2. Every 60 seconds (heartbeat):
   a. Check for tasks in "peer_review" → review peers
   b. Check for tasks in "todo" → pick highest priority
   c. Move task → "in_progress"
   d. Send task to LLM (Ollama or Claude)
   e. Post LLM output as comment on task
   f. Move task → "peer_review"
3. If BLOCKER detected → stay in "in_progress" + notify manager
```

### Task Status Flow

```
backlog → todo → in_progress → peer_review → final_review → done
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login + get JWT token |
| GET | `/api/projects/` | List all projects |
| POST | `/api/projects/` | Create project |
| GET | `/api/tasks/` | List all tasks |
| POST | `/api/tasks/` | Create task |
| GET | `/api/agents/` | List all agents |
| POST | `/api/agents/` | Create agent |
| GET | `/api/sprints/` | List all sprints |
| POST | `/api/sprints/` | Create sprint |
| GET | `/api/users/` | List all users |
| WS | `/ws/{room}` | WebSocket connection |

---

## Agent Types

| Agent | Specialty | LLM Persona |
|---|---|---|
| Backend | FastAPI, REST APIs, Auth | Nova |
| Frontend | React, HTML/CSS, UI | — |
| Database | PostgreSQL, SQLAlchemy, Redis | Atlas |
| DevOps | Docker, CI/CD, Nginx | — |
| Manager | Task creation, coordination | — |

---

## LLM Modes

| Mode | Provider | Best for |
|---|---|---|
| `local` | Ollama | Development, no cost |
| `api` | Claude / GPT-4 | Production, best quality |
| `hybrid` | API + Ollama fallback | Staging, resilient |

---

## Contributing

1. Fork the repo
2. Create a branch: `git checkout -b feature/my-feature`
3. Commit: `git commit -m "feat: add my feature"`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

## License

MIT License — free to use, modify, and distribute.

---

*Built with FastAPI, PostgreSQL, and AI Agents — NexaForge 2026*

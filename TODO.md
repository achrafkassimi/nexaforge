# NexaForge — Task Board

> Track progress on fixes, features, and improvements.

---

## 🔴 Quick Fixes — Priority 1

- [x] **Fix `routers/__init__.py`**
  - Fixed: `from . import auth, projects, tasks, agents, sprints, users`

- [x] **Create `.env.example`**
  - Created with: `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`, `ANTHROPIC_API_KEY`

- [x] **`PATCH /status` → broadcast WebSocket**
  - Fixed: `await manager.broadcast(...)` added inside PATCH endpoint

- [x] **Create `TaskUpdate` schema**
  - Created in `backend/schemas/task.py` with all optional fields including `status`

---

## 🟡 Medium Term — Priority 2

- [x] **Frontend Agent — `agents/frontend_agent.py`**
  - Pixel — senior Frontend Engineer, Ollama llama3.2

- [x] **Database Agent — `agents/database_agent.py`**
  - Atlas — senior Database Engineer, Ollama llama3.2

- [x] **DevOps Agent — `agents/devops_agent.py`**
  - Forge — senior DevOps Engineer, Ollama llama3.2

- [x] **Task Comments — endpoint + UI**
  - Backend: `GET/POST /api/tasks/{id}/comments` in `routers/tasks.py`
  - Migration: `a1b2c3d4e5f6_add_task_comments.py`
  - Frontend: comment feed in `task_detail.html` with WebSocket live reload

- [x] **Orchestrator — `agents/orchestrator.py`**
  - Nexus — promotes `peer_review` → `final_review` after all peers approve

---

## 🟢 Long Term — Priority 3

- [x] **SOUL.md per agent**
  - Created: `agents/souls/backend.md`, `frontend.md`, `database.md`, `devops.md`, `manager.md`

- [x] **Real Peer Review between agents**
  - Implemented in `base_agent.py`: `get_peer_review_tasks()`, `review_task()`, `post_comment()`
  - Posts `APPROVED` or `CHANGES_NEEDED` comments on peer_review tasks

- [x] **Sprint Burndown Chart**
  - Created `frontend/pages/sprint_burndown.html` with Chart.js
  - Ideal vs Real lines, sprint selector, story point stats

---

## ✅ Bonus features added

- [x] **Full project workflow**: draft → pending_approval → approved → active → done
- [x] **CDC Agent** (`agents/cdc_agent.py`): reads cahier de charge, auto-generates tasks+subtasks via Claude
- [x] **Generate CDC with AI** button in projects.html (Ollama primary, Anthropic fallback)
- [x] **Admin approval flow**: submit, approve, reject with reason
- [x] **Shared sidebar.js**: auth guard, logout, active nav, user card — used by all pages
- [x] **Consistent UI**: all pages use `globals.css` + `sidebar.js`
- [x] **project_detail.html**: workflow visualization, sprints + tasks, CDC display
- [x] **task_detail.html**: task info, comment feed, WebSocket live updates
- [x] **start_nexaforge.bat**: launches all 6 agents + Docker + migrations

---

## Progress

| Category | Done | Total |
|---|---|---|
| Quick Fixes | 4 | 4 |
| Medium Term | 5 | 5 |
| Long Term | 3 | 3 |
| Bonus | 9 | 9 |
| **Total** | **21** | **21** |

---

*Last updated: all tasks complete — project fully functional*

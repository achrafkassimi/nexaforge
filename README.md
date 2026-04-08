Etapes — ch'no tkteb f kol fichier
Etape 1 — Setup

Install les outils
Cree le repo GitHub
Cree les dossiers

Etape 2 — docker-compose.yml

Kteb fiha: PostgreSQL + Redis

Etape 3 — main.py

Kteb fiha: FastAPI app + /health endpoint

Etape 4 — models/

Kteb fiha: les tables (User, Project, Task, Sprint, Agent)

Etape 5 — schemas/

Kteb fiha: les formats JSON ta3 kol table (ch'no kayb3at/yatlqa l'API)

Etape 6 — routers/auth.py

Kteb fiha: login + register endpoints + JWT

Etape 7 — routers/projects.py + tasks.py + agents.py

Kteb fiha: CRUD complet ta3 kol entite

Etape 8 — services/

Kteb fiha: la logique (kifach tcreei project, kifach tassigni agent...)

Etape 9 — frontend/pages/login.html

Kteb fiha: formulaire login yconnecti lil API

Etape 10 — frontend/pages/dashboard.html

Kteb fiha: dashboard Admin basique

Etape 11 — agents/base_agent.py

Kteb fiha: heartbeat loop

Etape 12 — agents/backend_agent.py

Kteb fiha: yb3at task lil Claude API + yupdate statut

Etape 13 — websockets/

Kteb fiha: real-time updates lil dashboard


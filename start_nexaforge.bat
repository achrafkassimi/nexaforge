@echo off
title NexaForge Launcher
color 0D

echo.
echo  ==================================================================================
echo  ███╗   ██╗███████╗██╗  ██╗ █████╗ ███████╗ ██████╗ ██████╗  ██████╗ ███████╗
echo  ████╗  ██║██╔════╝╚██╗██╔╝██╔══██╗██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝
echo  ██╔██╗ ██║█████╗   ╚███╔╝ ███████║█████╗  ██║   ██║██████╔╝██║  ███╗█████╗
echo  ██║╚██╗██║██╔══╝   ██╔██╗ ██╔══██║██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝
echo  ██║ ╚████║███████╗██╔╝ ██╗██║  ██║██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗
echo  ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝
echo.
echo                    AI Agency Management Platform — v2.0
echo  ==================================================================================
echo.

:: Check if running from project root
if not exist "backend\main.py" (
    echo  [ERROR] Run this file from the nexaforge root directory!
    echo  Example: C:\Users\Achraf\Documents\nexaforge\start_nexaforge.bat
    pause
    exit /b 1
)

:: ─── STEP 1 — Docker (PostgreSQL + Redis) ─────────────────────────────────
echo  [1/5] Starting Docker services (PostgreSQL + Redis)...
cd infra
docker compose up -d
if %errorlevel% neq 0 (
    echo  [ERROR] Docker failed. Make sure Docker Desktop is running.
    cd ..
    pause
    exit /b 1
)
cd ..
echo  [OK] PostgreSQL + Redis started
echo.

:: Wait for DB to be ready
echo  [2/5] Waiting for database to be ready...
timeout /t 4 /nobreak >nul

:: Run Alembic migrations
echo  Running database migrations...
cd backend
call venv\Scripts\activate
alembic upgrade head
if %errorlevel% neq 0 (
    echo  [WARN] Migration failed or already up to date — continuing...
)
cd ..
echo  [OK] Database ready
echo.

:: ─── STEP 2 — Ollama (local LLM fallback) ─────────────────────────────────
echo  [3/5] Starting Ollama (local AI for backend/frontend/db/devops agents)...
start "Ollama Server" cmd /k "ollama serve"
timeout /t 2 /nobreak >nul
echo  [OK] Ollama started
echo.

:: ─── STEP 3 — FastAPI Backend ─────────────────────────────────────────────
echo  [4/5] Starting FastAPI backend...
start "NexaForge Backend" cmd /k "cd /d %~dp0backend && venv\Scripts\activate && uvicorn main:app --reload"
timeout /t 4 /nobreak >nul
echo  [OK] Backend started at http://localhost:8000
echo.

:: ─── STEP 4 — Wait then start agents ─────────────────────────────────────
echo  [5/5] Starting AI Agents...
echo.
timeout /t 2 /nobreak >nul

start "Agent: Nova (Backend)"   cmd /k "cd /d %~dp0agents && ..\backend\venv\Scripts\activate && python backend_agent.py"
timeout /t 1 /nobreak >nul

start "Agent: Pixel (Frontend)" cmd /k "cd /d %~dp0agents && ..\backend\venv\Scripts\activate && python frontend_agent.py"
timeout /t 1 /nobreak >nul

start "Agent: Atlas (Database)" cmd /k "cd /d %~dp0agents && ..\backend\venv\Scripts\activate && python database_agent.py"
timeout /t 1 /nobreak >nul

start "Agent: Forge (DevOps)"   cmd /k "cd /d %~dp0agents && ..\backend\venv\Scripts\activate && python devops_agent.py"
timeout /t 1 /nobreak >nul

start "Agent: CDC (Claude AI)"  cmd /k "cd /d %~dp0agents && ..\backend\venv\Scripts\activate && python cdc_agent.py"
timeout /t 1 /nobreak >nul

start "Agent: Nexus (Orchestrator)" cmd /k "cd /d %~dp0agents && ..\backend\venv\Scripts\activate && python orchestrator.py"
timeout /t 1 /nobreak >nul

echo  [OK] All 6 agents started
echo.

:: ─── READY ────────────────────────────────────────────────────────────────
echo  =====================================================================
echo.
echo  [READY] NexaForge is fully running!
echo.
echo  Frontend  →  Opens automatically in browser
echo  API Docs  →  http://localhost:8000/docs
echo  Health    →  http://localhost:8000/health
echo.
echo  AGENTS running:
echo    Nova     — Backend Engineer  (Ollama llama3.2)
echo    Pixel    — Frontend Engineer (Ollama llama3.2)
echo    Atlas    — Database Engineer (Ollama llama3.2)
echo    Forge    — DevOps Engineer   (Ollama llama3.2)
echo    CDC      — Specs → Tasks     (Claude Sonnet 4.6)
echo    Nexus    — Orchestrator      (Ollama llama3.2)
echo.
echo  WORKFLOW:
echo    1. Open Projects → New Project → write Cahier de Charge
echo    2. Click Submit  → Super Admin logs in → Approve
echo    3. Click Start   → CDC Agent generates all tasks automatically
echo    4. Agents pick up tasks and execute them every 60s
echo    5. Track progress in Burndown chart
echo.
echo  =====================================================================
echo.

:: Open browser
timeout /t 2 /nobreak >nul
start "" "%~dp0frontend\pages\login.html"

echo  Press any key to STOP all services...
pause >nul

:: Stop services
echo.
echo  Stopping Docker services...
cd infra
docker compose stop
echo  [OK] Docker stopped
echo  [OK] Close agent windows manually (or close all cmd windows)
echo.
pause

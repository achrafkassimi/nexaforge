@echo off
title NexaForge Launcher
color 0D

echo.
echo  ███╗   ██╗███████╗██╗  ██╗ █████╗ ███████╗ ██████╗ ██████╗  ██████╗ ███████╗
echo  ████╗  ██║██╔════╝╚██╗██╔╝██╔══██╗██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝
echo  ██╔██╗ ██║█████╗   ╚███╔╝ ███████║█████╗  ██║   ██║██████╔╝██║  ███╗█████╗
echo  ██║╚██╗██║██╔══╝   ██╔██╗ ██╔══██║██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝
echo  ██║ ╚████║███████╗██╔╝ ██╗██║  ██║██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗
echo  ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝
echo.
echo  AI Agency Management Platform — v1.0
echo  ===============================================================
echo.

:: Check if running from project root
if not exist "backend\main.py" (
    echo  [ERROR] Run this file from the nexaforge root directory!
    echo  Example: C:\Users\Achraf\Documents\nexaforge\start_nexaforge.bat
    pause
    exit /b 1
)

echo  [1/4] Starting Docker services (PostgreSQL + Redis)...
cd infra
docker compose up -d
if %errorlevel% neq 0 (
    echo  [ERROR] Docker failed. Make sure Docker Desktop is running.
    pause
    exit /b 1
)
cd ..
echo  [OK] PostgreSQL + Redis started
echo.

:: Wait for DB to be ready
echo  [2/4] Waiting for database to be ready...
timeout /t 3 /nobreak >nul
echo  [OK] Database ready
echo.

:: Start Ollama in new window
echo  [3/4] Starting Ollama (local AI)...
start "Ollama Server" cmd /k "ollama serve"
timeout /t 2 /nobreak >nul
echo  [OK] Ollama started
echo.

:: Start FastAPI backend in new window
echo  [4/4] Starting FastAPI backend...
start "NexaForge Backend" cmd /k "cd /d %~dp0backend && venv\Scripts\activate && uvicorn main:app --reload"
timeout /t 3 /nobreak >nul
echo  [OK] Backend started at http://localhost:8000
echo.

echo  ===============================================================
echo.
echo  [READY] NexaForge is running!
echo.
echo  Frontend  →  open frontend\pages\login.html in browser
echo  API Docs  →  http://localhost:8000/docs
echo  Health    →  http://localhost:8000/health
echo.
echo  ---------------------------------------------------------------
echo  To run an AI Agent, open a new terminal and run:
echo    cd agents
echo    venv\Scripts\activate (from backend folder)
echo    python backend_agent.py
echo  ---------------------------------------------------------------
echo.

:: Open browser automatically
echo  Opening dashboard in browser...
timeout /t 2 /nobreak >nul
start "" "%~dp0frontend\pages\login.html"

echo.
echo  Press any key to stop all services...
pause >nul

:: Stop services
echo.
echo  Stopping services...
cd infra
docker compose down
echo  [OK] Docker services stopped
echo  [OK] Close the other terminal windows manually (Ollama, Backend)
echo.
pause
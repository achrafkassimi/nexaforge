from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, projects, tasks, agents, sprints, users
from routers import ws
from routers import ai
from routers import files

app = FastAPI(title="NexaForge API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(agents.router)
app.include_router(sprints.router)
app.include_router(ws.router)
app.include_router(users.router)
app.include_router(ai.router)
app.include_router(files.router)


@app.get("/health")
def health():
    return {"status": "ok", "app": "NexaForge"}
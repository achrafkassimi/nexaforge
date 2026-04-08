from fastapi import FastAPI
from routers import auth, projects, tasks, agents

app = FastAPI(title="NexaForge API", version="1.0.0")

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(agents.router)

@app.get("/health")
def health():
    return {"status": "ok", "app": "NexaForge"}
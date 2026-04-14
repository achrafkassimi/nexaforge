"""
CahierDeChargeAgent — watches for active projects and auto-generates
tasks + subtasks using Ollama (qwen2.5:7b) from the cahier de charge.
"""
import asyncio
import httpx
import json
import re
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../backend/.env"))

API          = "http://localhost:8000"
OLLAMA_URL   = os.getenv("OLLAMA_URL",   "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

SYSTEM_PROMPT = """You are Nexus CDC, a senior Technical Project Manager.
Read the cahier de charge (project specifications) and decompose it into
concrete engineering tasks and subtasks for AI agents.

Agent types available: backend, frontend, database, devops

Rules:
- Create 5 to 15 tasks depending on project complexity
- Each task can have 0 to 4 subtasks
- backend = API/logic, frontend = UI, database = schema/migrations, devops = infra/CI
- story_points between 1 and 8
- priority: critical > high > medium > low

RESPOND WITH VALID JSON ONLY — no explanation, no markdown, no code fences.
Example format:
{
  "tasks": [
    {
      "title": "Create user authentication API",
      "description": "Implement JWT login and registration endpoints",
      "agent_type": "backend",
      "priority": "high",
      "story_points": 5,
      "subtasks": [
        {
          "title": "Create User model",
          "description": "SQLAlchemy model with hashed password",
          "agent_type": "database",
          "priority": "high",
          "story_points": 2
        }
      ]
    }
  ]
}"""


class CahierDeChargeAgent:
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        self.processed_projects = set()

    async def get_active_projects(self):
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{API}/api/projects/", headers=self.headers)
            return [p for p in res.json() if p["status"] == "active"]

    async def get_sprint_for_project(self, project_id: str):
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{API}/api/sprints/", headers=self.headers)
            active = [s for s in res.json() if s["project_id"] == project_id and s["status"] == "active"]
            return active[0] if active else None

    async def create_task(self, sprint_id: str, task_data: dict, parent_task_id: str = None) -> dict:
        payload = {
            "title":        task_data["title"],
            "description":  task_data.get("description", ""),
            "priority":     task_data.get("priority", "medium"),
            "story_points": task_data.get("story_points", 3),
            "agent_type":   task_data.get("agent_type", "backend"),
            "sprint_id":    sprint_id,
        }
        if parent_task_id:
            payload["parent_task_id"] = parent_task_id
        async with httpx.AsyncClient() as client:
            res = await client.post(f"{API}/api/tasks/", headers=self.headers, json=payload)
            return res.json()

    async def post_comment(self, task_id: str, content: str):
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{API}/api/tasks/{task_id}/comments",
                headers=self.headers,
                json={"content": content}
            )

    def generate_tasks_from_cdc(self, project_name: str, cahier_de_charge: str) -> list:
        print(f"[CDC] Sending cahier de charge to Ollama ({OLLAMA_MODEL}) for '{project_name}'...")

        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"Project: {project_name}\n\n"
            f"Cahier de charge:\n{cahier_de_charge}\n\n"
            f"Respond with JSON only:"
        )

        try:
            response = httpx.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
                timeout=180
            )
        except Exception as e:
            print(f"[CDC] Cannot reach Ollama: {e}")
            return []

        if response.status_code == 404:
            print(f"[CDC] Model '{OLLAMA_MODEL}' not found. Run: ollama pull {OLLAMA_MODEL}")
            return []

        if response.status_code != 200:
            print(f"[CDC] Ollama error {response.status_code}: {response.text[:200]}")
            return []

        raw = response.json().get("response", "").strip()
        if not raw:
            print("[CDC] Ollama returned empty response")
            return []

        # Extract JSON from response
        match = re.search(r'\{[\s\S]*\}', raw)
        if not match:
            print(f"[CDC] Could not find JSON in response. Raw: {raw[:200]}")
            return []

        try:
            data = json.loads(match.group())
            return data.get("tasks", [])
        except json.JSONDecodeError as e:
            print(f"[CDC] JSON parse error: {e}")
            return []

    async def process_project(self, project: dict):
        project_id = project["id"]
        if project_id in self.processed_projects:
            return

        cahier = project.get("cahier_de_charge", "").strip()
        if not cahier:
            print(f"[CDC] Project '{project['name']}' has no cahier de charge — skipping")
            self.processed_projects.add(project_id)
            return

        sprint = await self.get_sprint_for_project(project_id)
        if not sprint:
            print(f"[CDC] No active sprint for '{project['name']}' — skipping")
            return

        print(f"[CDC] Processing project: {project['name']}")
        tasks_data = self.generate_tasks_from_cdc(project["name"], cahier)

        if not tasks_data:
            print(f"[CDC] No tasks generated for '{project['name']}' — will retry next cycle")
            return  # Don't add to processed_projects so it retries

        created = 0
        for task_data in tasks_data:
            task = await self.create_task(sprint["id"], task_data)
            task_id = task.get("id")
            if not task_id:
                continue
            created += 1

            agent_type = task_data.get("agent_type", "backend")
            await self.post_comment(task_id, f"[CDC] Assigned to {agent_type} agent. Generated from cahier de charge.")

            for sub in task_data.get("subtasks", []):
                subtask = await self.create_task(sprint["id"], sub, parent_task_id=task_id)
                if subtask.get("id"):
                    created += 1
                    await self.post_comment(
                        subtask["id"],
                        f"[CDC] Subtask of '{task_data['title']}'. Assigned to {sub.get('agent_type', agent_type)} agent."
                    )

        print(f"[CDC] Created {created} tasks/subtasks for '{project['name']}'")
        self.processed_projects.add(project_id)

    async def run(self):
        print(f"[CDC] CahierDeChargeAgent started — using Ollama {OLLAMA_MODEL}")
        print(f"[CDC] Watching for active projects...")
        while True:
            try:
                ts = datetime.now(timezone.utc).strftime('%H:%M:%S')
                print(f"[CDC] [{ts}] Scanning for active projects...")
                projects = await self.get_active_projects()
                for project in projects:
                    if project["id"] not in self.processed_projects:
                        await self.process_project(project)
            except Exception as e:
                print(f"[CDC] Error: {e}")
            await asyncio.sleep(30)


if __name__ == "__main__":
    res = httpx.post("http://localhost:8000/api/auth/login", json={
        "email": "admin@nexaforge.com",
        "password": "admin123"
    })
    token = res.json()["access_token"]
    print("[CDC] Token received")

    agent = CahierDeChargeAgent(token=token)
    asyncio.run(agent.run())

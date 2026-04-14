import asyncio
import httpx
import os
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv(os.path.join(os.path.dirname(__file__), "../backend/.env"))

API = "http://localhost:8000"

AGENT_TYPE_MAP = {
    "backend": ["api", "endpoint", "fastapi", "python", "server", "auth", "database schema"],
    "frontend": ["ui", "page", "html", "css", "javascript", "button", "form", "dashboard"],
    "database": ["migration", "query", "sql", "index", "model", "schema", "postgresql", "redis"],
    "devops": ["docker", "ci", "cd", "deploy", "nginx", "pipeline", "github actions", "infra"],
}

SOUL = """
You are Nexus, the Orchestrator Agent for NexaForge.
You analyze sprint goals and create tasks for the right specialists.
Be concise. Always respond with a JSON array of tasks.
"""


class Orchestrator:
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

    def _infer_agent_type(self, title: str, description: str = "") -> str:
        text = (title + " " + (description or "")).lower()
        scores = {agent_type: 0 for agent_type in AGENT_TYPE_MAP}
        for agent_type, keywords in AGENT_TYPE_MAP.items():
            for kw in keywords:
                if kw in text:
                    scores[agent_type] += 1
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else "backend"

    async def get_active_sprints(self):
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{API}/api/sprints/", headers=self.headers)
            sprints = res.json()
            return [s for s in sprints if s["status"] == "active"]

    async def get_tasks_for_sprint(self, sprint_id: str):
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{API}/api/tasks/", headers=self.headers)
            tasks = res.json()
            return [t for t in tasks if t["sprint_id"] == sprint_id]

    async def create_task(self, title: str, description: str, sprint_id: str, priority: str = "medium"):
        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"{API}/api/tasks/",
                headers=self.headers,
                json={
                    "title": title,
                    "description": description,
                    "priority": priority,
                    "sprint_id": sprint_id,
                    "story_points": 3
                }
            )
            return res.json()

    async def promote_approved_tasks(self):
        """Move tasks from peer_review → final_review when all peer comments say APPROVED."""
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{API}/api/tasks/", headers=self.headers)
            tasks = [t for t in res.json() if t["status"] == "peer_review"]

        for task in tasks:
            async with httpx.AsyncClient() as client:
                res = await client.get(f"{API}/api/tasks/{task['id']}/comments", headers=self.headers)
                comments = res.json()

            if not comments:
                continue

            peer_comments = [c for c in comments if "APPROVED" in c["content"] or "CHANGES_NEEDED" in c["content"]]
            if not peer_comments:
                continue

            all_approved = all("APPROVED" in c["content"] and "CHANGES_NEEDED" not in c["content"] for c in peer_comments)
            if all_approved:
                async with httpx.AsyncClient() as client:
                    await client.patch(
                        f"{API}/api/tasks/{task['id']}/status?status=final_review",
                        headers=self.headers
                    )
                print(f"[Nexus] Task '{task['title']}' promoted → final_review")

    async def analyze_sprint_and_create_tasks(self, sprint: dict):
        """Use LLM to suggest tasks for a sprint goal, then create them."""
        goal = sprint.get("goal", "")
        if not goal:
            return

        existing = await self.get_tasks_for_sprint(sprint["id"])
        if len(existing) >= 10:
            return

        prompt = f"""
Sprint goal: {goal}
Existing tasks: {[t['title'] for t in existing]}

Suggest 2-3 new tasks needed to achieve this sprint goal that are NOT already covered.
Respond with a JSON array only, like:
[{{"title": "...", "description": "...", "priority": "medium"}}]
"""

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                res = await client.post(
                    "http://localhost:11434/api/generate",
                    json={"model": "llama3.2:3b", "prompt": SOUL + "\n\n" + prompt, "stream": False}
                )
                raw = res.json()["response"]

            import json, re
            match = re.search(r'\[.*\]', raw, re.DOTALL)
            if not match:
                return
            suggested = json.loads(match.group())

            for item in suggested[:3]:
                task = await self.create_task(
                    title=item["title"],
                    description=item.get("description", ""),
                    sprint_id=sprint["id"],
                    priority=item.get("priority", "medium")
                )
                print(f"[Nexus] Created task: {task['title']}")

        except Exception as e:
            print(f"[Nexus] LLM error: {e}")

    async def run(self):
        print("[Nexus] Orchestrator started")
        while True:
            try:
                print(f"[Nexus] [{datetime.now(timezone.utc).strftime('%H:%M:%S')}] Running orchestration cycle...")

                # Promote peer_review tasks that are fully approved
                await self.promote_approved_tasks()

                # Analyze active sprints and auto-create missing tasks
                sprints = await self.get_active_sprints()
                for sprint in sprints:
                    await self.analyze_sprint_and_create_tasks(sprint)

            except Exception as e:
                print(f"[Nexus] Error: {e}")

            await asyncio.sleep(3600)  # run every hour


if __name__ == "__main__":
    import httpx as _httpx

    res = _httpx.post("http://localhost:8000/api/auth/login", json={
        "email": "admin@nexaforge.com",
        "password": "admin123"
    })
    token = res.json()["access_token"]
    print("Token received ✅")

    orch = Orchestrator(token=token)
    asyncio.run(orch.run())

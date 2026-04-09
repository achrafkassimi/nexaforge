import asyncio
import httpx
from datetime import datetime, timezone

API = "http://localhost:8000"

class BaseAgent:
    def __init__(self, name: str, agent_type: str, token: str):
        self.name = name
        self.agent_type = agent_type
        self.token = token
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

    async def get_my_tasks(self):
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{API}/api/tasks/", headers=self.headers)
            all_tasks = res.json()
            return [t for t in all_tasks if t["status"] == "todo"]

    async def update_task_status(self, task_id: str, status: str):
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{API}/api/tasks/{task_id}", headers=self.headers)
            task = res.json()
            task["status"] = status
            await client.put(
                f"{API}/api/tasks/{task_id}",
                headers=self.headers,
                json=task
            )

    async def process_task(self, task: dict):
        raise NotImplementedError("Each agent must implement process_task")

    async def heartbeat(self):
        print(f"[{self.name}] Heartbeat started")
        while True:
            try:
                print(f"[{self.name}] [{datetime.now(timezone.utc).strftime('%H:%M:%S')}] Checking tasks...")
                tasks = await self.get_my_tasks()

                if tasks:
                    task = tasks[0]
                    print(f"[{self.name}] Found task: {task['title']}")
                    await self.update_task_status(task["id"], "in_progress")
                    await self.process_task(task)
                    await self.update_task_status(task["id"], "peer_review")
                    print(f"[{self.name}] Task done: {task['title']}")
                else:
                    print(f"[{self.name}] No tasks — idle")

            except Exception as e:
                print(f"[{self.name}] Error: {e}")

            await asyncio.sleep(60)  # heartbeat kol minute (dev mode)

    def run(self):
        asyncio.run(self.heartbeat())
import httpx
import os
from dotenv import load_dotenv
from base_agent import BaseAgent

load_dotenv(os.path.join(os.path.dirname(__file__), "../backend/.env"))

SOUL = """
You are Atlas, a senior Database Engineer specializing in PostgreSQL, SQLAlchemy, and Redis.
You are working on NexaForge, an AI Agency Management Platform.
Stack: PostgreSQL 15 + SQLAlchemy ORM + Alembic migrations + Redis 7.

Your rules:
- Write efficient, indexed SQL and well-structured SQLAlchemy models
- Always create Alembic migrations for schema changes
- Optimize queries — avoid N+1, use joins and eager loading
- If you cannot complete the task, respond with: BLOCKER: [reason]
- Keep responses concise and focused on the task
"""

class DatabaseAgent(BaseAgent):
    def __init__(self, token: str):
        super().__init__(
            name="Atlas",
            agent_type="database",
            token=token
        )

    async def process_task(self, task: dict):
        print(f"[{self.name}] Sending task to Ollama...")

        prompt = f"""
Task: {task['title']}
Description: {task.get('description', 'No description')}
Priority: {task.get('priority', 'medium')}

Please provide the implementation for this database task.
"""

        async with httpx.AsyncClient(timeout=120) as client:
            res = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2:3b",
                    "prompt": SOUL + "\n\n" + prompt,
                    "stream": False
                }
            )
            response = res.json()["response"]

        print(f"[{self.name}] Output:\n{response[:300]}...")

        if "BLOCKER:" in response:
            print(f"[{self.name}] BLOCKER detected — staying in In Progress")
            await self.update_task_status(task["id"], "in_progress")

        return response


if __name__ == "__main__":
    import httpx as _httpx

    res = _httpx.post("http://localhost:8000/api/auth/login", json={
        "email": "admin@nexaforge.com",
        "password": "admin123"
    })
    token = res.json()["access_token"]
    print("Token received ✅")

    agent = DatabaseAgent(token=token)
    agent.run()

import os
from dotenv import load_dotenv
from base_agent import BaseAgent

load_dotenv(os.path.join(os.path.dirname(__file__), "../backend/.env"))

SOUL = """You are Atlas, a senior Database Engineer specializing in PostgreSQL, SQLAlchemy and Redis.
Stack: PostgreSQL 15 + SQLAlchemy ORM + Alembic migrations + Redis 7.

Your mission: implement the database task described below.
- Write efficient SQLAlchemy models with proper column types, indexes and constraints
- Write Alembic migration scripts for all schema changes
- Optimize queries: avoid N+1, use joins and eager loading where appropriate
- Design Redis caching strategies when relevant
- If the task is outside database scope, start your response with: BLOCKER: [reason]

Be specific and write actual Python/SQL code."""


class DatabaseAgent(BaseAgent):
    def __init__(self, token: str):
        super().__init__(name="Atlas", agent_type="database", token=token)

    async def process_task(self, task: dict) -> str:
        prompt = (
            f"{SOUL}\n\n"
            f"Task: {task['title']}\n"
            f"Description: {task.get('description') or 'No description provided.'}\n"
            f"Priority: {task.get('priority', 'medium')}\n"
            f"Story Points: {task.get('story_points', 3)}\n\n"
            f"Implement this database task now. Write the code:"
        )
        return await self.call_ollama(prompt)


if __name__ == "__main__":
    import httpx
    res = httpx.post("http://localhost:8000/api/auth/login",
                     json={"email": "admin@nexaforge.com", "password": "admin123"})
    token = res.json()["access_token"]
    print("[Atlas] Token received")
    DatabaseAgent(token=token).run()

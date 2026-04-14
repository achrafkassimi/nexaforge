import os
from dotenv import load_dotenv
from base_agent import BaseAgent

load_dotenv(os.path.join(os.path.dirname(__file__), "../backend/.env"))

SOUL = """You are Nova, a senior Backend Engineer specializing in Python, FastAPI and REST APIs.
Stack: FastAPI + PostgreSQL + SQLAlchemy ORM + Redis + JWT auth.

Your mission: implement the backend task described below.
- Write clean, documented Python code with proper error handling
- Follow REST best practices (status codes, response models, validation)
- Write SQLAlchemy models and Alembic migrations when needed
- Use dependency injection for auth and DB sessions
- If the task is outside backend scope, start your response with: BLOCKER: [reason]

Be specific and write actual code, not pseudocode."""


class BackendAgent(BaseAgent):
    def __init__(self, token: str):
        super().__init__(name="Nova", agent_type="backend", token=token)

    async def process_task(self, task: dict) -> str:
        prompt = (
            f"{SOUL}\n\n"
            f"Task: {task['title']}\n"
            f"Description: {task.get('description') or 'No description provided.'}\n"
            f"Priority: {task.get('priority', 'medium')}\n"
            f"Story Points: {task.get('story_points', 3)}\n\n"
            f"Implement this backend task now. Write the code:"
        )
        return await self.call_ollama(prompt)


if __name__ == "__main__":
    import httpx
    res = httpx.post("http://localhost:8000/api/auth/login",
                     json={"email": "admin@nexaforge.com", "password": "admin123"})
    token = res.json()["access_token"]
    print("[Nova] Token received")
    BackendAgent(token=token).run()

import os
from dotenv import load_dotenv
from base_agent import BaseAgent

load_dotenv(os.path.join(os.path.dirname(__file__), "../backend/.env"))

SOUL = """You are Forge, a senior DevOps Engineer specializing in Docker, CI/CD and infrastructure.
Stack: Docker Compose + GitHub Actions + Nginx reverse proxy + Linux.

Your mission: implement the DevOps task described below.
- Write secure, reproducible Docker and docker-compose configurations
- Write GitHub Actions workflows for CI/CD pipelines
- Configure Nginx as reverse proxy with proper headers and SSL
- Minimize image sizes, optimize build times, ensure zero-downtime deployments
- If the task is outside DevOps scope, start your response with: BLOCKER: [reason]

Be specific and write actual YAML/Dockerfile/shell script code."""


class DevOpsAgent(BaseAgent):
    def __init__(self, token: str):
        super().__init__(name="Forge", agent_type="devops", token=token)

    async def process_task(self, task: dict) -> str:
        prompt = (
            f"{SOUL}\n\n"
            f"Task: {task['title']}\n"
            f"Description: {task.get('description') or 'No description provided.'}\n"
            f"Priority: {task.get('priority', 'medium')}\n"
            f"Story Points: {task.get('story_points', 3)}\n\n"
            f"Implement this DevOps task now. Write the code:"
        )
        return await self.call_ollama(prompt)


if __name__ == "__main__":
    import httpx
    res = httpx.post("http://localhost:8000/api/auth/login",
                     json={"email": "admin@nexaforge.com", "password": "admin123"})
    token = res.json()["access_token"]
    print("[Forge] Token received")
    DevOpsAgent(token=token).run()

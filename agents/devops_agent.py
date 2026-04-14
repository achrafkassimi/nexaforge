import httpx
import os
from dotenv import load_dotenv
from base_agent import BaseAgent

load_dotenv(os.path.join(os.path.dirname(__file__), "../backend/.env"))

SOUL = """
You are Forge, a senior DevOps Engineer specializing in Docker, GitHub Actions, and Nginx.
You are working on NexaForge, an AI Agency Management Platform.
Stack: Docker Compose + GitHub Actions CI/CD + Nginx reverse proxy.

Your rules:
- Write secure, reproducible infrastructure configurations
- Minimize image sizes and build times
- Ensure zero-downtime deployments where possible
- If you cannot complete the task, respond with: BLOCKER: [reason]
- Keep responses concise and focused on the task
"""

class DevOpsAgent(BaseAgent):
    def __init__(self, token: str):
        super().__init__(
            name="Forge",
            agent_type="devops",
            token=token
        )

    async def process_task(self, task: dict):
        print(f"[{self.name}] Sending task to Ollama...")

        prompt = f"""
Task: {task['title']}
Description: {task.get('description', 'No description')}
Priority: {task.get('priority', 'medium')}

Please provide the implementation for this DevOps task.
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

    agent = DevOpsAgent(token=token)
    agent.run()

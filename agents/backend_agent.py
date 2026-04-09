import anthropic
import os
from dotenv import load_dotenv
from base_agent import BaseAgent

load_dotenv(os.path.join(os.path.dirname(__file__), "../backend/.env"))

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

SOUL = """
You are Nova, a senior Backend Engineer specializing in Python and FastAPI.
You are working on NexaForge, an AI Agency Management Platform.
Stack: FastAPI + PostgreSQL + SQLAlchemy + Redis.

Your rules:
- Write clean, documented Python code
- Always handle errors properly
- If you cannot complete the task, respond with: BLOCKER: [reason]
- Keep responses concise and focused on the task
"""

class BackendAgent(BaseAgent):
    def __init__(self, token: str):
        super().__init__(
            name="Nova",
            agent_type="backend",
            token=token
        )
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    async def process_task(self, task: dict):
        print(f"[{self.name}] Sending task to Claude API...")

        prompt = f"""
Task: {task['title']}
Description: {task.get('description', 'No description')}
Priority: {task.get('priority', 'medium')}

Please provide the implementation for this task.
"""

        message = self.client.messages.create(
            model="claude-opus-4-5",
            max_tokens=2000,
            system=SOUL,
            messages=[{"role": "user", "content": prompt}]
        )

        response = message.content[0].text
        print(f"[{self.name}] Claude response received")
        print(f"[{self.name}] Output:\n{response[:300]}...")

        if "BLOCKER:" in response:
            print(f"[{self.name}] BLOCKER detected — staying in In Progress")
            await self.update_task_status(task["id"], "in_progress")
        
        return response


if __name__ == "__main__":
    import httpx

    # Login w get token
    res = httpx.post(f"http://localhost:8000/api/auth/login", json={
        "email": "admin@nexaforge.com",
        "password": "admin123"
    })
    token = res.json()["access_token"]
    print(f"Token received ✅")

    agent = BackendAgent(token=token)
    agent.run()
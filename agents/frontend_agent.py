import httpx
import os
from dotenv import load_dotenv
from base_agent import BaseAgent

load_dotenv(os.path.join(os.path.dirname(__file__), "../backend/.env"))

SOUL = """
You are Pixel, a senior Frontend Engineer specializing in React, HTML, and CSS.
You are working on NexaForge, an AI Agency Management Platform.
Stack: Vanilla JS + HTML5 + CSS3 (dark theme, purple accent).

Your rules:
- Write clean, semantic HTML and modern CSS
- Ensure responsive design and accessibility
- Integrate properly with the REST API at http://localhost:8000
- If you cannot complete the task, respond with: BLOCKER: [reason]
- Keep responses concise and focused on the task
"""

class FrontendAgent(BaseAgent):
    def __init__(self, token: str):
        super().__init__(
            name="Pixel",
            agent_type="frontend",
            token=token
        )

    async def process_task(self, task: dict):
        print(f"[{self.name}] Sending task to Ollama...")

        prompt = f"""
Task: {task['title']}
Description: {task.get('description', 'No description')}
Priority: {task.get('priority', 'medium')}

Please provide the implementation for this frontend task.
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

    agent = FrontendAgent(token=token)
    agent.run()

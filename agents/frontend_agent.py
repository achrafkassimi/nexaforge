import os
from dotenv import load_dotenv
from base_agent import BaseAgent

load_dotenv(os.path.join(os.path.dirname(__file__), "../backend/.env"))

SOUL = """You are Pixel, a senior Frontend Engineer specializing in HTML, CSS and Vanilla JavaScript.
Stack: HTML5 + CSS3 (dark theme, purple accent #8b5cf6) + Vanilla JS + REST API at http://localhost:8000.

Your mission: implement the frontend task described below.
- Write semantic HTML with proper structure
- Write modern CSS using CSS variables (--purple, --bg, --bg2, --border, --text, --muted)
- Write clean Vanilla JS with fetch() calls to the API, using Bearer token from localStorage
- Ensure responsive design and good UX
- If the task is outside frontend scope, start your response with: BLOCKER: [reason]

Be specific and write actual HTML/CSS/JS code, not descriptions."""


class FrontendAgent(BaseAgent):
    def __init__(self, token: str):
        super().__init__(name="Pixel", agent_type="frontend", token=token)

    async def process_task(self, task: dict) -> str:
        prompt = (
            f"{SOUL}\n\n"
            f"Task: {task['title']}\n"
            f"Description: {task.get('description') or 'No description provided.'}\n"
            f"Priority: {task.get('priority', 'medium')}\n"
            f"Story Points: {task.get('story_points', 3)}\n\n"
            f"Implement this frontend task now. Write the code:"
        )
        return await self.call_ollama(prompt)


if __name__ == "__main__":
    import httpx
    res = httpx.post("http://localhost:8000/api/auth/login",
                     json={"email": "admin@nexaforge.com", "password": "admin123"})
    token = res.json()["access_token"]
    print("[Pixel] Token received")
    FrontendAgent(token=token).run()

import asyncio
import httpx
import os
import re
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../backend/.env"))

API            = "http://localhost:8000"
OLLAMA_URL     = os.getenv("OLLAMA_URL",   "http://localhost:11434")
OLLAMA_MODEL   = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
WORKSPACE_ROOT = os.path.join(os.path.dirname(__file__), "..", "workspace")

# File extensions by agent type
AGENT_EXT = {
    "backend":  ".py",
    "frontend": ".html",
    "database": ".py",
    "devops":   ".yml",
}


def slugify(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    return slug[:48]


def task_filename(task_title: str, agent_type: str) -> str:
    slug = slugify(task_title)
    ext  = AGENT_EXT.get(agent_type, ".md")
    return f"{slug}{ext}"


class BaseAgent:
    def __init__(self, name: str, agent_type: str, token: str):
        self.name       = name
        self.agent_type = agent_type
        self.token      = token
        self.headers    = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

    async def get_my_tasks(self):
        """Get todo tasks assigned to this agent's type."""
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{API}/api/tasks/", headers=self.headers)
            all_tasks = res.json()
            return [
                t for t in all_tasks
                if t["status"] == "todo" and t.get("agent_type") == self.agent_type
            ]

    async def get_peer_review_tasks(self):
        """Get peer_review tasks from OTHER agent types."""
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{API}/api/tasks/", headers=self.headers)
            all_tasks = res.json()
            return [
                t for t in all_tasks
                if t["status"] == "peer_review" and t.get("agent_type") != self.agent_type
            ]

    async def get_task_comments(self, task_id: str) -> list:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{API}/api/tasks/{task_id}/comments", headers=self.headers)
            return res.json() if res.status_code == 200 else []

    async def post_comment(self, task_id: str, content: str):
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{API}/api/tasks/{task_id}/comments",
                headers=self.headers,
                json={"content": content}
            )

    async def already_reviewed(self, task_id: str) -> bool:
        comments = await self.get_task_comments(task_id)
        marker = f"[{self.name}]"
        return any(marker in c["content"] for c in comments)

    async def update_task_status(self, task_id: str, status: str):
        async with httpx.AsyncClient() as client:
            await client.patch(
                f"{API}/api/tasks/{task_id}/status?status={status}",
                headers=self.headers
            )
            print(f"[{self.name}] Status → {status}")

    async def get_sprint(self, sprint_id: str) -> dict:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{API}/api/sprints/", headers=self.headers)
            for s in res.json():
                if s["id"] == sprint_id:
                    return s
        return {}

    async def get_project(self, project_id: str) -> dict:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{API}/api/projects/{project_id}", headers=self.headers)
            return res.json() if res.status_code == 200 else {}

    def save_output_to_file(self, project_name: str, project_id: str, task_title: str, output: str):
        """Save agent output to the project workspace file."""
        try:
            slug      = slugify(project_name) + "-" + project_id[:8]
            workspace = os.path.join(WORKSPACE_ROOT, slug)
            if not os.path.isdir(workspace):
                return  # workspace not created yet (project not started)

            agent_dir = os.path.join(workspace, self.agent_type)
            os.makedirs(agent_dir, exist_ok=True)

            filename = task_filename(task_title, self.agent_type)
            filepath = os.path.join(agent_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# {task_title}\n")
                f.write(f"# Agent: {self.name} ({self.agent_type})\n")
                f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(output)

            print(f"[{self.name}] Saved output → workspace/{slug}/{self.agent_type}/{filename}")
        except Exception as e:
            print(f"[{self.name}] Warning: could not save file: {e}")

    async def call_ollama(self, prompt: str) -> str:
        """Call Ollama and return the response text."""
        try:
            async with httpx.AsyncClient(timeout=180) as client:
                res = await client.post(
                    f"{OLLAMA_URL}/api/generate",
                    json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
                )
                if res.status_code == 404:
                    return f"BLOCKER: Model '{OLLAMA_MODEL}' not found. Run: ollama pull {OLLAMA_MODEL}"
                return res.json().get("response", "").strip()
        except Exception as e:
            return f"BLOCKER: Cannot reach Ollama at {OLLAMA_URL}: {e}"

    async def process_task(self, task: dict) -> str:
        """Subclasses must implement this. Returns the output string."""
        raise NotImplementedError(f"[{self.name}] process_task not implemented for task: {task['title']}")

    async def review_task(self, task: dict) -> str:
        """Peer review: look at the task output and post verdict."""
        comments = await self.get_task_comments(task["id"])
        output_comments = [
            c for c in comments
            if len(c.get("content", "")) > 30 and not c["content"].startswith("[CDC]")
        ]

        if output_comments:
            verdict = f"[{self.name}] APPROVED — output reviewed and looks good."
        else:
            verdict = f"[{self.name}] CHANGES_NEEDED: No implementation output found in task comments."

        await self.post_comment(task["id"], verdict)
        print(f"[{self.name}] Reviewed '{task['title']}': {'APPROVED' if 'APPROVED' in verdict else 'CHANGES_NEEDED'}")
        return verdict

    async def heartbeat(self):
        print(f"[{self.name}] Agent started — type={self.agent_type}, model={OLLAMA_MODEL}")
        while True:
            try:
                ts = datetime.now(timezone.utc).strftime('%H:%M:%S')
                print(f"[{self.name}] [{ts}] Checking {self.agent_type} tasks...")

                tasks = await self.get_my_tasks()
                if tasks:
                    task = tasks[0]
                    print(f"[{self.name}] Picked up: {task['title']}")
                    await self.update_task_status(task["id"], "in_progress")
                    output = await self.process_task(task)

                    if output:
                        await self.post_comment(task["id"], f"[{self.name}] Output:\n{output}")

                        # Save output to workspace file
                        sprint  = await self.get_sprint(str(task.get("sprint_id", "")))
                        if sprint.get("project_id"):
                            project = await self.get_project(str(sprint["project_id"]))
                            if project.get("name"):
                                self.save_output_to_file(
                                    project_name=project["name"],
                                    project_id=str(project["id"]),
                                    task_title=task["title"],
                                    output=output
                                )

                    if output and "BLOCKER:" not in output:
                        await self.update_task_status(task["id"], "peer_review")
                        print(f"[{self.name}] Done → peer_review: {task['title']}")
                    else:
                        print(f"[{self.name}] BLOCKER on '{task['title']}' — left in_progress")

                else:
                    peer_tasks = await self.get_peer_review_tasks()
                    reviewed = 0
                    for task in peer_tasks:
                        if not await self.already_reviewed(task["id"]):
                            await self.review_task(task)
                            reviewed += 1
                            break

                    if reviewed == 0:
                        print(f"[{self.name}] No tasks — idle")

            except Exception as e:
                print(f"[{self.name}] Error: {e}")

            await asyncio.sleep(60)

    def run(self):
        asyncio.run(self.heartbeat())

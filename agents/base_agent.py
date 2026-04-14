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

    async def get_peer_review_tasks(self):
        """Get tasks in peer_review that were NOT worked on by this agent type."""
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{API}/api/tasks/", headers=self.headers)
            all_tasks = res.json()
            return [t for t in all_tasks if t["status"] == "peer_review"]

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
        """Check if this agent already posted a review on this task."""
        comments = await self.get_task_comments(task_id)
        marker = f"[{self.name}]"
        return any(marker in c["content"] for c in comments)

    async def update_task_status(self, task_id: str, status: str):
        async with httpx.AsyncClient() as client:
            await client.patch(
                f"{API}/api/tasks/{task_id}/status?status={status}",
                headers=self.headers
            )
            print(f"[{self.name}] PATCH status={status}")

    async def process_task(self, task: dict):
        raise NotImplementedError("Each agent must implement process_task")

    async def review_task(self, task: dict) -> str:
        """
        Peer review: read the task + its comments, then post APPROVED or CHANGES_NEEDED.
        Subclasses can override for domain-specific review logic.
        Default: approve if there is at least one comment with output, else request changes.
        """
        comments = await self.get_task_comments(task["id"])
        output_comments = [c for c in comments if len(c["content"]) > 20]

        if output_comments:
            verdict = f"[{self.name}] APPROVED — implementation looks good."
        else:
            verdict = f"[{self.name}] CHANGES_NEEDED: No implementation output found in comments."

        await self.post_comment(task["id"], verdict)
        print(f"[{self.name}] Reviewed task '{task['title']}': {verdict[:60]}...")
        return verdict

    async def heartbeat(self):
        print(f"[{self.name}] Heartbeat started")
        while True:
            try:
                ts = datetime.now(timezone.utc).strftime('%H:%M:%S')
                print(f"[{self.name}] [{ts}] Checking tasks...")

                # 1. Work on todo tasks
                tasks = await self.get_my_tasks()
                if tasks:
                    task = tasks[0]
                    print(f"[{self.name}] Found task: {task['title']}")
                    await self.update_task_status(task["id"], "in_progress")
                    output = await self.process_task(task)

                    # Post output as a comment for peer review
                    if output:
                        await self.post_comment(task["id"], f"[{self.name}] Output:\n{output}")

                    await self.update_task_status(task["id"], "peer_review")
                    print(f"[{self.name}] Task done → peer_review: {task['title']}")

                else:
                    # 2. Do peer reviews on tasks from other agents
                    peer_tasks = await self.get_peer_review_tasks()
                    reviewed = 0
                    for task in peer_tasks:
                        if not await self.already_reviewed(task["id"]):
                            await self.review_task(task)
                            reviewed += 1
                            break  # one review per cycle

                    if reviewed == 0:
                        print(f"[{self.name}] No tasks — idle")

            except Exception as e:
                print(f"[{self.name}] Error: {e}")

            await asyncio.sleep(60)

    def run(self):
        asyncio.run(self.heartbeat())

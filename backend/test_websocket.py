import asyncio
import websockets
import json
import httpx

BASE = "http://localhost:8000"

async def test_websocket():
    # 1 - Login
    res = httpx.post(f"{BASE}/api/auth/login", json={
        "email": "admin@nexaforge.com",
        "password": "admin123"
    })
    token = res.json()["access_token"]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    print("Login ✅")

    # 2 - Connect WebSocket
    async with websockets.connect("ws://localhost:8000/ws/dashboard") as ws:
        print("WebSocket connected ✅")

        # 3 - Get sprint id
        res = httpx.get(f"{BASE}/api/sprints/", headers=headers)
        sprint_id = res.json()[0]["id"]

        # 4 - Create task
        res = httpx.post(f"{BASE}/api/tasks/", headers=headers, json={
            "title": "Test WebSocket task",
            "description": "Testing real-time updates",
            "priority": "high",
            "story_points": 2,
            "sprint_id": sprint_id
        })
        task_id = res.json()["id"]
        print(f"Task created: {task_id}")

        # 5 - Update task status → listen for WS message
        print("Updating task status → todo...")
        res = httpx.put(f"{BASE}/api/tasks/{task_id}", headers=headers, json={
            "title": "Test WebSocket task",
            "description": "Testing real-time updates",
            "priority": "high",
            "story_points": 2,
            "sprint_id": sprint_id,
            "status": "todo"
        })

        # 6 - Wait for WS message
        print("Waiting for WebSocket message...")
        message = await asyncio.wait_for(ws.recv(), timeout=5)
        data = json.loads(message)
        print(f"WS message received ✅: {data}")

asyncio.run(test_websocket())
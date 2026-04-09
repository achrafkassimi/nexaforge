import httpx

BASE = "http://localhost:8000"

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

# 2 - Get sprint id
res = httpx.get(f"{BASE}/api/sprints/", headers=headers)
sprint_id = res.json()[0]["id"]
print(f"Sprint ID: {sprint_id}")

# 3 - Create task
res = httpx.post(f"{BASE}/api/tasks/", headers=headers, json={
    "title": "Create health check endpoint",
    "description": "Add a /api/health endpoint that returns system status",
    "priority": "medium",
    "story_points": 1,
    "sprint_id": sprint_id
})
task = res.json()
task_id = task["id"]
print(f"Task created: {task_id}")

# # 4 - Update status to todo
# res = httpx.put(f"{BASE}/api/tasks/{task_id}", headers=headers, json={
#     "title": task["title"],
#     "description": task["description"],
#     "priority": task["priority"],
#     "story_points": task["story_points"],
#     "sprint_id": task["sprint_id"],
#     "status": "todo"
# })

# 4 - Update status to todo
res = httpx.patch(
    f"{BASE}/api/tasks/{task_id}/status",
    headers=headers,
    params={"status": "todo"}
)
print(f"Task status → {res.json()['status']} ✅")


print(f"Task status → todo ✅")
print(f"Task ready — tsenna l'agent yb3atha lil Ollama 🚀")
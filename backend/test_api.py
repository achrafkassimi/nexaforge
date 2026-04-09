# import requests

# BASE = "http://localhost:8000"

# # 1 - Register
# r = requests.post(f"{BASE}/api/auth/register", json={
#     "email": "admin@nexaforge.com",
#     "password": "admin123",
#     "full_name": "Achraf Kassimi",
#     "role": "super_admin"
# })
# print("Register:", r.status_code, r.json())

# # 2 - Login
# r = requests.post(f"{BASE}/api/auth/login", json={
#     "email": "admin@nexaforge.com",
#     "password": "admin123"
# })
# print("Login:", r.status_code, r.json())

# # 3 - Create project
# r = requests.post(f"{BASE}/api/projects", json={
#     "name": "NexaForge Platform",
#     "description": "AI Agency Management Platform",
#     "priority": "high"
# })
# print("Create project:", r.status_code, r.json())
# project_id = r.json()["id"]

# # 4 - Create agent
# r = requests.post(f"{BASE}/api/agents", json={
#     "name": "Atlas",
#     "agent_type": "database"
# })
# print("Create agent:", r.status_code, r.json())

# # 5 - Get all projects
# r = requests.get(f"{BASE}/api/projects")
# print("Get projects:", r.status_code, r.json())

# # 6 - Get all agents
# r = requests.get(f"{BASE}/api/agents")
# print("Get agents:", r.status_code, r.json())

# -------------------------------------------------------------------------------

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
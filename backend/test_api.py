import requests

BASE = "http://localhost:8000"

# 1 - Register
r = requests.post(f"{BASE}/api/auth/register", json={
    "email": "admin@nexaforge.com",
    "password": "admin123",
    "full_name": "Achraf Kassimi",
    "role": "super_admin"
})
print("Register:", r.status_code, r.json())

# 2 - Login
r = requests.post(f"{BASE}/api/auth/login", json={
    "email": "admin@nexaforge.com",
    "password": "admin123"
})
print("Login:", r.status_code, r.json())

# 3 - Create project
r = requests.post(f"{BASE}/api/projects", json={
    "name": "NexaForge Platform",
    "description": "AI Agency Management Platform",
    "priority": "high"
})
print("Create project:", r.status_code, r.json())
project_id = r.json()["id"]

# 4 - Create agent
r = requests.post(f"{BASE}/api/agents", json={
    "name": "Atlas",
    "agent_type": "database"
})
print("Create agent:", r.status_code, r.json())

# 5 - Get all projects
r = requests.get(f"{BASE}/api/projects")
print("Get projects:", r.status_code, r.json())

# 6 - Get all agents
r = requests.get(f"{BASE}/api/agents")
print("Get agents:", r.status_code, r.json())
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from models.project import Project
from models.sprint import Sprint
from schemas.project import ProjectCreate, ProjectOut
from services.auth_service import decode_token
from typing import List
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ws_manager.manager import manager

WORKSPACE_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "workspace")


def slugify(name: str) -> str:
    """Convert project name to a safe directory name."""
    slug = name.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    return slug[:48]


def create_project_workspace(project_id: str, project_name: str, cahier_de_charge: str = "") -> str:
    """Create the project workspace directory structure. Returns the workspace path."""
    slug = slugify(project_name) + "-" + str(project_id)[:8]
    workspace = os.path.join(WORKSPACE_ROOT, slug)

    subdirs = ["backend", "frontend", "database", "devops", "docs", "tests"]
    for d in subdirs:
        os.makedirs(os.path.join(workspace, d), exist_ok=True)

    # README
    with open(os.path.join(workspace, "README.md"), "w", encoding="utf-8") as f:
        f.write(f"# {project_name}\n\n")
        f.write(f"Project ID: `{project_id}`\n\n")
        f.write("## Structure\n")
        f.write("```\n")
        for d in subdirs:
            f.write(f"{d}/\n")
        f.write("```\n")

    # Cahier de charge
    if cahier_de_charge:
        with open(os.path.join(workspace, "docs", "cahier_de_charge.md"), "w", encoding="utf-8") as f:
            f.write(f"# Cahier de Charge — {project_name}\n\n")
            f.write(cahier_de_charge)

    # .gitignore
    with open(os.path.join(workspace, ".gitignore"), "w", encoding="utf-8") as f:
        f.write("__pycache__/\n*.pyc\n.env\nnode_modules/\n.DS_Store\n")

    return workspace

router = APIRouter(prefix="/api/projects", tags=["projects"])
security = HTTPBearer(auto_error=False)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        return decode_token(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/", response_model=List[ProjectOut])
def get_projects(db: Session = Depends(get_db)):
    return db.query(Project).all()


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/", response_model=ProjectOut)
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(**data.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(project_id: str, data: ProjectCreate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    for key, value in data.model_dump().items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}")
def delete_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"message": "Project deleted"}


# ─── Workflow endpoints ──────────────────────────────────────────────────────

@router.post("/{project_id}/submit", response_model=ProjectOut)
async def submit_for_approval(
    project_id: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Chef de projet submits the cahier de charge for super_admin review."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.status != "draft":
        raise HTTPException(status_code=400, detail=f"Cannot submit from status '{project.status}'")
    if not project.cahier_de_charge:
        raise HTTPException(status_code=400, detail="Cahier de charge is required before submitting")
    project.status = "pending_approval"
    db.commit()
    db.refresh(project)
    await manager.broadcast("dashboard", {
        "type": "project_submitted",
        "project_id": str(project.id),
        "name": project.name
    })
    return project


@router.post("/{project_id}/approve", response_model=ProjectOut)
async def approve_project(
    project_id: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Super admin approves the cahier de charge."""
    if user.get("role") != "super_admin":
        raise HTTPException(status_code=403, detail="Only super_admin can approve projects")
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.status != "pending_approval":
        raise HTTPException(status_code=400, detail=f"Cannot approve from status '{project.status}'")
    project.status = "approved"
    project.rejection_note = None
    db.commit()
    db.refresh(project)
    await manager.broadcast("dashboard", {
        "type": "project_approved",
        "project_id": str(project.id),
        "name": project.name
    })
    return project


@router.post("/{project_id}/reject", response_model=ProjectOut)
async def reject_project(
    project_id: str,
    reason: str = "No reason provided",
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Super admin rejects the cahier de charge with a reason."""
    if user.get("role") != "super_admin":
        raise HTTPException(status_code=403, detail="Only super_admin can reject projects")
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.status != "pending_approval":
        raise HTTPException(status_code=400, detail=f"Cannot reject from status '{project.status}'")
    project.status = "draft"
    project.rejection_note = reason
    db.commit()
    db.refresh(project)
    await manager.broadcast("dashboard", {
        "type": "project_rejected",
        "project_id": str(project.id),
        "name": project.name,
        "reason": reason
    })
    return project


@router.post("/{project_id}/start", response_model=ProjectOut)
async def start_project(
    project_id: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Start an approved project:
    1. Creates Sprint 1
    2. Marks project as active
    3. Broadcasts to agents — CDC Agent picks it up and generates tasks
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.status != "approved":
        raise HTTPException(status_code=400, detail=f"Cannot start from status '{project.status}'")

    # Create Sprint 1 automatically
    sprint = Sprint(
        name=f"Sprint 1 — {project.name}",
        goal=f"Implement the first deliverables for: {project.name}",
        status="active",
        project_id=project.id
    )
    db.add(sprint)
    project.status = "active"
    db.commit()
    db.refresh(project)
    db.refresh(sprint)

    # Create workspace directory structure
    try:
        workspace = create_project_workspace(
            project_id=str(project.id),
            project_name=project.name,
            cahier_de_charge=project.cahier_de_charge or ""
        )
        print(f"[Projects] Workspace created: {workspace}")
    except Exception as e:
        print(f"[Projects] Warning: could not create workspace: {e}")

    await manager.broadcast("dashboard", {
        "type": "project_started",
        "project_id": str(project.id),
        "sprint_id": str(sprint.id),
        "name": project.name
    })
    return project

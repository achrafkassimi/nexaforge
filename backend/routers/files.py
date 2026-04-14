"""
Files router — list and read project workspace files.
Workspace: nexaforge/workspace/{project-slug}-{id[:8]}/
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
import os
import re

router = APIRouter(prefix="/api/files", tags=["files"])

WORKSPACE_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "workspace")

BINARY_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".zip", ".tar", ".gz", ".exe"}


def slugify(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    return slug[:48]


def find_workspace(project_id: str, project_name: str) -> str | None:
    """Find the workspace directory for a project."""
    slug = slugify(project_name) + "-" + project_id[:8]
    path = os.path.join(WORKSPACE_ROOT, slug)
    return path if os.path.isdir(path) else None


def safe_path(workspace: str, rel: str) -> str:
    """Resolve a relative path within workspace, raising 403 on traversal."""
    full = os.path.abspath(os.path.join(workspace, rel.lstrip("/")))
    if not full.startswith(os.path.abspath(workspace)):
        raise HTTPException(status_code=403, detail="Path traversal not allowed")
    return full


def list_dir_tree(base: str, rel: str = "") -> list:
    """Return a flat list of {path, name, type, size} dicts."""
    result = []
    current = os.path.join(base, rel) if rel else base
    try:
        entries = sorted(os.listdir(current), key=lambda x: (os.path.isfile(os.path.join(current, x)), x))
    except PermissionError:
        return result

    for entry in entries:
        if entry.startswith("."):
            continue
        full    = os.path.join(current, entry)
        rel_path = (rel + "/" + entry).lstrip("/") if rel else entry
        if os.path.isdir(full):
            result.append({"path": rel_path, "name": entry, "type": "dir", "size": 0})
            result.extend(list_dir_tree(base, rel_path))
        else:
            result.append({
                "path": rel_path,
                "name": entry,
                "type": "file",
                "size": os.path.getsize(full),
                "ext":  os.path.splitext(entry)[1].lower()
            })
    return result


@router.get("/{project_id}")
def list_files(project_id: str, project_name: str):
    """List all files in the project workspace."""
    workspace = find_workspace(project_id, project_name)
    if not workspace:
        return {"exists": False, "files": []}
    return {"exists": True, "workspace": workspace, "files": list_dir_tree(workspace)}


@router.get("/{project_id}/content")
def read_file(project_id: str, project_name: str, path: str):
    """Read the content of a specific file."""
    workspace = find_workspace(project_id, project_name)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    full = safe_path(workspace, path)
    if not os.path.isfile(full):
        raise HTTPException(status_code=404, detail="File not found")

    ext = os.path.splitext(full)[1].lower()
    if ext in BINARY_EXTS:
        raise HTTPException(status_code=400, detail="Binary file — cannot display")

    try:
        with open(full, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        return {"path": path, "content": content, "size": len(content)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.task import Task
from models.task_comment import TaskComment
from schemas.task import TaskCreate, TaskOut
from schemas.task_comment import TaskCommentCreate, TaskCommentOut
from typing import List
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ws_manager.manager import manager

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.get("/", response_model=List[TaskOut])
def get_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()

@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/", response_model=TaskOut)
def create_task(data: TaskCreate, db: Session = Depends(get_db)):
    task = Task(**data.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

# @router.put("/{task_id}", response_model=TaskOut)
# def update_task(task_id: str, data: TaskCreate, db: Session = Depends(get_db)):
#     task = db.query(Task).filter(Task.id == task_id).first()
#     if not task:
#         raise HTTPException(status_code=404, detail="Task not found")
#     for key, value in data.model_dump().items():
#         setattr(task, key, value)
#     db.commit()
#     db.refresh(task)
#     return task

@router.put("/{task_id}", response_model=TaskOut)
async def update_task(task_id: str, data: TaskCreate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in data.model_dump().items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)

    # Broadcast real-time
    await manager.broadcast("dashboard", {
        "type": "task_updated",
        "task_id": str(task.id),
        "title": task.title,
        "status": task.status
    })

    return task

@router.patch("/{task_id}/status")
async def update_task_status(task_id: str, status: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = status
    db.commit()
    db.refresh(task)

    await manager.broadcast("dashboard", {
        "type": "task_updated",
        "task_id": str(task.id),
        "title": task.title,
        "status": task.status
    })

    return task

@router.delete("/{task_id}")
def delete_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"message": "Task deleted"}


@router.get("/{task_id}/comments", response_model=List[TaskCommentOut])
def get_task_comments(task_id: str, db: Session = Depends(get_db)):
    return db.query(TaskComment).filter(TaskComment.task_id == task_id).order_by(TaskComment.created_at).all()


@router.post("/{task_id}/comments", response_model=TaskCommentOut)
async def create_task_comment(task_id: str, data: TaskCommentCreate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    comment = TaskComment(task_id=task_id, **data.model_dump())
    db.add(comment)
    db.commit()
    db.refresh(comment)

    await manager.broadcast("dashboard", {
        "type": "task_comment",
        "task_id": task_id,
        "content": comment.content
    })

    return comment
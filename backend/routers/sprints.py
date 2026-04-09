from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.sprint import Sprint
from schemas.sprint import SprintCreate, SprintOut
from typing import List

router = APIRouter(prefix="/api/sprints", tags=["sprints"])

@router.get("/", response_model=List[SprintOut])
def get_sprints(db: Session = Depends(get_db)):
    return db.query(Sprint).all()

@router.post("/", response_model=SprintOut)
def create_sprint(data: SprintCreate, db: Session = Depends(get_db)):
    sprint = Sprint(**data.model_dump())
    db.add(sprint)
    db.commit()
    db.refresh(sprint)
    return sprint
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import Task, User
from app.schemas import TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)) -> Task:
    if not db.get(User, payload.owner_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Owner not found")
    task = Task(title=payload.title, description=payload.description, owner_id=payload.owner_id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("", response_model=list[TaskRead])
def list_tasks(owner_id: int | None = None, db: Session = Depends(get_db)) -> list[Task]:
    stmt = select(Task)
    if owner_id is not None:
        stmt = stmt.where(Task.owner_id == owner_id)
    return list(db.scalars(stmt))


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)) -> Task:
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")
    return task


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)) -> Task:
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task

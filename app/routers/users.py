from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import User
from app.schemas import UserCreate, UserRead
from app.security import hash_password

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    if db.scalar(select(User).where(User.email == payload.email)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
    user = User(
        email=payload.email,
        username=payload.username,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db)) -> list[User]:
    return list(db.scalars(select(User)))


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return user

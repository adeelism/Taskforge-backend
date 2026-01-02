from app.auth.schemas import SignupRequest
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.core.security import hash_password
from app.models import User

def create_user(request: SignupRequest, db: Session) -> User:
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    hashed_password = hash_password(request.password)
    new_user = User(
        username=request.username,
        full_name=request.full_name,
        email=request.email,
        hashed_password=hashed_password
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)  # load id
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user")

    return new_user

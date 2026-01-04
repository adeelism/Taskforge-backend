from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.auth.dependencies import oauth2_scheme, decode_access_token
from app.database import SessionLocal
from app.models import User

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    user_id = payload["sub"]
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User Not found")
    return user

def admin_required(current_user: User = Depends(
    get_current_user)) -> User:  # for future permission based access if a route requires an admin role
    if current_user.global_role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an administrator")
    return current_user


def manager_required(current_user: User = Depends(get_current_user)) -> User: # for future permission based access if a route requires a manager role
    if current_user.global_role != "manager":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a manager")
    return current_user

from datetime import timedelta, datetime, timezone
from jose import jwt
from app.auth.schemas import SignupRequest, LoginRequest
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.core.security import hash_password, verify_password
from app.models import User
from app.core.config import settings
from uuid import uuid4
from typing import cast, Optional


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


def create_access_token(
        *,
        # this * indicates that the arguments passed to this function when calling it will be in keywords. Meaning it can't be called casually, you need to pass keyword with value.
        user_id: int,
        role: str,
) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),  # stable identifier
        "role": role,  # authorization
        "iat": int(now.timestamp()),  # issued at
        "nbf": int(now.timestamp()),  # not before
        "exp": int((now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
        "jti": str(uuid4()),  # token id (future revocation)
    }

    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    return token


def authenticate_user(*, request: LoginRequest, db: Session) -> User:
    user: Optional[User] = db.query(User).filter(User.email == request.email).first()
    hashed_pw: str = cast(str, user.hashed_password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_NOT_FOUND, detail="Invalid Credentials")
    if not verify_password(request.password, hashed_pw):
        raise HTTPException(status_code=status.HTTP_401_NOT_FOUND, detail="Invalid Credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return user

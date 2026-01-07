from fastapi import APIRouter, status, Depends, HTTPException
from app.auth.services import create_user, create_access_token, authenticate_user, create_refresh_token, \
    refresh_access_token, logout_refresh_token
from typing import Annotated
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dependencies import get_db
from app.auth.schemas import SignupRequest, Token, LoginRequest, RefreshTokenRequest

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

db_dependency = Annotated[Session, Depends(get_db)]


@router.post('/signup', response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(db: db_dependency, request: SignupRequest):
    user = create_user(db=db, request=request)
    access_token = create_access_token(user_id=user.id, role=user.global_role.value)
    refresh_token = create_refresh_token(user_id=user.id, db=db)
    return {"access_token": access_token,
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "refresh_token": refresh_token,
            "refresh_expires_in": settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            "token_type": "bearer"}


@router.post('/login', response_model=Token, status_code=status.HTTP_200_OK)
def login(db: db_dependency, request: LoginRequest):
    user = authenticate_user(db=db, request=request)
    access_token = create_access_token(user_id=user.id, role=user.global_role.value)
    refresh_token = create_refresh_token(user_id=user.id, db=db)
    return {"access_token": access_token,
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "refresh_token": refresh_token,
            "refresh_expires_in": settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            "token_type": "bearer"}

@router.post('/refresh', response_model=Token, status_code=status.HTTP_201_CREATED)
def refresh(db: db_dependency, request: RefreshTokenRequest):
    return refresh_access_token(db=db, request=request.refresh_token)

@router.post('/logout', status_code=status.HTTP_204_NO_CONTENT)
def logout(request: RefreshTokenRequest,db: db_dependency) -> None:
    # logs out user by revoking the refresh token
    return logout_refresh_token(request.refresh_token, db=db)
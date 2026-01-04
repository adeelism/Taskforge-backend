from fastapi import APIRouter, status, Depends, HTTPException
from app.auth.services import create_user, create_access_token, authenticate_user
from typing import Annotated
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.auth.schemas import SignupRequest, Token, LoginRequest

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

db_dependency = Annotated[Session, Depends(get_db)]


@router.post('/signup', response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(db: db_dependency, request: SignupRequest):
    user = create_user(db=db, request=request)
    access_token = create_access_token(user_id=user.id, role=user.global_role.value)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post('/login',response_model=Token, status_code=status.HTTP_200_OK)
def login(db: db_dependency, request: LoginRequest):
    user = authenticate_user(db=db, request=request)
    access_token = create_access_token(user_id=user.id, role=user.global_role.value)
    return {"access_token": access_token, "token_type": "bearer"}

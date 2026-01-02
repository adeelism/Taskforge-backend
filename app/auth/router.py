from fastapi import APIRouter, status, Depends, HTTPException
from app.auth.services import create_user
from typing import Annotated
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.auth.schemas import SignupRequest, Token

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

db_dependency = Annotated[Session, Depends(get_db)]

@router.post('/signup', response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(db: db_dependency, request: SignupRequest):
    user = create_user(db=db, request=request)
    """
    will do this part again later for generating access tokens
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    """

    return {"access_token": 'access_token', "token_type": "bearer"}

from datetime import timedelta, datetime, timezone
from jose import jwt
from app.auth.schemas import SignupRequest, LoginRequest, RefreshTokenRequest, Token
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.core.security import hash_password, verify_password, hash_refresh_token
from app.models.refresh_tokens import RefreshToken
from app.models.users import User
from app.core.config import settings
from uuid import uuid4
from typing import Optional
import secrets


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
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Email")
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return user


def create_refresh_token(*, user_id: int, db: Session) -> str:
    """
    Creates a refresh token
    hashes the token
    saves in db
    returns the token (only once)
    """
    raw_token = secrets.token_urlsafe(
        64)  # This is cryptographically a random string, which is a good secure practice to create random refresh tokens. Url-safe, Industry standard.
    token_hash = hash_refresh_token(raw_token)
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = RefreshToken(token_hash=token_hash, expires_at=expires_at, user_id=user_id)

    try:
        with db.begin:  # start a transaction. This way any exception raised while committing to db, this automatically rolls back your changes made to committing. db.begin context commits
            # automatically, we don't need to explicitly write the commit statement, might cause some problems. and when exiting the begin statement, commit statement is executed
            # and if any exception it rolls back
            db.add(refresh_token)

    except Exception as e:
        # rollback happens automatically, you can log or handle the error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to create refresh token") from e

    return raw_token


def refresh_access_token(*, request: str, db: Session) -> Token:
    token_hash = hash_refresh_token(request)
    db_token = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
    if not db_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    if db_token.revoked_at is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked")

    if db_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

    db_token.revoked_at = datetime.now(timezone.utc)
    db.commit()  # db.add() command can act as update and insert. if no record exists it will insert else update. No need to do it with db.begin() here because the change is
    # already tracked by sqlalchemy, we just need to commit to db.

    user = db.query(User).filter(User.id == db_token.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    new_refresh_token = create_refresh_token(user_id=db_token.user_id, db=db)

    access_token = create_access_token(user_id=db_token.user_id, role=user.global_role.value)

    return Token(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_token=new_refresh_token,
        refresh_expires_in=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        token_type="bearer",
    )


def logout_refresh_token(refresh_token: str, db: Session) -> None:
    token_hash = hash_refresh_token(refresh_token)
    db_token = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
    if not db_token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid refresh token")
    if db_token.revoked_at is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked")

    db_token.revoked_at = datetime.now(timezone.utc)
    try:
        with db.begin:
            db.add(
                db_token)  # update happens here, sqlalchemy already was tracking the record and it knows it exists so rather than inserting it will update.
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to logout user") from e

## will contain all the logic related to hashing, JWT, secrets,
from passlib.context import CryptContext
from app.core.config import settings
from hashlib import sha256

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = settings.ALGORITHM
SECRET_KEY = settings.SECRET_KEY

def hash_password(password):
    return bcrypt_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt_context.verify(plain_password, hashed_password)

def hash_refresh_token(refresh_token: str) -> str:
    return sha256(refresh_token.encode()).hexdigest()

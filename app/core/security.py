## will contain all the logic related to hashing, JWT, secrets,
from passlib.context import CryptContext
from app.core.config import settings

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = settings.ALGORITHM
SECRET_KEY = settings.SECRET_KEY

def hash_password(password):
    return bcrypt_context.hash(password)
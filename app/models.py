from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Enum
from app.database import Base
import enum

class GlobalRoleEnum(str, enum.Enum):
    admin = "admin"
    manager = "manager"
    member = "member"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    global_role = Column(Enum(GlobalRoleEnum), default=GlobalRoleEnum.member)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

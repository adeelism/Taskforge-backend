from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import GlobalRoleEnum, TaskStatusEnum


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    username: str | None = None
    full_name: str | None = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    username: str | None
    full_name: str | None
    is_active: bool
    global_role: GlobalRoleEnum
    created_at: datetime


class TaskCreate(BaseModel):
    title: str = Field(min_length=1)
    description: str | None = None
    owner_id: int


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    description: str | None = None
    status: TaskStatusEnum | None = None


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    status: TaskStatusEnum
    owner_id: int
    created_at: datetime

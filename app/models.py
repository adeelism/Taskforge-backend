import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class GlobalRoleEnum(enum.StrEnum):
    admin = "admin"
    manager = "manager"
    member = "member"


class TaskStatusEnum(enum.StrEnum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    username: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    full_name: Mapped[str | None] = mapped_column(String, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    global_role: Mapped[GlobalRoleEnum] = mapped_column(
        Enum(GlobalRoleEnum), default=GlobalRoleEnum.member
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    tasks: Mapped[list["Task"]] = relationship(back_populates="owner", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[TaskStatusEnum] = mapped_column(
        Enum(TaskStatusEnum), default=TaskStatusEnum.todo
    )
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owner: Mapped["User"] = relationship(back_populates="tasks")

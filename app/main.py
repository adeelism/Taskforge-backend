from fastapi import FastAPI

from app.database import Base, engine
from app.models import Task, User  # noqa: F401  (import so tables are registered)
from app.routers import tasks, users

app = FastAPI(title="Taskforge API", version="1.0.0")

Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(tasks.router)


@app.get("/healthy", tags=["health"])
def healthy() -> dict[str, str]:
    return {"status": "ok"}

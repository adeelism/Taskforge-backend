from fastapi import FastAPI
from app.database import engine
from app.models import Base
from app.auth.router import router as auth_router
app = FastAPI()
Base.metadata.create_all(bind=engine)
@app.get("/healthy")
async def healthy():
    return {"status": "ok"}
app.include_router(auth_router)

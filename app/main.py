from fastapi import FastAPI
from app.database import engine
from app.models import Base
app = FastAPI()
Base.metadata.create_all(bind=engine)

@app.get("/healthy")
async def healthy():
    return {"status": "ok"}
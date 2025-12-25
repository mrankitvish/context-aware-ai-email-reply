from fastapi import FastAPI
from backend.api.v1.endpoints import email, threads
from backend.db.database import engine, Base

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Context Aware AI Email Reply", lifespan=lifespan)

app.include_router(email.router, prefix="/api/v1/email", tags=["email"])
app.include_router(threads.router, prefix="/api/v1/threads", tags=["threads"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Context Aware AI Email Reply API"}

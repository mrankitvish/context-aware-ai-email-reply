from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db.database import get_db
from backend.db.models import Thread, Email
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

router = APIRouter()

class GeneratedReplyResponse(BaseModel):
    id: int
    reply_text: str
    tone: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class EmailResponse(BaseModel):
    id: str
    sender: str
    subject: str
    body: str
    received_at: datetime
    reply: Optional[GeneratedReplyResponse] = None
    
    model_config = ConfigDict(from_attributes=True)

class ThreadResponse(BaseModel):
    id: str
    created_at: datetime
    emails: List[EmailResponse]
    
    model_config = ConfigDict(from_attributes=True)

@router.get("/", response_model=List[ThreadResponse])
def list_threads(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    threads = db.query(Thread).offset(skip).limit(limit).all()
    return threads

@router.get("/{thread_id}", response_model=ThreadResponse)
def get_thread(thread_id: str, db: Session = Depends(get_db)):
    thread = db.query(Thread).filter(Thread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    return thread

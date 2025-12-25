from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db.database import get_db
from backend.db.models import EmailSummary, GeneratedReply
from backend.ai.email_processor import EmailProcessor
from backend.ai.reply_generator import ReplyGenerator
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class EmailSubmitRequest(BaseModel):
    subject: str
    body: str
    sender: str
    thread_id: Optional[str] = None

class GenerateReplyRequest(BaseModel):
    tone: str = "professional"
    auto_send: bool = False

from backend.core.security import validate_content

@router.post("/submit")
def submit_email(email_request: EmailSubmitRequest, db: Session = Depends(get_db)):
    # Basic Guardrail
    validate_content(email_request.subject, email_request.body)
    
    processor = EmailProcessor(db)
    summary = processor.process_email(email_request.model_dump())
    return {"status": "success", "email_id": summary.email_id, "summary": summary.summary_json}

@router.get("/{email_id}/summary")
def get_email_summary(email_id: str, db: Session = Depends(get_db)):
    summary = db.query(EmailSummary).filter(EmailSummary.email_id == email_id).first()
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return {"summary": summary.summary_json}

@router.post("/{email_id}/generate-reply")
def generate_reply(email_id: str, request: GenerateReplyRequest, db: Session = Depends(get_db)):
    summary = db.query(EmailSummary).filter(EmailSummary.email_id == email_id).first()
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    
    generator = ReplyGenerator()
    result = generator.generate(summary.summary_json, tone=request.tone)
    
    if result["status"] == "error":
        # Do not save to DB
        raise HTTPException(status_code=400, detail=f"Reply generation failed: {result['error']}")
    
    reply_text = result["reply"]
    
    # Store reply
    existing_reply = db.query(GeneratedReply).filter(GeneratedReply.email_id == email_id).first()
    if existing_reply:
        existing_reply.reply_text = reply_text
        existing_reply.tone = request.tone
    else:
        reply = GeneratedReply(
            email_id=email_id,
            reply_text=reply_text,
            tone=request.tone
        )
        db.add(reply)
    
    db.commit()
    
    # Return thread_id, email_id along with reply
    thread_id = summary.summary_json.get("thread_info", {}).get("thread_id")
    
    return {
        "email_id": email_id,
        "thread_id": thread_id,
        "reply": reply_text
    }

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
    instructions: Optional[str] = None

class RawEmailRequest(BaseModel):
    raw_content: str
    thread_id: Optional[str] = None

from backend.core.security import validate_content

@router.post("/webhook")
def process_raw_email(request: RawEmailRequest, db: Session = Depends(get_db)):
    """
    Webhook endpoint to process raw email content pasted by users.
    Uses LLM to intelligently parse the raw text to extract sender, subject, and body.
    """
    raw_text = request.raw_content.strip()
    
    if not raw_text:
        raise HTTPException(status_code=400, detail="Raw content cannot be empty")
    
    # Use LLM to parse the raw email content
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import JsonOutputParser
    from pydantic import BaseModel as PydanticBaseModel, Field
    from backend.core.config import settings
    
    class ParsedEmail(PydanticBaseModel):
        sender: str = Field(description="Email address of the sender")
        subject: str = Field(description="Subject line of the email")
        body: str = Field(description="Main body content of the email")
    
    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL
    )
    
    parser = JsonOutputParser(pydantic_object=ParsedEmail)
    
    # Get guardrail rules from security module
    from backend.core.security import UNSAFE_KEYWORDS
    guardrail_rules = ", ".join(UNSAFE_KEYWORDS)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert email parser with built-in safety filters. Extract the sender email address, subject, and body from raw email content.

SAFETY GUARDRAILS:
Before parsing, check if the content contains any of these unsafe patterns: {guardrail_rules}

If the content contains ANY of these patterns, you MUST:
1. Set subject to "UNSAFE_CONTENT_DETECTED"
2. Set body to "This email was blocked due to safety concerns"
3. Set sender to "blocked@security.system"

Rules for safe content:
- If you find "From:" or similar headers, extract the email address
- If you find "Subject:" extract the subject line
- The body is the main message content
- If no clear sender is found, use "unknown@example.com"
- If no clear subject is found, use the first line or "No Subject"
- Always extract the complete body content
- Handle various email formats (Gmail, Outlook, plain text, etc.)"""),
        ("user", "Parse this raw email content:\n\n{raw_content}\n\n{format_instructions}")
    ])
    
    chain = prompt | llm | parser
    
    try:
        parsed = chain.invoke({
            "raw_content": raw_text,
            "format_instructions": parser.get_format_instructions(),
            "guardrail_rules": guardrail_rules
        })
        
        sender = parsed.get('sender', 'unknown@example.com')
        subject = parsed.get('subject', 'No Subject')
        body = parsed.get('body', raw_text)
        
        # Check if LLM detected unsafe content
        if subject == "UNSAFE_CONTENT_DETECTED":
            raise HTTPException(status_code=400, detail="Content blocked by AI safety filters")
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        # Fallback to simple extraction if LLM fails
        lines = raw_text.split('\n')
        sender = "unknown@example.com"
        subject = lines[0][:100] if lines else "No Subject"
        body = raw_text
    
    # Validate extracted content
    if not body:
        raise HTTPException(status_code=400, detail="Could not extract email body from raw content")
    
    # Apply guardrails to parsed subject and body (double-check)
    validate_content(subject, body)
    
    email_data = {
        "sender": sender,
        "subject": subject,
        "body": body,
        "thread_id": request.thread_id
    }
    
    processor = EmailProcessor(db)
    summary = processor.process_email(email_data)
    
    return {
        "status": "success",
        "email_id": summary.email_id,
        "summary": summary.summary_json,
        "parsed_data": {
            "sender": sender,
            "subject": subject,
            "body_preview": body[:200] + "..." if len(body) > 200 else body
        }
    }

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
    result = generator.generate(
        summary.summary_json, 
        tone=request.tone, 
        instructions=request.instructions
    )
    
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

from sqlalchemy.orm import Session
from backend.db.models import Email, Thread, EmailSummary
from backend.core.config import settings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional
import json
import uuid

# Define Pydantic models for the structured summary output
class SenderInfo(BaseModel):
    email: str
    name: Optional[str] = None
    previous_interactions: int = 0

class ThreadInfo(BaseModel):
    is_thread: bool
    thread_id: Optional[str] = None
    email_count: int = 1
    thread_summary: Optional[str] = None

class ContentAnalysis(BaseModel):
    main_topic: str
    questions: List[str] = []
    action_items: List[str] = []
    mentioned_entities: List[str] = []
    dates_deadlines: List[str] = []

class Classification(BaseModel):
    intent: str
    sub_intent: Optional[str] = None
    confidence: float

class Sentiment(BaseModel):
    score: float
    label: str
    tone: str

class Urgency(BaseModel):
    level: str
    reason: str
    suggested_response_time: str

class EmailSummaryModel(BaseModel):
    email_id: str
    timestamp: str
    sender: SenderInfo
    thread_info: ThreadInfo
    content_analysis: ContentAnalysis
    classification: Classification
    sentiment: Sentiment
    urgency: Urgency
    context_summary: str
    recommended_tone: str

class EmailProcessor:
    def __init__(self, db: Session):
        self.db = db
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )

    def process_email(self, email_data: dict) -> EmailSummary:
        # 1. Store Email
        email_id = str(uuid.uuid4())
        thread_id = email_data.get("thread_id")
        
        if not thread_id:
            # Simple logic: create new thread if none provided
            thread_id = str(uuid.uuid4())
            thread = Thread(id=thread_id)
            self.db.add(thread)
        else:
            thread = self.db.query(Thread).filter(Thread.id == thread_id).first()
            if not thread:
                thread = Thread(id=thread_id)
                self.db.add(thread)
        
        new_email = Email(
            id=email_id,
            thread_id=thread_id,
            sender=email_data["sender"],
            subject=email_data["subject"],
            body=email_data["body"]
        )
        self.db.add(new_email)
        self.db.commit()
        self.db.refresh(new_email)

        # 2. Build Context (Fetch Thread)
        thread_emails = self.db.query(Email).filter(Email.thread_id == thread_id).order_by(Email.received_at).all()
        thread_context = "\n\n".join([f"From: {e.sender}\nSubject: {e.subject}\nBody: {e.body}" for e in thread_emails])

        # 3. Summarize using LLM
        summary_data = self._generate_summary(new_email, thread_context, len(thread_emails))
        
        # 4. Store Summary
        email_summary = EmailSummary(
            email_id=email_id,
            summary_json=summary_data.dict()
        )
        self.db.add(email_summary)
        self.db.commit()
        
        return email_summary

    def _generate_summary(self, email: Email, thread_context: str, email_count: int) -> EmailSummaryModel:
        parser = JsonOutputParser(pydantic_object=EmailSummaryModel)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert email analyst. Analyze the following email and its thread context to produce a structured summary."),
            ("user", "Email ID: {email_id}\nTimestamp: {timestamp}\nSender: {sender}\n\nThread Context:\n{thread_context}\n\nAnalyze this email and return the result in JSON format.\n{format_instructions}")
        ])

        chain = prompt | self.llm | parser

        result = chain.invoke({
            "email_id": email.id,
            "timestamp": str(email.received_at),
            "sender": email.sender,
            "thread_context": thread_context,
            "format_instructions": parser.get_format_instructions()
        })
        
        # Ensure thread info is accurate based on DB
        result['thread_info']['is_thread'] = email_count > 1
        result['thread_info']['email_count'] = email_count
        result['thread_info']['thread_id'] = email.thread_id
        
        return EmailSummaryModel(**result)

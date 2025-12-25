from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db.database import Base

class Thread(Base):
    __tablename__ = "threads"

    id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    emails = relationship("Email", back_populates="thread")

class Email(Base):
    __tablename__ = "emails"

    id = Column(String, primary_key=True, index=True)
    thread_id = Column(String, ForeignKey("threads.id"), nullable=True)
    sender = Column(String, index=True)
    subject = Column(String)
    body = Column(Text)
    received_at = Column(DateTime(timezone=True), server_default=func.now())
    
    thread = relationship("Thread", back_populates="emails")
    summary = relationship("EmailSummary", back_populates="email", uselist=False)
    reply = relationship("GeneratedReply", back_populates="email", uselist=False)

class EmailSummary(Base):
    __tablename__ = "email_summaries"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(String, ForeignKey("emails.id"), unique=True)
    summary_json = Column(JSON) # Stores the full structured summary
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    email = relationship("Email", back_populates="summary")

class GeneratedReply(Base):
    __tablename__ = "generated_replies"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(String, ForeignKey("emails.id"), unique=True)
    reply_text = Column(Text)
    tone = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    email = relationship("Email", back_populates="reply")

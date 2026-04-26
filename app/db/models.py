from sqlalchemy import Column, String, Text, Integer, DateTime
from sqlalchemy.orm import declarative_base
import uuid, datetime

Base = declarative_base()

class Message(Base):
    __tablename__ = "messages"

    id       = Column(String,  primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, index=True)
    role     = Column(String)          # "user" | "assistant" | "system"
    content  = Column(Text)
    turn     = Column(Integer, default=0)   # sequential turn index
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class SessionSummary(Base):
    """Stores compressed long-term memory for a session."""
    __tablename__ = "session_summaries"

    id         = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, index=True, unique=True)
    summary    = Column(Text)
    turn_upto  = Column(Integer, default=0)   # messages up to which turn are summarised
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

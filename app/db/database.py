import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import Base

default_sqlite_url = "sqlite:////tmp/chat.db" if os.getenv("VERCEL") else "sqlite:///./chat.db"
DATABASE_URL = os.getenv("DATABASE_URL", default_sqlite_url)

engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

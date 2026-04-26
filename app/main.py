from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.db.database import init_db

app = FastAPI(title="Stateful AI Chatbot — Intelligent Memory")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

app.include_router(chat_router, prefix="/api")

@app.get("/")
def health_check():
    return {"status": "running", "version": "2.0"}

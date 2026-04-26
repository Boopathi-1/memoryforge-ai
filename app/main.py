from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.chat import router as chat_router
from app.db.database import init_db

app = FastAPI(title="Stateful AI Chatbot - Intelligent Memory")

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
def home():
    return RedirectResponse(url="/index.html", status_code=307)


@app.get("/api/health")
def health_check():
    return {"status": "running", "version": "2.0"}

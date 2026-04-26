# Stateful AI Chatbot — Intelligent Memory Architecture

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env        # add your GROQ_API_KEY
uvicorn app.main:app --reload
# open chat_ui.html in your browser
```

## Architecture

```
User Message
     │
     ▼
┌──────────────────────────────────────────────┐
│             FastAPI  /api/chat               │
│                                              │
│  1. Store user message (DB)                  │
│  2. Build context ──────────────────────┐   │
│       ├─ Long-term summary (DB)         │   │
│       └─ Short-term window (last 10)    │   │
│  3. Auto-summarise if > 20 msgs  ◄──────┘   │
│  4. Call Groq LLM                            │
│  5. Store assistant reply (DB)               │
└──────────────────────────────────────────────┘
     │
     ▼
ChatResponse { reply, session_id, memory_stats }
```

## Memory Layers

| Layer       | Storage    | Content                          | Tokens  |
|-------------|------------|----------------------------------|---------|
| Short-term  | DB (live)  | Last 10 messages verbatim        | ~1-2k   |
| Long-term   | DB summary | Bullet-point summary of older msgs | ~400  |
| Context     | In-memory  | Summary + recent merged for LLM  | <4k     |

## API Endpoints

| Method | Path                   | Description                     |
|--------|------------------------|---------------------------------|
| POST   | /api/chat              | Send a message                  |
| GET    | /api/memory/{sid}      | Inspect full memory state       |
| POST   | /api/clear             | Clear session memory            |
| GET    | /                      | Health check                    |

## Debug UI

Open `chat_ui.html` in your browser. Toggle **DEBUG** in the header to reveal:

- **MEMORY tab** — live stats: total messages, short-term window, archived count, estimated tokens, long-term summary status
- **MSG LOG tab** — full conversation history with turn numbers
- **JSON tab** — raw API state for inspection

# MemoryForge AI

MemoryForge AI is a stateful chatbot built with FastAPI, Groq, SQLite, and a custom memory pipeline that helps the assistant stay coherent across longer conversations.

Instead of sending the entire chat history on every request, the app keeps a short-term working window of recent messages and compresses older context into a long-term summary. That gives you lower prompt size, better continuity, and a clearer view into how conversational memory works.

## Highlights

- Persistent session-based chat memory
- Short-term memory window for recent turns
- Long-term memory summaries for older context
- Automatic summarization after the conversation grows
- SQLite-backed message and summary storage
- FastAPI backend with simple REST endpoints
- Debug UI for inspecting memory state, token estimates, and message logs

## How It Works

1. A user message is sent to `/api/chat`.
2. The message is stored in SQLite with a session id and turn number.
3. The app builds context using:
   recent messages for short-term memory
   stored summary for long-term memory
4. If the conversation is large enough, older messages are summarized and saved.
5. The merged context is sent to the Groq model.
6. The assistant reply is stored and returned with memory statistics.

## Memory Architecture

| Layer | Purpose | Stored As |
|---|---|---|
| Short-term memory | Keeps the latest conversation turns verbatim | Recent messages in DB |
| Long-term memory | Compresses older chat history | Session summary in DB |
| Context builder | Prepares the final prompt for the model | In memory at request time |

Default behavior in the current project:

- `SHORT_TERM_LIMIT = 10`
- `SUMMARY_TRIGGER = 20`
- `MAX_TOKENS = 1024`

## Tech Stack

- FastAPI
- Groq API
- SQLAlchemy
- SQLite
- Pydantic
- Static HTML/CSS/JS frontend

## Project Structure

```text
app/
  api/         # FastAPI routes
  core/        # settings and config
  db/          # database setup and models
  schemas/     # request/response models
  services/    # LLM and memory logic
  utils/       # helpers such as session id generation
chat_ui.html   # browser UI with debug panel
```

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/chat` | Send a message and get the assistant reply |
| `GET` | `/api/memory/{session_id}` | Inspect stored messages, summary, and memory stats |
| `POST` | `/api/clear` | Clear a session's memory |
| `GET` | `/` | Health check |

## Local Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Add environment variables

Create a `.env` file from `.env.example` and add your Groq key:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Run the backend

```bash
uvicorn app.main:app --reload
```

### 4. Open the UI

Open `chat_ui.html` in your browser.

## Debug Features

The frontend includes a debug panel to help inspect how memory evolves during a conversation.

- `MEMORY` tab shows total messages, short-term count, archived count, summary coverage, and estimated tokens
- `MSG LOG` tab shows the stored message history with turn numbers
- `JSON` tab shows the raw memory state returned by the backend

## Why This Project Stands Out

This project is more than a basic chatbot demo. It shows how to build:

- context-aware conversational systems
- practical long-session memory management
- cost-conscious prompt construction
- observable AI applications with inspectable internal state

It is a strong foundation for assistants, support bots, AI companions, learning tools, and portfolio demos focused on applied LLM engineering.

## Future Improvements

- streaming responses
- authentication and multi-user support
- vector memory or retrieval augmentation
- richer summarization strategies
- deployment setup for cloud hosting
- improved frontend session management

## License

This project currently has no license file. Add one before distributing it broadly if needed.

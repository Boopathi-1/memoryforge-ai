from fastapi import APIRouter
from app.schemas.chat_schema import ChatRequest, ChatResponse, ClearRequest, MemoryStateResponse
from app.utils.session import create_session_id
from app.services.llm import get_ai_response, summarise_messages
from app.services.memory import (
    add_message, build_context, get_all_messages,
    get_summary, save_summary, clear_session
)
from app.core.config import settings

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    session_id = request.session_id or create_session_id()

    # Store incoming user message
    add_message(session_id, "user", request.message)

    # Build context (short-term + long-term summary)
    ctx = build_context(session_id)

    # Auto-summarise if history is long
    all_msgs = get_all_messages(session_id)
    if len(all_msgs) > settings.SUMMARY_TRIGGER:
        existing_summary = get_summary(session_id)
        covered_up_to = existing_summary["turn_upto"] if existing_summary else -1
        to_summarise = [m for m in all_msgs if m["turn"] > covered_up_to]
        # Only re-summarise if there are enough new messages
        if len(to_summarise) >= settings.SHORT_TERM_LIMIT:
            archive = all_msgs[:-settings.SHORT_TERM_LIMIT]
            summary_text = summarise_messages(archive)
            save_summary(session_id, summary_text, archive[-1]["turn"])
            # Rebuild context with fresh summary
            ctx = build_context(session_id)

    # Generate reply
    reply = get_ai_response(ctx["messages"])

    # Persist assistant reply
    add_message(session_id, "assistant", reply)

    return ChatResponse(
        session_id=session_id,
        reply=reply,
        memory_stats=ctx["memory_stats"],
    )


@router.get("/memory/{session_id}", response_model=MemoryStateResponse)
def get_memory_state(session_id: str):
    ctx = build_context(session_id)
    all_msgs = get_all_messages(session_id)
    summary_row = get_summary(session_id)
    return MemoryStateResponse(
        session_id=session_id,
        messages=all_msgs,
        summary=summary_row["summary"] if summary_row else None,
        memory_stats=ctx["memory_stats"],
    )


@router.post("/clear")
def clear_memory(request: ClearRequest):
    clear_session(request.session_id)
    return {"status": "cleared", "session_id": request.session_id}

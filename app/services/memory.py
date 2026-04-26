"""
Memory service — three-layer architecture:
  1. Short-term  : last SHORT_TERM_LIMIT messages (verbatim, for coherence)
  2. Long-term   : LLM-generated summary of older messages (stored in DB)
  3. Context builder : merges summary + recent messages into LLM prompt
"""

import datetime
from typing import List

from app.db.database import SessionLocal
from app.db.models import Message, SessionSummary
from app.core.config import settings


# ── helpers ──────────────────────────────────────────────────────────────────

def _next_turn(session_id: str, db) -> int:
    last = (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.turn.desc())
        .first()
    )
    return (last.turn + 1) if last else 0


# ── public API ────────────────────────────────────────────────────────────────

def add_message(session_id: str, role: str, content: str):
    db = SessionLocal()
    try:
        turn = _next_turn(session_id, db)
        msg = Message(session_id=session_id, role=role, content=content, turn=turn)
        db.add(msg)
        db.commit()
    finally:
        db.close()


def get_all_messages(session_id: str) -> List[dict]:
    db = SessionLocal()
    try:
        rows = (
            db.query(Message)
            .filter(Message.session_id == session_id)
            .order_by(Message.turn)
            .all()
        )
        return [{"role": m.role, "content": m.content, "turn": m.turn} for m in rows]
    finally:
        db.close()


def get_summary(session_id: str):
    db = SessionLocal()
    try:
        row = db.query(SessionSummary).filter(SessionSummary.session_id == session_id).first()
        return {"summary": row.summary, "turn_upto": row.turn_upto} if row else None
    finally:
        db.close()


def save_summary(session_id: str, summary_text: str, turn_upto: int):
    db = SessionLocal()
    try:
        row = db.query(SessionSummary).filter(SessionSummary.session_id == session_id).first()
        if row:
            row.summary    = summary_text
            row.turn_upto  = turn_upto
            row.updated_at = datetime.datetime.utcnow()
        else:
            db.add(SessionSummary(session_id=session_id, summary=summary_text, turn_upto=turn_upto))
        db.commit()
    finally:
        db.close()


def build_context(session_id: str) -> dict:
    """
    Returns:
      {
        "messages"        : [...],   # ready-to-send message list for LLM
        "memory_stats"    : {...},   # for debug panel
      }
    """
    all_msgs = get_all_messages(session_id)
    summary_row = get_summary(session_id)

    short_term_limit = settings.SHORT_TERM_LIMIT
    recent = all_msgs[-short_term_limit:]           # short-term window
    archived = all_msgs[:-short_term_limit] if len(all_msgs) > short_term_limit else []

    messages_for_llm = []

    # Inject long-term summary if available
    if summary_row:
        messages_for_llm.append({
            "role": "system",
            "content": f"[Long-term memory summary of earlier conversation]\n{summary_row['summary']}"
        })

    # Add recent short-term messages
    messages_for_llm += [{"role": m["role"], "content": m["content"]} for m in recent]

    memory_stats = {
        "total_messages"   : len(all_msgs),
        "short_term_count" : len(recent),
        "archived_count"   : len(archived),
        "has_summary"      : summary_row is not None,
        "summary_covers_turns": summary_row["turn_upto"] if summary_row else 0,
        "estimated_tokens" : sum(len(m["content"].split()) * 1.3 for m in messages_for_llm),
    }

    return {"messages": messages_for_llm, "memory_stats": memory_stats}


def clear_session(session_id: str):
    db = SessionLocal()
    try:
        db.query(Message).filter(Message.session_id == session_id).delete()
        db.query(SessionSummary).filter(SessionSummary.session_id == session_id).delete()
        db.commit()
    finally:
        db.close()

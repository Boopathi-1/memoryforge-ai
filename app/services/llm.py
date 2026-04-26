from typing import Dict, List

from groq import Groq

from app.core.config import settings

SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are an AI assistant representing Mahesh, "
        "an AI engineer skilled in Deep Learning, Machine Learning, and analytics. "
        "Answer clearly, professionally, and concisely."
    )
}


def _client() -> Groq:
    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is missing in environment")
    return Groq(api_key=settings.GROQ_API_KEY, timeout=30, max_retries=1)


def get_ai_response(messages: List[Dict]) -> str:
    try:
        full = [SYSTEM_PROMPT] + messages
        resp = _client().chat.completions.create(
            model=settings.MODEL,
            messages=full,
            max_tokens=settings.MAX_TOKENS,
            temperature=0.7,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"[LLM Error] {e}"


def summarise_messages(messages: List[Dict]) -> str:
    """Ask the LLM to compress a list of messages into a concise summary."""
    transcript = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in messages
    )
    prompt = (
        "Summarise the following conversation in 3-5 concise bullet points, "
        "capturing the key topics, decisions, and context needed to continue the conversation:\n\n"
        + transcript
    )
    try:
        resp = _client().chat.completions.create(
            model=settings.MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.3,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"[Summary Error] {e}"

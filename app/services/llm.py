import json
from typing import Dict, List
from urllib import error, request

from app.core.config import settings

SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are an AI assistant representing Mahesh, "
        "an AI engineer skilled in Deep Learning, Machine Learning, and analytics. "
        "Answer clearly, professionally, and concisely."
    )
}

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"


def _chat_completion(messages: List[Dict], max_tokens: int, temperature: float) -> str:
    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is missing in environment")

    payload = json.dumps(
        {
            "model": settings.MODEL,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
    ).encode("utf-8")

    req = request.Request(
        GROQ_CHAT_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {body}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"Connection error: {exc.reason}") from exc


def get_ai_response(messages: List[Dict]) -> str:
    try:
        full = [SYSTEM_PROMPT] + messages
        return _chat_completion(
            messages=full,
            max_tokens=settings.MAX_TOKENS,
            temperature=0.7,
        )
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
        return _chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.3,
        )
    except Exception as e:
        return f"[Summary Error] {e}"

from pydantic import BaseModel
from typing import Optional, Any, Dict, List

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    session_id : str
    reply      : str
    memory_stats: Dict[str, Any]

class ClearRequest(BaseModel):
    session_id: str

class MemoryStateResponse(BaseModel):
    session_id   : str
    messages     : List[dict]
    summary      : Optional[str] = None
    memory_stats : Dict[str, Any]

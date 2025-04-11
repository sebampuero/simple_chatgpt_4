from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import datetime
from uuid import uuid4

class ChatStateModel(BaseModel):
    email: str = Field(default="")
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    timestamp: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    current_chat_id: str = Field(default_factory=lambda: uuid4().hex)
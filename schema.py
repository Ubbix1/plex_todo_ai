from pydantic import BaseModel
from typing import Optional

class TodoTask(BaseModel):
    title: str
    time: Optional[str] = None
    date: Optional[str] = None
    repeat: Optional[str] = None
    priority: Optional[str] = "medium"
    advice: Optional[str] = None
    emotional_support: Optional[str] = None
    thought_process: Optional[str] = None

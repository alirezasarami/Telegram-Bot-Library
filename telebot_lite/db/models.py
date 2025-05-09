# models.py
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

class User(BaseModel):
    id: int
    is_bot: bool
    first_name: str
    username: Optional[str]


class Chat(BaseModel):
    id: int
    type: str
    title: Optional[str]


class Message(BaseModel):
    message_id: int
    from_: User = Field(..., alias="from")
    date: int
    chat: "Chat"
    text: Optional[str]
    @field_validator("date", mode="before")
    def ts_to_datetime(cls, v):
        return datetime.fromtimestamp(v, tz=timezone.utc)
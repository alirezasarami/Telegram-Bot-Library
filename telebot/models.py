from __future__ import annotations
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from typing import List, Optional

class User:
    id: int
    is_bot: bool
    first_name: str
    username: Optional[str]


class Message:
    message_id: int
    from_: User = Field(..., alias="from")
    date: datetime
    chat: "chat"
    text: Optional[str]

    @field_validator("date", mode="before")
    def ts_to_datetime(cls, v):
        return datetime.fromtimestamp(v, timezone.utc)


class Chat:
    id: int
    type: str
    title: Optional[str]

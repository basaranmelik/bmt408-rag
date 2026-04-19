from pydantic import BaseModel
from datetime import datetime
from typing import List


class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatSessionCreate(BaseModel):
    historical_figure_id: int


class ChatSessionResponse(BaseModel):
    id: int
    historical_figure_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatSessionWithMessages(BaseModel):
    id: int
    historical_figure_id: int
    created_at: datetime
    messages: List[ChatMessageResponse] = []

    model_config = {"from_attributes": True}


class ChatMessageCreate(BaseModel):
    session_id: int
    role: str
    content: str

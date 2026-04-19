from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class HistoricalFigureCreate(BaseModel):
    name: str
    birth_date: Optional[str] = None
    death_date: Optional[str] = None
    region: Optional[str] = None
    bio: Optional[str] = None
    collection_name: Optional[str] = None


class HistoricalFigureUpdate(BaseModel):
    name: Optional[str] = None
    birth_date: Optional[str] = None
    death_date: Optional[str] = None
    region: Optional[str] = None
    bio: Optional[str] = None


class HistoricalFigureResponse(BaseModel):
    id: int
    name: str
    birth_date: Optional[str]
    death_date: Optional[str]
    region: Optional[str]
    bio: Optional[str]
    collection_name: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}

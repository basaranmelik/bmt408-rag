from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db
from database.schemas.chat_session import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatSessionWithMessages,
)

from database.crud import chat_session as session_crud

router = APIRouter(prefix="/sessions")


@router.post("", response_model=ChatSessionResponse, status_code=201)
async def create_session(data: ChatSessionCreate, db: AsyncSession = Depends(get_db)):
    return await session_crud.create_session(db, data)


@router.get("/{session_id}", response_model=ChatSessionWithMessages)
async def get_session(session_id: int, db: AsyncSession = Depends(get_db)):
    session = await session_crud.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Oturum bulunamadı.")
    return session


@router.delete("/{session_id}", status_code=204)
async def delete_session(session_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await session_crud.delete_session(db, session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Oturum bulunamadı.")

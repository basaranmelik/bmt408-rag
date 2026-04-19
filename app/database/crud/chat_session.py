from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional
from database.models.chat_session import ChatSession
from database.models.chat_message import ChatMessage
from database.schemas.chat_session import ChatSessionCreate, ChatMessageCreate


async def create_session(db: AsyncSession, data: ChatSessionCreate) -> ChatSession:
    session = ChatSession(historical_figure_id=data.historical_figure_id)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def get_session(db: AsyncSession, session_id: int) -> Optional[ChatSession]:
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.id == session_id)
        .options(
            selectinload(ChatSession.messages),
            selectinload(ChatSession.historical_figure),
        )
    )
    return result.scalar_one_or_none()


async def delete_session(db: AsyncSession, session_id: int) -> bool:
    result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        return False
    await db.delete(session)
    await db.commit()
    return True


async def add_message(db: AsyncSession, data: ChatMessageCreate) -> ChatMessage:
    message = ChatMessage(session_id=data.session_id, role=data.role, content=data.content)
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message

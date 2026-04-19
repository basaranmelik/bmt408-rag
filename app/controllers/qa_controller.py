from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage
from database.connection import get_db
from database.crud.chat_session import get_session, add_message
from database.schemas.chat_session import ChatMessageCreate
from services.qa_service import answer_question

router = APIRouter()


class AskRequest(BaseModel):
    session_id: int
    question: str


@router.post("/ask")
async def ask_question_endpoint(request: AskRequest, db: AsyncSession = Depends(get_db)):
    session = await get_session(db, request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Oturum bulunamadı.")

    figure = session.historical_figure
    if not figure:
        raise HTTPException(status_code=404, detail="Tarihi figür bulunamadı.")

    # DB'deki mesaj geçmişini LangChain formatına çevir
    chat_history = []
    for msg in session.messages:
        if msg.role == "user":
            chat_history.append(HumanMessage(content=msg.content))
        else:
            chat_history.append(AIMessage(content=msg.content))

    answer = answer_question(
        figure_id=figure.id,
        figure_name=figure.name,
        collection_name=figure.collection_name,
        question=request.question,
        chat_history=chat_history
    )

    # Mesajları DB'ye kaydet
    await add_message(db, ChatMessageCreate(session_id=request.session_id, role="user", content=request.question))
    await add_message(db, ChatMessageCreate(session_id=request.session_id, role="ai", content=answer))

    return {"answer": answer}

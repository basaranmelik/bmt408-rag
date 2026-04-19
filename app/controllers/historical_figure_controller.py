from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from database.connection import get_db
from database.schemas.historical_figure import HistoricalFigureUpdate, HistoricalFigureResponse
from database.crud import historical_figure as figure_crud
from config.qdrant_client import client as qdrant_client

router = APIRouter(prefix="/figures")


@router.get("", response_model=List[HistoricalFigureResponse])
async def list_figures(db: AsyncSession = Depends(get_db)):
    return await figure_crud.get_all_figures(db)


@router.get("/{figure_id}", response_model=HistoricalFigureResponse)
async def get_figure(figure_id: int, db: AsyncSession = Depends(get_db)):
    figure = await figure_crud.get_figure(db, figure_id)
    if not figure:
        raise HTTPException(status_code=404, detail="Tarihi figür bulunamadı.")
    return figure


@router.put("/{figure_id}", response_model=HistoricalFigureResponse)
async def update_figure(figure_id: int, data: HistoricalFigureUpdate, db: AsyncSession = Depends(get_db)):
    figure = await figure_crud.update_figure(db, figure_id, data)
    if not figure:
        raise HTTPException(status_code=404, detail="Tarihi figür bulunamadı.")
    return figure


@router.delete("/{figure_id}", status_code=204)
async def delete_figure(figure_id: int, db: AsyncSession = Depends(get_db)):
    collection_name = await figure_crud.delete_figure(db, figure_id)
    if collection_name is None:
        raise HTTPException(status_code=404, detail="Tarihi figür bulunamadı.")
    # Qdrant koleksiyonunu da sil
    try:
        qdrant_client.delete_collection(collection_name)
    except Exception:
        pass

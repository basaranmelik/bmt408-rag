from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from database.models.historical_figure import HistoricalFigure
from database.schemas.historical_figure import HistoricalFigureCreate, HistoricalFigureUpdate


async def create_figure(db: AsyncSession, data: HistoricalFigureCreate) -> HistoricalFigure:
    figure = HistoricalFigure(**data.model_dump())
    db.add(figure)
    await db.commit()
    await db.refresh(figure)
    return figure


async def get_figure(db: AsyncSession, figure_id: int) -> Optional[HistoricalFigure]:
    result = await db.execute(select(HistoricalFigure).where(HistoricalFigure.id == figure_id))
    return result.scalar_one_or_none()


async def get_all_figures(db: AsyncSession) -> List[HistoricalFigure]:
    result = await db.execute(select(HistoricalFigure).order_by(HistoricalFigure.created_at.desc()))
    return list(result.scalars().all())


async def update_figure(db: AsyncSession, figure_id: int, data: HistoricalFigureUpdate) -> Optional[HistoricalFigure]:
    figure = await get_figure(db, figure_id)
    if not figure:
        return None
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(figure, field, value)
    await db.commit()
    await db.refresh(figure)
    return figure


async def set_collection_name(db: AsyncSession, figure_id: int, collection_name: str) -> None:
    figure = await get_figure(db, figure_id)
    if figure:
        figure.collection_name = collection_name
        await db.commit()


async def delete_figure(db: AsyncSession, figure_id: int) -> Optional[str]:
    figure = await get_figure(db, figure_id)
    if not figure:
        return None
    collection_name = figure.collection_name
    await db.delete(figure)
    await db.commit()
    return collection_name

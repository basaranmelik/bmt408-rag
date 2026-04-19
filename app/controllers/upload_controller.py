from fastapi import APIRouter, UploadFile, Form, File, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db
from services.upload_service import handle_upload

router = APIRouter()


@router.post("/upload")
async def upload_pdf(
    historical_figure_name: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    return await handle_upload(historical_figure_name, file, db)

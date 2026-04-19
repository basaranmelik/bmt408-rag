import shutil
import json
import re
import tempfile
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from utils.ingestion_loader import load_and_ingest_pdf
from langchain_community.document_loaders import PyPDFLoader
from agents.character_info_extractor import character_info_extraction_chain
from agents.character_validation_agent import character_validation_chain
from database.crud.historical_figure import create_figure, set_collection_name
from database.schemas.historical_figure import HistoricalFigureCreate


async def handle_upload(historical_figure_name: str, file, db: AsyncSession):
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            temp_file_path = Path(temp_dir) / file.filename

            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            loader = PyPDFLoader(str(temp_file_path))
            pages = loader.load()
            full_text = "\n".join([page.page_content for page in pages])

            validation_result = character_validation_chain.invoke({
                "historical_figure_name": historical_figure_name,
                "context": full_text
            })

            raw_output = validation_result.get("text") or validation_result.get("output") if isinstance(validation_result, dict) else validation_result
            if "no" in raw_output.lower():
                return {
                    "status": "error",
                    "message": f"Yüklenen PDF '{historical_figure_name}' ile ilgili görünmüyor."
                }

            # Karakter bilgilerini çıkar
            raw_info = character_info_extraction_chain.invoke({"context": full_text})
            if isinstance(raw_info, dict) and "text" in raw_info:
                match = re.search(r"\{.*?\}", raw_info["text"], re.DOTALL)
                info = json.loads(match.group(0)) if match else {}
            else:
                info = {}

            figure = await create_figure(db, HistoricalFigureCreate(
                name=historical_figure_name,
                birth_date=info.get("birth_date"),
                death_date=info.get("death_date"),
                region=info.get("region"),
                bio=info.get("bio"),
            ))

            # Qdrant collection adını belirle ve ingestion yap
            collection_name = f"figure_{figure.id}"
            load_and_ingest_pdf(
                pdf_path=temp_file_path,
                collection_name=collection_name,
                metadata={
                    "figure_id": figure.id,
                    "figure_name": historical_figure_name,
                    "source": "user_upload"
                }
            )

            # Collection adını DB'ye yaz
            await set_collection_name(db, figure.id, collection_name)
            figure.collection_name = collection_name

            return {
                "status": "ok",
                "message": "PDF başarıyla yüklendi.",
                "figure": {
                    "id": figure.id,
                    "name": figure.name,
                    "birth_date": figure.birth_date,
                    "death_date": figure.death_date,
                    "region": figure.region,
                    "bio": figure.bio,
                    "collection_name": figure.collection_name,
                }
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

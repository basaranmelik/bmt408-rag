from contextlib import asynccontextmanager
from fastapi import FastAPI
from controllers.upload_controller import router as upload_router
from controllers.qa_controller import router as qa_router
from controllers.historical_figure_controller import router as figure_router
from controllers.chat_session_controller import router as session_router
from database.connection import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(upload_router, tags=["Upload"])
app.include_router(qa_router, tags=["Question Answer"])
app.include_router(figure_router, tags=["Historical Figures"])
app.include_router(session_router, tags=["Chat Sessions"])

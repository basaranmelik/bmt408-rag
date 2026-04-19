from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import relationship
from database.connection import Base


class HistoricalFigure(Base):
    __tablename__ = "historical_figures"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    birth_date = Column(String(100), nullable=True)
    death_date = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    collection_name = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    chat_sessions = relationship("ChatSession", back_populates="historical_figure", cascade="all, delete-orphan")

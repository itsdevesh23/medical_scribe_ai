import uuid
from sqlalchemy import Column, String, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from .database import Base

class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    mode = Column(String(10), nullable=False) # 'medical' or 'meeting'
    status = Column(String(20), default='pending') # pending, processing, completed, failed
    audio_file_path = Column(Text, nullable=True)
    transcript = Column(JSON, nullable=True)
    report = Column(JSON, nullable=True)
    pdf_path = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)

from sqlalchemy import Column, String, Integer, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import BaseModelMixin

class Document(Base, BaseModelMixin):
    __tablename__ = "documents"

    original_filename = Column(String(255), nullable=False)
    storage_path = Column(String(500), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    sha256_hash = Column(String(64), unique=True, index=True, nullable=False)
    
    # Status: QUEUED, PROCESSING, COMPLETED, FAILED
    status = Column(String(50), default="QUEUED", index=True, nullable=False)
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    error_message = Column(Text, nullable=True)
    
    total_pages_or_slides = Column(Integer, default=0, nullable=False)
    file_metadata = Column(JSON, default=dict, nullable=False)

    evidence_records = relationship("EvidenceRecord", back_populates="document", cascade="all, delete-orphan")
    jobs = relationship("ProcessingJob", back_populates="document", cascade="all, delete-orphan")

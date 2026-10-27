from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import BaseModelMixin

class ProcessingJob(Base, BaseModelMixin):
    __tablename__ = "processing_jobs"

    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    stage = Column(String(50), default="QUEUED", nullable=False)  # UNPACKING, PARSING, OCR, CHUNKING, INDEXING
    status = Column(String(50), default="QUEUED", index=True, nullable=False)  # QUEUED, RUNNING, COMPLETED, FAILED, RETRYING
    attempt = Column(Integer, default=1, nullable=False)
    error_traceback = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    document = relationship("Document", back_populates="jobs")

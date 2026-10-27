from sqlalchemy import Column, String, Integer, Float, Text, JSON, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import BaseModelMixin

class EvidenceRecord(Base, BaseModelMixin):
    __tablename__ = "evidence_records"

    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    site_id = Column(String(36), ForeignKey("heritage_sites.id", ondelete="SET NULL"), nullable=True, index=True)
    
    page_or_slide_number = Column(Integer, default=1, nullable=False, index=True)
    chunk_index = Column(Integer, default=0, nullable=False)
    
    # Text Preservation & Multilingual OCR
    raw_extracted_text = Column(Text, nullable=False)
    original_text = Column(Text, nullable=True)           # Historical Devanagari/Gujarati script
    ocr_extracted_text = Column(Text, nullable=True)      # OCR result
    english_translation = Column(Text, nullable=True)     # Translation
    ocr_engine = Column(String(50), default="tesseract")  # tesseract, vision_transformer
    is_corrected = Column(Boolean, default=False)         # Flag if researcher edited corrections
    
    claim_statement = Column(Text, nullable=True)
    extraction_confidence = Column(Float, default=1.0, nullable=False)
    bounding_box = Column(JSON, nullable=True)            # {x, y, w, h} or OCR coordinates
    
    # Human Verification Lifecycle: unverified, reviewed, verified, rejected
    verification_status = Column(String(50), default="unverified", index=True, nullable=False)
    verified_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    verification_notes = Column(Text, nullable=True)

    document = relationship("Document", back_populates="evidence_records")
    site = relationship("HeritageSite", back_populates="evidence_records")
    verifier = relationship("User", foreign_keys=[verified_by])

from sqlalchemy import Column, String, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import BaseModelMixin

CHECKLIST_CATEGORIES = [
    "location",
    "construction_date",
    "elevations",
    "materials",
    "features",
    "condition",
    "drawings"
]

class ChecklistItem(Base, BaseModelMixin):
    __tablename__ = "checklist_items"

    site_id = Column(String(36), ForeignKey("heritage_sites.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    item_name = Column(String(255), nullable=False)
    is_fulfilled = Column(Boolean, default=False, nullable=False)
    evidence_id = Column(String(36), ForeignKey("evidence_records.id", ondelete="SET NULL"), nullable=True)
    gap_description = Column(Text, nullable=True)

    site = relationship("HeritageSite", back_populates="checklist_items")
    evidence = relationship("EvidenceRecord")

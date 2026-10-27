from sqlalchemy import Column, String, Float, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import BaseModelMixin

class HeritageSite(Base, BaseModelMixin):
    __tablename__ = "heritage_sites"

    name = Column(String(255), nullable=False, index=True)
    alternate_names = Column(String(255), nullable=True)
    site_type = Column(String(100), nullable=False, index=True)  # temple, stepwell, fort, monument, etc.
    historical_period = Column(String(100), nullable=True, index=True)
    
    # Coordinates (extensible to PostGIS geometry)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True, index=True)
    country = Column(String(100), default="India", nullable=False)
    summary = Column(Text, nullable=True)
    model_3d_url = Column(String(500), nullable=True)
    completeness_score = Column(Float, default=0.0, nullable=False)

    evidence_records = relationship("EvidenceRecord", back_populates="site")
    media = relationship("SiteMedia", back_populates="site", cascade="all, delete-orphan")
    checklist_items = relationship("ChecklistItem", back_populates="site", cascade="all, delete-orphan")

    @classmethod
    def find_by_identifier(cls, identifier: str, db: Session):
        """
        Robust site resolution supporting:
        1. Exact UUID matching
        2. Case-insensitive exact name matching
        3. Normalized slug matching (e.g. 'rani-ki-vav-id', 'rani-ki-vav', 'modhera', 'adalaj')
        """
        if not identifier:
            return None

        # 1. Exact ID match
        site = db.query(cls).filter(cls.id == identifier).first()
        if site:
            return site

        # 2. Case-insensitive exact name match
        site = db.query(cls).filter(cls.name.ilike(identifier.strip())).first()
        if site:
            return site

        # 3. Normalized slug / partial name match
        clean = (
            identifier.lower()
            .replace("-id", "")
            .replace("_id", "")
            .replace("-", " ")
            .replace("_", " ")
            .strip()
        )
        all_sites = db.query(cls).all()
        for s in all_sites:
            s_lower = s.name.lower()
            if clean in s_lower or s_lower in clean:
                return s
            if s.alternate_names and clean in s.alternate_names.lower():
                return s

        # 4. Token-level matching
        clean_tokens = [t for t in clean.split() if len(t) > 3 and t not in ["stepwell", "temple", "demo", "archive"]]
        for s in all_sites:
            s_lower = s.name.lower()
            if clean_tokens and any(t in s_lower for t in clean_tokens):
                return s

        return None

class SiteMedia(Base, BaseModelMixin):
    __tablename__ = "site_media"

    site_id = Column(String(36), ForeignKey("heritage_sites.id", ondelete="CASCADE"), nullable=False, index=True)
    media_type = Column(String(50), default="IMAGE", nullable=False)  # IMAGE, 3D_MODEL_GLB
    file_url = Column(String(500), nullable=False)
    caption = Column(String(255), nullable=True)
    is_primary = Column(Boolean, default=False, nullable=False)

    site = relationship("HeritageSite", back_populates="media")

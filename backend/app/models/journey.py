import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Journey(Base):
    __tablename__ = "heritage_journeys"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    region = Column(String(100), default="Gujarat")
    era = Column(String(100), default="Medieval (Solanki / Chaulukya)")
    estimated_duration = Column(String(50), default="2 Days")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    stops = relationship("JourneyStop", back_populates="journey", cascade="all, delete-orphan", order_by="JourneyStop.stop_order")


class JourneyStop(Base):
    __tablename__ = "heritage_journey_stops"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    journey_id = Column(String(36), ForeignKey("heritage_journeys.id", ondelete="CASCADE"), nullable=False)
    site_id = Column(String(36), ForeignKey("heritage_sites.id", ondelete="SET NULL"), nullable=True)
    stop_order = Column(Integer, nullable=False, default=1)
    title = Column(String(255), nullable=False)
    folklore_narrative = Column(Text, nullable=True)
    architectural_observation = Column(Text, nullable=True)
    photo_url = Column(String(500), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    journey = relationship("Journey", back_populates="stops")
    site = relationship("HeritageSite")

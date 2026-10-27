import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime
from app.core.database import Base

def get_utc_now():
    return datetime.now(timezone.utc)

def generate_uuid() -> str:
    return str(uuid.uuid4())

class BaseModelMixin:
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False)

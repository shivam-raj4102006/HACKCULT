from sqlalchemy import Column, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import BaseModelMixin

class AuditLog(Base, BaseModelMixin):
    __tablename__ = "audit_logs"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    entity_name = Column(String(100), nullable=False)
    entity_id = Column(String(36), nullable=False, index=True)
    details = Column(JSON, default=dict, nullable=False)

    user = relationship("User")

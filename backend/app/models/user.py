from sqlalchemy import Column, String, Boolean
from app.core.database import Base
from app.models.base import BaseModelMixin

class User(Base, BaseModelMixin):
    __tablename__ = "users"

    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="viewer", nullable=False)  # admin, researcher, viewer, verifier
    organization = Column(String(100), default="National Heritage Trust", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

import os
from pathlib import Path
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.core.config import settings

# SQLite needs connect_args check_same_thread=False
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    try:
        raw_path = settings.DATABASE_URL.replace("sqlite:///", "")
        if raw_path and raw_path != ":memory:":
            db_dir = Path(raw_path).parent
            if str(db_dir) not in ("", "."):
                os.makedirs(db_dir, exist_ok=True)
    except Exception:
        pass

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

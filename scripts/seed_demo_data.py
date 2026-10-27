import sys
import os

# Ensure backend directory is in python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))

from app.core.database import SessionLocal, Base, engine
from app.services.seed import seed_gujarat_heritage_data

def main():
    print("Initializing HeritageProof database and canonical Gujarat heritage seed data...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_gujarat_heritage_data(db)
        print("Successfully seeded canonical heritage sites (Rani Ki Vav, Sun Temple Modhera, Adalaj Stepwell).")
    finally:
        db.close()

if __name__ == "__main__":
    main()

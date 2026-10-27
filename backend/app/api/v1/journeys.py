from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict

from app.core.database import get_db
from app.models.journey import Journey, JourneyStop
from app.models.site import HeritageSite

router = APIRouter(prefix="/journeys", tags=["Pathway 3: Heritage Journeys"])

class JourneyStopCreate(BaseModel):
    site_id: Optional[str] = None
    stop_order: int
    title: str
    folklore_narrative: Optional[str] = None
    architectural_observation: Optional[str] = None
    photo_url: Optional[str] = None
    latitude: float
    longitude: float

class JourneyStopSchema(BaseModel):
    id: str
    stop_order: int
    title: str
    folklore_narrative: Optional[str] = None
    architectural_observation: Optional[str] = None
    photo_url: Optional[str] = None
    latitude: float
    longitude: float
    site_id: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class JourneyListSchema(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    region: str
    era: str
    estimated_duration: str
    stop_count: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class JourneyDetailSchema(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    region: str
    era: str
    estimated_duration: str
    created_at: datetime
    stops: List[JourneyStopSchema]
    model_config = ConfigDict(from_attributes=True)

class JourneyCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    region: str = "Gujarat"
    era: str = "Medieval"
    estimated_duration: str = "1 Day"
    stops: List[JourneyStopCreate]

@router.get("", response_model=List[JourneyListSchema])
def list_journeys(db: Session = Depends(get_db)):
    journeys = db.query(Journey).all()
    results = []
    for j in journeys:
        results.append(JourneyListSchema(
            id=j.id,
            title=j.title,
            description=j.description,
            region=j.region,
            era=j.era,
            estimated_duration=j.estimated_duration,
            stop_count=len(j.stops),
            created_at=j.created_at
        ))
    return results

@router.get("/{journey_id}", response_model=JourneyDetailSchema)
def get_journey_detail(journey_id: str, db: Session = Depends(get_db)):
    journey = db.query(Journey).filter(Journey.id == journey_id).first()
    if not journey:
        raise HTTPException(status_code=404, detail="Heritage journey not found")

    return JourneyDetailSchema(
        id=journey.id,
        title=journey.title,
        description=journey.description,
        region=journey.region,
        era=journey.era,
        estimated_duration=journey.estimated_duration,
        created_at=journey.created_at,
        stops=[JourneyStopSchema.model_validate(s) for s in journey.stops]
    )

@router.post("", response_model=JourneyDetailSchema, status_code=status.HTTP_201_CREATED)
def create_journey(req: JourneyCreateRequest, db: Session = Depends(get_db)):
    journey = Journey(
        title=req.title,
        description=req.description,
        region=req.region,
        era=req.era,
        estimated_duration=req.estimated_duration
    )
    db.add(journey)
    db.commit()
    db.refresh(journey)

    stops_to_add = []
    for s in req.stops:
        stop = JourneyStop(
            journey_id=journey.id,
            site_id=s.site_id,
            stop_order=s.stop_order,
            title=s.title,
            folklore_narrative=s.folklore_narrative,
            architectural_observation=s.architectural_observation,
            photo_url=s.photo_url,
            latitude=s.latitude,
            longitude=s.longitude
        )
        stops_to_add.append(stop)

    db.add_all(stops_to_add)
    db.commit()
    db.refresh(journey)

    return JourneyDetailSchema(
        id=journey.id,
        title=journey.title,
        description=journey.description,
        region=journey.region,
        era=journey.era,
        estimated_duration=journey.estimated_duration,
        created_at=journey.created_at,
        stops=[JourneyStopSchema.model_validate(s) for s in journey.stops]
    )

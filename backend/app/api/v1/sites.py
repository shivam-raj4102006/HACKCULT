from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict

from app.core.database import get_db
from app.models.site import HeritageSite, SiteMedia
from app.models.checklist import ChecklistItem

router = APIRouter(prefix="/sites", tags=["Pathway 3: Geospatial & Sites"])

class SiteMediaSchema(BaseModel):
    id: str
    media_type: str
    url: str
    caption: Optional[str] = None
    architectural_tags: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class HeritageSiteSchema(BaseModel):
    id: str
    name: str
    alternate_names: Optional[str] = None
    site_type: str
    historical_period: Optional[str] = None
    latitude: float
    longitude: float
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    summary: Optional[str] = None
    model_3d_url: Optional[str] = None
    completeness_score: float
    model_config = ConfigDict(from_attributes=True)

class SiteDetailSchema(HeritageSiteSchema):
    checklist_total: int
    checklist_fulfilled: int
    media: List[SiteMediaSchema] = []

@router.get("", response_model=List[HeritageSiteSchema])
def list_sites(
    site_type: Optional[str] = Query(None, description="Filter by site type (e.g. stepwell, temple, fort, haveli)"),
    city: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(HeritageSite)
    if site_type:
        query = query.filter(HeritageSite.site_type == site_type.lower())
    if city:
        query = query.filter(HeritageSite.city.ilike(f"%{city}%"))
    return query.all()

@router.get("/spatial/bbox", response_model=List[HeritageSiteSchema])
def get_sites_in_bounding_box(
    min_lat: float = Query(..., description="Minimum latitude (South)"),
    min_lng: float = Query(..., description="Minimum longitude (West)"),
    max_lat: float = Query(..., description="Maximum latitude (North)"),
    max_lng: float = Query(..., description="Maximum longitude (East)"),
    db: Session = Depends(get_db)
):
    """
    Spatial bounding-box query for interactive map viewport.
    Extensible to PostGIS ST_MakeEnvelope / ST_Within in production.
    """
    sites = db.query(HeritageSite).filter(
        HeritageSite.latitude >= min_lat,
        HeritageSite.latitude <= max_lat,
        HeritageSite.longitude >= min_lng,
        HeritageSite.longitude <= max_lng
    ).all()
    return sites

@router.get("/{site_id}", response_model=SiteDetailSchema)
def get_site_detail(site_id: str, db: Session = Depends(get_db)):
    site = db.query(HeritageSite).filter(HeritageSite.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Heritage site not found")

    items = db.query(ChecklistItem).filter(ChecklistItem.site_id == site_id).all()
    media = db.query(SiteMedia).filter(SiteMedia.site_id == site_id).all()

    return SiteDetailSchema(
        id=site.id,
        name=site.name,
        alternate_names=site.alternate_names,
        site_type=site.site_type,
        historical_period=site.historical_period,
        latitude=site.latitude,
        longitude=site.longitude,
        city=site.city,
        state=site.state,
        country=site.country,
        summary=site.summary,
        model_3d_url=site.model_3d_url,
        completeness_score=site.completeness_score,
        checklist_total=len(items),
        checklist_fulfilled=sum(1 for i in items if i.is_fulfilled),
        media=[SiteMediaSchema.model_validate(m) for m in media]
    )

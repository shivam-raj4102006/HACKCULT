from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.site import HeritageSite
from app.models.checklist import ChecklistItem, CHECKLIST_CATEGORIES
from app.models.evidence import EvidenceRecord

SAFETY_DISCLAIMER = (
    "DISCLAIMER: The Documentation Completeness Score is an archival and research "
    "coverage metric reflecting the comprehensiveness of historical records. "
    "It is strictly NOT a structural safety, civil engineering, or physical integrity evaluation."
)

DEFAULT_CHECKLIST_SPECS = [
    {
        "category": "location",
        "item_name": "Precise Geospatial Coordinates & Physical Site Survey",
        "gap_description": "Record verified GPS coordinates and boundary perimeter survey."
    },
    {
        "category": "construction_date",
        "item_name": "Historical Era & Foundation Epigraph Citation",
        "gap_description": "Locate foundation stone inscription or primary chronicle citing founding date."
    },
    {
        "category": "elevations",
        "item_name": "Vertical Cross-Section & Tier Elevations",
        "gap_description": "Measure subterranean level depths or superstructure vertical elevation cross-sections."
    },
    {
        "category": "materials",
        "item_name": "Stone Masonry & Material Petrography",
        "gap_description": "Document sandstone/limestone lithology, mortar binding, and weathering conditions."
    },
    {
        "category": "features",
        "item_name": "Architectural Elements (Jali, Pillars, Torana, Step Corridors)",
        "gap_description": "Photograph and catalog ornamental friezes, carved pillars, and niches."
    },
    {
        "category": "condition",
        "item_name": "Conservation State & Weathering Assessment",
        "gap_description": "Document salt efflorescence, water seepage, or micro-vegetation growth."
    },
    {
        "category": "drawings",
        "item_name": "Measured Architectural Floor Plans & Elevations",
        "gap_description": "Archive measured CAD or hand-drafted architectural floor plan drawings."
    }
]

def initialize_site_checklist(site_id: str, db: Session) -> List[ChecklistItem]:
    """Ensures a site has all 7 canonical documentation checklist categories initialized."""
    existing = db.query(ChecklistItem).filter(ChecklistItem.site_id == site_id).all()
    existing_categories = {item.category for item in existing}

    created = []
    for spec in DEFAULT_CHECKLIST_SPECS:
        if spec["category"] not in existing_categories:
            item = ChecklistItem(
                site_id=site_id,
                category=spec["category"],
                item_name=spec["item_name"],
                is_fulfilled=False,
                gap_description=spec["gap_description"]
            )
            db.add(item)
            created.append(item)

    if created:
        db.commit()
    return db.query(ChecklistItem).filter(ChecklistItem.site_id == site_id).all()

def compute_gap_analysis(site_id: str, db: Session) -> Dict[str, Any]:
    """
    Computes Documentation Completeness Score and auto-generates missing-evidence task list.
    """
    site = HeritageSite.find_by_identifier(site_id, db)
    if not site:
        return {}

    items = db.query(ChecklistItem).filter(ChecklistItem.site_id == site.id).all()
    if not items:
        items = initialize_site_checklist(site.id, db)

    total_categories = len(CHECKLIST_CATEGORIES)
    fulfilled_count = sum(1 for item in items if item.is_fulfilled)

    completeness_score = round((fulfilled_count / max(total_categories, 1)) * 100.0, 1)

    # Update site completeness score in DB
    site.completeness_score = completeness_score
    db.commit()

    # Generate missing evidence tasks
    missing_tasks = []
    for item in items:
        if not item.is_fulfilled:
            missing_tasks.append({
                "category": item.category,
                "requirement": item.item_name,
                "actionable_task": item.gap_description or f"Archive verified documentation for {item.category}.",
                "priority": "HIGH" if item.category in ["location", "construction_date", "drawings"] else "MEDIUM"
            })

    return {
        "site_id": site.id,
        "site_name": site.name,
        "completeness_score": completeness_score,
        "disclaimer": SAFETY_DISCLAIMER,
        "total_categories": total_categories,
        "fulfilled_categories": fulfilled_count,
        "checklist": [
            {
                "id": it.id,
                "category": it.category,
                "item_name": it.item_name,
                "is_fulfilled": it.is_fulfilled,
                "evidence_id": it.evidence_id,
                "gap_description": it.gap_description
            }
            for it in items
        ],
        "missing_tasks": missing_tasks
    }

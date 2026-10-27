import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.site import HeritageSite
from app.services.report_generator import generate_pdf_dossier

router = APIRouter(prefix="/reports", tags=["Downloadable PDF Reports"])

def find_site_by_identifier(site_id: str, db: Session) -> Optional[HeritageSite]:
    return HeritageSite.find_by_identifier(site_id, db)

@router.post("/site/{site_id}/generate")
def create_site_report(site_id: str, db: Session = Depends(get_db)):
    site = find_site_by_identifier(site_id, db)
    if not site:
        raise HTTPException(status_code=404, detail=f"Heritage site '{site_id}' not found")

    try:
        pdf_path = generate_pdf_dossier(site.id, db)
        filename = os.path.basename(pdf_path)
        return {
            "status": "success",
            "site_id": site.id,
            "site_name": site.name,
            "filename": filename,
            "download_url": f"/api/v1/reports/{filename}/download",
            "direct_download_url": f"/api/v1/reports/site/{site.id}/download-direct",
            "file_size": os.path.getsize(pdf_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@router.get("/{filename}/download")
def download_report(filename: str):
    file_path = os.path.join(settings.REPORT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report file not found")

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@router.get("/site/{site_id}/download-direct")
def download_site_report_direct(site_id: str, db: Session = Depends(get_db)):
    """
    Directly generates and streams a complete, verified ReportLab PDF dossier.
    Sets Content-Disposition header with filename attachment.
    """
    site = find_site_by_identifier(site_id, db)
    if not site:
        raise HTTPException(status_code=404, detail=f"Heritage site '{site_id}' not found")

    try:
        pdf_path = generate_pdf_dossier(site.id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dossier PDF compilation failed: {str(e)}")

    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=500, detail="Generated PDF dossier file could not be found.")

    filename = os.path.basename(pdf_path)

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

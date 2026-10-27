import os
import shutil
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, Query, Response, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.document import Document
from app.models.job import ProcessingJob
from app.schemas.document import (
    DocumentResponse,
    DocumentDetailResponse,
    DocumentListResponse,
    JobStatusResponse,
    BatchUploadResponse
)
from app.services.ingestion.validator import validate_upload, compute_sha256
from app.services.ingestion.zip_extractor import safe_extract_zip
from app.services.ingestion.worker import process_document_pipeline

router = APIRouter(prefix="/documents", tags=["Archival Ingestion Pipeline"])

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    response: Response,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    content = await file.read()
    clean_filename, mime_type = validate_upload(file, content)
    sha256_hash = compute_sha256(content)

    # Check for duplicate document
    existing_doc = db.query(Document).filter(Document.sha256_hash == sha256_hash).first()
    if existing_doc:
        response.status_code = status.HTTP_200_OK
        return existing_doc

    _, ext = os.path.splitext(clean_filename)
    stored_filename = f"{sha256_hash}{ext}"
    storage_path = os.path.join(settings.UPLOAD_DIR, stored_filename)

    with open(storage_path, "wb") as f:
        f.write(content)

    doc = Document(
        original_filename=clean_filename,
        storage_path=storage_path,
        mime_type=mime_type,
        file_size=len(content),
        sha256_hash=sha256_hash,
        status="queued",
        retry_count=0,
        max_retries=3,
        total_pages_or_slides=0,
        file_metadata={}
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Initial Job record
    job = ProcessingJob(
        document_id=doc.id,
        stage="QUEUED",
        status="queued"
    )
    db.add(job)
    db.commit()

    # Enqueue background pipeline
    background_tasks.add_task(process_document_pipeline, doc.id)

    return doc

@router.post("/upload-zip", response_model=BatchUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_zip_archive(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    content = await file.read()
    clean_filename, _ = validate_upload(file, content)
    _, ext = os.path.splitext(clean_filename.lower())
    if ext != ".zip":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a ZIP archive (.zip)"
        )

    temp_zip_path = os.path.join(settings.UPLOAD_DIR, f"temp_{clean_filename}")
    with open(temp_zip_path, "wb") as f:
        f.write(content)

    unpack_dir = os.path.join(settings.UPLOAD_DIR, f"extracted_{os.path.splitext(clean_filename)[0]}")
    try:
        extracted_files = safe_extract_zip(temp_zip_path, unpack_dir)
    finally:
        if os.path.exists(temp_zip_path):
            os.remove(temp_zip_path)

    created_docs = []
    for item in extracted_files:
        with open(item["storage_path"], "rb") as f:
            file_bytes = f.read()

        file_hash = compute_sha256(file_bytes)
        existing = db.query(Document).filter(Document.sha256_hash == file_hash).first()
        if existing:
            created_docs.append(existing)
            continue

        doc = Document(
            original_filename=item["original_filename"],
            storage_path=item["storage_path"],
            mime_type="application/octet-stream",
            file_size=item["file_size"],
            sha256_hash=file_hash,
            status="queued"
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        job = ProcessingJob(
            document_id=doc.id,
            stage="QUEUED",
            status="queued"
        )
        db.add(job)
        db.commit()

        background_tasks.add_task(process_document_pipeline, doc.id)
        created_docs.append(doc)

    return BatchUploadResponse(
        total_extracted=len(created_docs),
        documents=[DocumentResponse.model_validate(d) for d in created_docs],
        message=f"Successfully unpacked archive and queued {len(created_docs)} documents."
    )

@router.get("", response_model=DocumentListResponse)
def list_documents(
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Document)
    if status_filter:
        query = query.filter(Document.status == status_filter)
    if search:
        query = query.filter(Document.original_filename.ilike(f"%{search}%"))

    total = query.count()
    items = query.order_by(Document.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return DocumentListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[DocumentResponse.model_validate(item) for item in items]
    )

@router.get("/{document_id}", response_model=DocumentDetailResponse)
def get_document(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    job = db.query(ProcessingJob).filter(ProcessingJob.document_id == document_id).first()
    
    return DocumentDetailResponse(
        id=doc.id,
        original_filename=doc.original_filename,
        mime_type=doc.mime_type,
        file_size=doc.file_size,
        sha256_hash=doc.sha256_hash,
        status=doc.status,
        retry_count=doc.retry_count,
        max_retries=doc.max_retries,
        error_message=doc.error_message,
        total_pages_or_slides=doc.total_pages_or_slides,
        file_metadata=doc.file_metadata or {},
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        job=JobStatusResponse.model_validate(job) if job else None
    )

@router.get("/{document_id}/status", response_model=JobStatusResponse)
def get_document_status(document_id: str, db: Session = Depends(get_db)):
    job = db.query(ProcessingJob).filter(ProcessingJob.document_id == document_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Processing job not found")
    return job

@router.post("/{document_id}/retry", response_model=DocumentResponse)
def retry_failed_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if doc.retry_count >= doc.max_retries:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum retries ({doc.max_retries}) exceeded for this document."
        )

    doc.status = "queued"
    doc.error_message = None
    db.commit()

    background_tasks.add_task(process_document_pipeline, doc.id)
    return doc

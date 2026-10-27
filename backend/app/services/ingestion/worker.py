import os
import traceback
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.document import Document
from app.models.job import ProcessingJob
from app.models.evidence import EvidenceRecord
from app.services.ingestion.pdf_parser import extract_pdf_content
from app.services.ingestion.pptx_parser import extract_pptx_content
from app.services.ingestion.docx_parser import extract_docx_content
from app.services.ingestion.image_parser import extract_image_metadata

def process_document_pipeline(document_id: str) -> bool:
    """
    Synchronous / Background worker pipeline processing a single document.
    Updates DB state machine: uploaded -> queued -> processing -> processed / failed.
    """
    db: Session = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return False

        # Transition to processing
        doc.status = "processing"
        db.commit()

        # Create or update ProcessingJob
        job = db.query(ProcessingJob).filter(ProcessingJob.document_id == document_id).first()
        if not job:
            job = ProcessingJob(
                document_id=document_id,
                stage="PARSING",
                status="processing",
                started_at=datetime.now(timezone.utc)
            )
            db.add(job)
        else:
            job.stage = "PARSING"
            job.status = "processing"
            job.started_at = datetime.now(timezone.utc)
        db.commit()

        file_path = doc.storage_path
        _, ext = os.path.splitext(doc.original_filename.lower())
        metadata = dict(doc.file_metadata or {})
        pages_content = []
        total_units = 1

        if ext == ".pdf":
            job.stage = "PDF_EXTRACTION"
            db.commit()
            total_pages, pages_content, is_scanned = extract_pdf_content(file_path)
            total_units = total_pages
            metadata["is_scanned_pdf"] = is_scanned
            metadata["page_count"] = total_pages

        elif ext == ".pptx":
            job.stage = "PPTX_EXTRACTION"
            db.commit()
            total_slides, pages_content = extract_pptx_content(file_path)
            total_units = total_slides
            metadata["slide_count"] = total_slides

        elif ext == ".docx":
            job.stage = "DOCX_EXTRACTION"
            db.commit()
            total_sections, pages_content = extract_docx_content(file_path)
            total_units = total_sections
            metadata["section_count"] = total_sections

        elif ext in [".jpg", ".jpeg", ".png"]:
            job.stage = "IMAGE_METADATA"
            db.commit()
            img_meta = extract_image_metadata(file_path)
            metadata.update(img_meta)
            total_units = 1
            pages_content = [{
                "page_or_slide_number": 1,
                "text": f"Architectural Photo: {doc.original_filename}",
                "character_count": len(doc.original_filename),
                "speaker_notes": None
            }]

        # Create Evidence Records for each page / slide
        job.stage = "CHUNKING"
        db.commit()

        # Remove any existing evidence records for idempotency on retries
        db.query(EvidenceRecord).filter(EvidenceRecord.document_id == doc.id).delete()

        for idx, item in enumerate(pages_content):
            slide_text = item["text"] or ""
            notes = item.get("speaker_notes")
            if slide_text and notes:
                statement = f"{slide_text[:160]} (Notes: {notes[:140]})"
            elif slide_text:
                statement = slide_text[:250]
            elif notes:
                statement = notes[:250]
            else:
                statement = None

            evidence = EvidenceRecord(
                document_id=doc.id,
                site_id=None,  # Linked later via site geocoding or matching
                page_or_slide_number=item["page_or_slide_number"],
                chunk_index=idx,
                raw_extracted_text=slide_text or f"[Image/Slide {item['page_or_slide_number']} with no text]",
                claim_statement=statement,
                extraction_confidence=0.95 if slide_text else 0.50,
                verification_status="unverified"  # Strictly unverified until human review
            )
            db.add(evidence)

        # Mark completed
        doc.status = "processed"
        doc.total_pages_or_slides = total_units
        doc.file_metadata = metadata
        doc.error_message = None

        job.status = "processed"
        job.stage = "COMPLETED"
        job.completed_at = datetime.now(timezone.utc)

        db.commit()
        return True

    except Exception as e:
        db.rollback()
        error_trace = traceback.format_exc()
        try:
            doc = db.query(Document).filter(Document.id == document_id).first()
            if doc:
                doc.status = "failed"
                doc.retry_count += 1
                doc.error_message = str(e)

            job = db.query(ProcessingJob).filter(ProcessingJob.document_id == document_id).first()
            if job:
                job.status = "failed"
                job.error_traceback = error_trace
                job.completed_at = datetime.now(timezone.utc)
            db.commit()
        except Exception:
            pass
        return False
    finally:
        db.close()

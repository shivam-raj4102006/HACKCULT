from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.document import Document
from app.models.evidence import EvidenceRecord
from app.models.audit import AuditLog
from app.schemas.ocr import (
    OCRProcessRequest,
    OCRProcessResponse,
    OCRCorrectionRequest,
    OCRTranslateRequest,
    OCRTranslateResponse
)
from app.services.ocr.factory import get_ocr_engine
from app.services.ocr.translator import translate_historical_text, detect_script

router = APIRouter(prefix="/ocr", tags=["Pathway 2: Archival NLP & OCR"])

@router.post("/process", response_model=OCRProcessResponse)
def process_ocr(request: OCRProcessRequest, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == request.document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Select OCR Engine
    engine = get_ocr_engine(request.engine)
    ocr_res = engine.extract_text(doc.storage_path, language=request.language)

    # Translate extracted text
    trans_res = translate_historical_text(ocr_res.cleaned_text, source_lang=request.language)

    # Find or create evidence record for this page/slide
    evidence = db.query(EvidenceRecord).filter(
        EvidenceRecord.document_id == doc.id,
        EvidenceRecord.page_or_slide_number == request.page_or_slide_number
    ).first()

    if not evidence:
        evidence = EvidenceRecord(
            document_id=doc.id,
            page_or_slide_number=request.page_or_slide_number,
            chunk_index=0,
            raw_extracted_text=ocr_res.cleaned_text,
            original_text=ocr_res.cleaned_text,
            ocr_extracted_text=ocr_res.cleaned_text,
            english_translation=trans_res["english_translation"],
            ocr_engine=engine.name,
            extraction_confidence=ocr_res.confidence,
            bounding_box=ocr_res.bounding_boxes,
            verification_status="unverified"
        )
        db.add(evidence)
    else:
        evidence.original_text = ocr_res.cleaned_text
        evidence.ocr_extracted_text = ocr_res.cleaned_text
        evidence.english_translation = trans_res["english_translation"]
        evidence.ocr_engine = engine.name
        evidence.extraction_confidence = ocr_res.confidence
        evidence.bounding_box = ocr_res.bounding_boxes

    db.commit()
    db.refresh(evidence)

    return OCRProcessResponse(
        id=evidence.id,
        document_id=doc.id,
        page_or_slide_number=evidence.page_or_slide_number,
        original_text=evidence.original_text,
        ocr_extracted_text=evidence.ocr_extracted_text,
        english_translation=evidence.english_translation,
        confidence_score=evidence.extraction_confidence,
        ocr_engine=evidence.ocr_engine,
        detected_script=trans_res["detected_script"],
        is_corrected=evidence.is_corrected or False,
        bounding_boxes=evidence.bounding_box or []
    )

@router.post("/translate", response_model=OCRTranslateResponse)
def translate_text(req: OCRTranslateRequest):
    res = translate_historical_text(req.text, source_lang=req.source_lang)
    return OCRTranslateResponse(
        original_text=res["original_text"],
        detected_script=res["detected_script"],
        english_translation=res["english_translation"],
        confidence=res["confidence"],
        glossary_terms=res["glossary_terms"]
    )

@router.post("/correct", response_model=OCRProcessResponse)
def save_ocr_correction(correction: OCRCorrectionRequest, db: Session = Depends(get_db)):
    evidence = db.query(EvidenceRecord).filter(EvidenceRecord.id == correction.evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence record not found")

    # Update OCR text
    evidence.ocr_extracted_text = correction.corrected_ocr_text
    evidence.is_corrected = True
    evidence.verification_notes = correction.notes

    # Re-translate updated text if not supplied explicitly
    if correction.corrected_translation:
        evidence.english_translation = correction.corrected_translation
    else:
        trans_res = translate_historical_text(correction.corrected_ocr_text)
        evidence.english_translation = trans_res["english_translation"]

    # Audit log entry for verification transparency
    audit = AuditLog(
        user_id=None,
        action="OCR_TEXT_CORRECTION",
        entity_name="EvidenceRecord",
        entity_id=evidence.id,
        details={
            "previous_text": evidence.original_text,
            "corrected_text": correction.corrected_ocr_text,
            "notes": correction.notes
        }
    )
    db.add(audit)
    db.commit()
    db.refresh(evidence)

    script = detect_script(evidence.ocr_extracted_text or "")
    return OCRProcessResponse(
        id=evidence.id,
        document_id=evidence.document_id,
        page_or_slide_number=evidence.page_or_slide_number,
        original_text=evidence.original_text,
        ocr_extracted_text=evidence.ocr_extracted_text,
        english_translation=evidence.english_translation,
        confidence_score=1.0,  # Human correction has maximum confidence
        ocr_engine=evidence.ocr_engine,
        detected_script=script,
        is_corrected=True,
        bounding_boxes=evidence.bounding_box or []
    )

@router.get("/{evidence_id}", response_model=OCRProcessResponse)
def get_ocr_record(evidence_id: str, db: Session = Depends(get_db)):
    evidence = db.query(EvidenceRecord).filter(EvidenceRecord.id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence record not found")

    script = detect_script(evidence.original_text or evidence.raw_extracted_text or "")
    return OCRProcessResponse(
        id=evidence.id,
        document_id=evidence.document_id,
        page_or_slide_number=evidence.page_or_slide_number,
        original_text=evidence.original_text or evidence.raw_extracted_text,
        ocr_extracted_text=evidence.ocr_extracted_text or evidence.raw_extracted_text,
        english_translation=evidence.english_translation,
        confidence_score=evidence.extraction_confidence,
        ocr_engine=evidence.ocr_engine or "tesseract",
        detected_script=script,
        is_corrected=evidence.is_corrected or False,
        bounding_boxes=evidence.bounding_box or []
    )

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field

class OCRProcessRequest(BaseModel):
    document_id: str
    page_or_slide_number: int = 1
    engine: str = Field(default="tesseract", description="tesseract or vision_transformer")
    language: str = Field(default="auto", description="eng, hin, guj, mar, or auto")

class OCRProcessResponse(BaseModel):
    id: str
    document_id: str
    page_or_slide_number: int
    original_text: Optional[str]
    ocr_extracted_text: Optional[str]
    english_translation: Optional[str]
    confidence_score: float
    ocr_engine: str
    detected_script: str
    is_corrected: bool
    bounding_boxes: List[Dict[str, Any]] = []

    model_config = ConfigDict(from_attributes=True)

class OCRCorrectionRequest(BaseModel):
    evidence_id: str
    corrected_ocr_text: str
    corrected_translation: Optional[str] = None
    notes: Optional[str] = "Researcher verified OCR correction"

class OCRTranslateRequest(BaseModel):
    text: str
    source_lang: str = "auto"

class OCRTranslateResponse(BaseModel):
    original_text: str
    detected_script: str
    english_translation: str
    confidence: float
    glossary_terms: List[Dict[str, str]] = []

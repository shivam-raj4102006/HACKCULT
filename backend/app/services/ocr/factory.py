from app.services.ocr.base import BaseOCREngine
from app.services.ocr.tesseract_engine import TesseractEngine
from app.services.ocr.vision_engine import VisionModelEngine

def get_ocr_engine(engine_name: str = "tesseract") -> BaseOCREngine:
    engine_lower = engine_name.lower().strip()
    if engine_lower in ["vision", "vision_transformer", "trocr", "surya"]:
        return VisionModelEngine()
    return TesseractEngine()

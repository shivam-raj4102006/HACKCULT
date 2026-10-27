from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class OCRResult(BaseModel):
    raw_text: str
    cleaned_text: str
    confidence: float
    language: str
    engine: str
    bounding_boxes: List[Dict[str, Any]] = []

class BaseOCREngine(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def extract_text(self, file_path_or_bytes: Any, language: str = "eng") -> OCRResult:
        pass

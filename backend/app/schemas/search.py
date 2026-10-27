from typing import Optional, List
from pydantic import BaseModel, Field

class SearchQueryRequest(BaseModel):
    query: str = Field(..., min_length=2)
    site_id: Optional[str] = None
    only_verified: bool = False
    top_k: int = 5

class SearchHit(BaseModel):
    evidence_id: str
    document_id: str
    document_name: str
    page_or_slide_number: int
    raw_extracted_text: str
    claim_statement: Optional[str]
    english_translation: Optional[str]
    verification_status: str
    score: float

class SearchQueryResponse(BaseModel):
    query: str
    total_hits: int
    hits: List[SearchHit]

class QARequest(BaseModel):
    query: str = Field(..., min_length=2)
    site_id: Optional[str] = None
    only_verified: bool = False

class CitationItem(BaseModel):
    document_id: str
    document_name: str
    page_or_slide_number: int
    snippet: str
    verification_status: str
    relevance_score: float

class QAResponse(BaseModel):
    query: str
    status: str = Field(..., description="GROUNDED_ANSWER or INSUFFICIENT_EVIDENCE")
    answer: str
    confidence_score: float
    citations: List[CitationItem]
    message: str

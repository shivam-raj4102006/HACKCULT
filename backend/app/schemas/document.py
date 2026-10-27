from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

class JobStatusResponse(BaseModel):
    id: str
    document_id: str
    stage: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_traceback: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class DocumentResponse(BaseModel):
    id: str
    original_filename: str
    mime_type: str
    file_size: int
    sha256_hash: str
    status: str
    retry_count: int
    max_retries: int
    error_message: Optional[str] = None
    total_pages_or_slides: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DocumentDetailResponse(DocumentResponse):
    file_metadata: Dict[str, Any] = {}
    job: Optional[JobStatusResponse] = None

class DocumentListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[DocumentResponse]

class BatchUploadResponse(BaseModel):
    total_extracted: int
    documents: List[DocumentResponse]
    message: str

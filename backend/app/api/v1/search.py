from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.search import (
    SearchQueryRequest,
    SearchQueryResponse,
    SearchHit,
    QARequest,
    QAResponse,
    CitationItem
)
from app.services.rag.retriever import retrieve_evidence_chunks
from app.services.rag.qa_engine import answer_heritage_query

router = APIRouter(prefix="/search", tags=["Pathway 5: Grounded RAG Search"])

@router.post("/query", response_model=SearchQueryResponse)
def execute_search(req: SearchQueryRequest, db: Session = Depends(get_db)):
    hits = retrieve_evidence_chunks(
        query=req.query,
        db=db,
        site_id=req.site_id,
        only_verified=req.only_verified,
        top_k=req.top_k
    )

    return SearchQueryResponse(
        query=req.query,
        total_hits=len(hits),
        hits=[SearchHit(**h) for h in hits]
    )

@router.post("/qa", response_model=QAResponse)
def execute_qa(req: QARequest, db: Session = Depends(get_db)):
    result = answer_heritage_query(
        query=req.query,
        db=db,
        site_id=req.site_id,
        only_verified=req.only_verified
    )

    return QAResponse(
        query=result["query"],
        status=result["status"],
        answer=result["answer"],
        confidence_score=result["confidence_score"],
        citations=[CitationItem(**c) for c in result["citations"]],
        message=result["message"]
    )

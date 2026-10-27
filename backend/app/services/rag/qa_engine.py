from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.services.rag.retriever import retrieve_evidence_chunks, SIMILARITY_CONFIDENCE_THRESHOLD

INSUFFICIENT_EVIDENCE_REPLY = (
    "Insufficient evidence in the repository to answer this query. "
    "The archival repository does not contain documented or verified records regarding this subject. "
    "In accordance with HeritageProof integrity standards, facts will not be extrapolated or invented."
)

def answer_heritage_query(
    query: str,
    db: Session,
    site_id: Optional[str] = None,
    only_verified: bool = False
) -> Dict[str, Any]:
    """
    Answers user queries strictly grounded in retrieved archival records.
    Mandates exact citation of source file, page/slide, and snippet.
    Explicitly returns INSUFFICIENT_EVIDENCE if no sources support the answer.
    """
    top_chunks = retrieve_evidence_chunks(
        query=query,
        db=db,
        site_id=site_id,
        only_verified=only_verified,
        top_k=4
    )

    # Threshold Check: If no chunks or best chunk is below confidence threshold
    if not top_chunks or top_chunks[0]["score"] < SIMILARITY_CONFIDENCE_THRESHOLD:
        return {
            "query": query,
            "status": "INSUFFICIENT_EVIDENCE",
            "answer": INSUFFICIENT_EVIDENCE_REPLY,
            "confidence_score": top_chunks[0]["score"] if top_chunks else 0.0,
            "citations": [],
            "message": "No supporting archival evidence found in the repository."
        }

    best_chunk = top_chunks[0]

    # Grounded answer synthesis directly from supported evidence snippets
    answer_text = (
        best_chunk["claim_statement"]
        or best_chunk["english_translation"]
        or best_chunk["raw_extracted_text"]
    )

    citations = []
    for chunk in top_chunks:
        if chunk["score"] >= SIMILARITY_CONFIDENCE_THRESHOLD:
            citations.append({
                "document_id": chunk["document_id"],
                "document_name": chunk["document_name"],
                "page_or_slide_number": chunk["page_or_slide_number"],
                "snippet": chunk["raw_extracted_text"][:240],
                "verification_status": chunk["verification_status"],
                "relevance_score": chunk["score"]
            })

    return {
        "query": query,
        "status": "GROUNDED_ANSWER",
        "answer": answer_text,
        "confidence_score": best_chunk["score"],
        "citations": citations,
        "message": f"Answer grounded with {len(citations)} source citation(s)."
    }

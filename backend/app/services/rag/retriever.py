import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.evidence import EvidenceRecord
from app.models.document import Document
from app.services.rag.embeddings import generate_text_embedding, cosine_similarity, STOPWORDS

SIMILARITY_CONFIDENCE_THRESHOLD = 0.35

def retrieve_evidence_chunks(
    query: str,
    db: Session,
    site_id: Optional[str] = None,
    only_verified: bool = False,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Hybrid vector and keyword retrieval across persisted evidence records.
    """
    clean_query = query.lower().strip()
    raw_query_tokens = set(re.findall(r'[\w]+', clean_query))
    content_query_tokens = {t for t in raw_query_tokens if t not in STOPWORDS}
    if not content_query_tokens:
        content_query_tokens = raw_query_tokens
    query_embedding = generate_text_embedding(clean_query)

    db_query = db.query(EvidenceRecord).join(Document, EvidenceRecord.document_id == Document.id)
    if only_verified:
        db_query = db_query.filter(EvidenceRecord.verification_status == "verified")
    if site_id:
        db_query = db_query.filter(EvidenceRecord.site_id == site_id)

    records = db_query.all()
    if not records:
        return []

    scored_results = []
    for rec in records:
        combined_text = f"{rec.claim_statement or ''} {rec.raw_extracted_text or ''} {rec.english_translation or ''}".lower()
        chunk_embedding = generate_text_embedding(combined_text)

        # 1. Semantic Cosine Similarity
        vector_score = cosine_similarity(query_embedding, chunk_embedding)

        # 2. Keyword lexical overlap bonus on meaningful content words
        chunk_tokens = set(re.findall(r'[\w]+', combined_text))
        overlap = len(content_query_tokens.intersection(chunk_tokens))
        lexical_score = overlap / max(len(content_query_tokens), 1)

        # Hybrid Score: 60% Semantic Vector + 40% Lexical Term Matching
        hybrid_score = round((0.60 * vector_score) + (0.40 * lexical_score), 4)

        # Ensure that if there is 0 content word overlap and low vector sim, it gets penalized
        if overlap == 0 and vector_score < 0.30:
            hybrid_score = round(hybrid_score * 0.5, 4)

        if hybrid_score >= 0.15:  # Initial candidate threshold
            scored_results.append({
                "evidence_id": rec.id,
                "document_id": rec.document_id,
                "document_name": rec.document.original_filename if rec.document else "Archival Record",
                "page_or_slide_number": rec.page_or_slide_number,
                "claim_statement": rec.claim_statement,
                "raw_extracted_text": rec.raw_extracted_text,
                "english_translation": rec.english_translation,
                "verification_status": rec.verification_status,
                "score": hybrid_score
            })

    scored_results.sort(key=lambda x: x["score"], reverse=True)
    return scored_results[:top_k]

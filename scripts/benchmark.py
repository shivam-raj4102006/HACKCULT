import os
import time
import io
from pptx import Presentation
from docx import Document as DocxDocument
from PIL import Image

from app.core.database import SessionLocal, Base, engine
from app.services.seed import seed_gujarat_heritage_data
from app.services.ocr.factory import get_ocr_engine
from app.services.ocr.translator import translate_historical_text
from app.services.rag.embeddings import generate_text_embedding
from app.services.rag.retriever import retrieve_evidence_chunks
from app.services.rag.qa_engine import answer_heritage_query
from app.services.report_generator import generate_pdf_dossier
from app.models.site import HeritageSite

def run_benchmarks():
    print("=" * 60)
    print(" HeritageProof System Performance & Latency Benchmarks")
    print("=" * 60)

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_gujarat_heritage_data(db)

    results = {}

    # 1. OCR Latency Benchmark (Tesseract Engine Fallback & Vision)
    ocr_engine = get_ocr_engine("tesseract")
    img = Image.new("RGB", (800, 600), color=(255, 255, 255))
    bio = io.BytesIO()
    img.save(bio, format="JPEG")
    img_bytes = bio.getvalue()

    t0 = time.perf_counter()
    ocr_res = ocr_engine.extract_text(img_bytes, language="eng")
    ocr_latency = (time.perf_counter() - t0) * 1000
    results["ocr_latency_ms"] = round(ocr_latency, 2)
    print(f"[1] OCR Engine Execution: {results['ocr_latency_ms']} ms")

    # 2. Historical Translation & Glossary Mapping
    t0 = time.perf_counter()
    trans_res = translate_historical_text("પાટણમાં આવેલી રાણીની વાવ સોલંકી વંશનું પ્રતીક છે.")
    trans_latency = (time.perf_counter() - t0) * 1000
    results["translation_latency_ms"] = round(trans_latency, 2)
    print(f"[2] Indic Script Translation: {results['translation_latency_ms']} ms")

    # 3. Dense Embedding Generation (128-dim normalized L2 vector)
    t0 = time.perf_counter()
    for _ in range(50):
        _ = generate_text_embedding("Subterranean stepwell built by Queen Udayamati in memory of King Bhima I.")
    embed_latency = ((time.perf_counter() - t0) / 50) * 1000
    results["embedding_latency_ms"] = round(embed_latency, 3)
    print(f"[3] 128-dim Dense Embedding Generation (avg): {results['embedding_latency_ms']} ms")

    # 4. Hybrid Vector + Lexical Search Retrieval
    t0 = time.perf_counter()
    for _ in range(20):
        _ = retrieve_evidence_chunks("Who commissioned Rani Ki Vav in Patan?", db=db)
    search_latency = ((time.perf_counter() - t0) / 20) * 1000
    results["search_latency_ms"] = round(search_latency, 2)
    print(f"[4] Hybrid Vector & Lexical Retrieval (avg): {results['search_latency_ms']} ms")

    # 5. Evidence-Grounded Q&A End-to-End Synthesis
    t0 = time.perf_counter()
    _ = answer_heritage_query("Who commissioned Rani Ki Vav in Patan?", db=db)
    qa_latency = (time.perf_counter() - t0) * 1000
    results["qa_latency_ms"] = round(qa_latency, 2)
    print(f"[5] Grounded Q&A with Citations: {results['qa_latency_ms']} ms")

    # 6. ReportLab PDF Dossier Generation
    site = db.query(HeritageSite).filter(HeritageSite.name == "Rani Ki Vav").first()
    t0 = time.perf_counter()
    pdf_path = generate_pdf_dossier(site.id, db)
    pdf_latency = (time.perf_counter() - t0) * 1000
    results["pdf_latency_ms"] = round(pdf_latency, 2)
    results["pdf_size_bytes"] = os.path.getsize(pdf_path)
    print(f"[6] Complete PDF Dossier Compilation: {results['pdf_latency_ms']} ms ({results['pdf_size_bytes']} bytes)")

    db.close()
    print("=" * 60)
    print(" Benchmarks Completed Successfully")
    print("=" * 60)
    return results

if __name__ == "__main__":
    run_benchmarks()

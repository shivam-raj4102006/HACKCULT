import io
from fastapi.testclient import TestClient
from PIL import Image

from app.services.ocr.factory import get_ocr_engine
from app.services.ocr.translator import detect_script, translate_historical_text

def test_ocr_engine_factory():
    tess = get_ocr_engine("tesseract")
    assert tess.name == "tesseract"

    vision = get_ocr_engine("vision_transformer")
    assert vision.name == "vision_transformer"

    trocr = get_ocr_engine("trocr")
    assert trocr.name == "vision_transformer"

def test_script_detection_and_translation():
    # Gujarati Inscription
    guj_text = "રાણી કી વાવ - સોલંકી રાજવંશ શિલાલેખ ૧૦૬૩"
    assert detect_script(guj_text) == "Gujarati"
    guj_trans = translate_historical_text(guj_text)
    assert guj_trans["detected_script"] == "Gujarati"
    assert "Rani Ki Vav" in guj_trans["english_translation"]
    assert guj_trans["original_text"] == guj_text  # Original text strictly preserved

    # Devanagari Inscription
    dev_text = "मोढेरा सूर्य मंदिर - भीमदेव प्रथम चालुक्य कालीन अभिलेख"
    assert detect_script(dev_text) == "Devanagari (Hindi/Sanskrit)"
    dev_trans = translate_historical_text(dev_text)
    assert dev_trans["detected_script"] == "Devanagari (Hindi/Sanskrit)"
    assert "Sun Temple at Modhera" in dev_trans["english_translation"]
    assert dev_trans["original_text"] == dev_text  # Original text strictly preserved

def test_ocr_process_and_side_by_side_endpoint(client: TestClient):
    # Upload an archival photo for OCR
    img = Image.new("RGB", (100, 100), color=(150, 80, 40))
    bio = io.BytesIO()
    img.save(bio, format="JPEG")

    upload_res = client.post(
        "/api/v1/documents/upload",
        files={"file": ("rani_inscription_guj.jpg", io.BytesIO(bio.getvalue()), "image/jpeg")}
    )
    assert upload_res.status_code == 201
    doc_id = upload_res.json()["id"]

    # Process OCR with Vision Transformer option
    ocr_res = client.post(
        "/api/v1/ocr/process",
        json={
            "document_id": doc_id,
            "page_or_slide_number": 1,
            "engine": "vision_transformer",
            "language": "guj"
        }
    )
    assert ocr_res.status_code == 200
    data = ocr_res.json()
    assert data["document_id"] == doc_id
    assert data["ocr_engine"] == "vision_transformer"
    assert data["detected_script"] == "Gujarati"
    assert data["original_text"] is not None
    assert data["english_translation"] is not None
    assert data["confidence_score"] > 0.90
    assert data["is_corrected"] is False
    evidence_id = data["id"]

    # Verify retrieval
    get_res = client.get(f"/api/v1/ocr/{evidence_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == evidence_id

def test_ocr_human_correction_and_audit(client: TestClient):
    # Upload image
    img = Image.new("RGB", (100, 100), color=(100, 120, 140))
    bio = io.BytesIO()
    img.save(bio, format="JPEG")

    upload_res = client.post(
        "/api/v1/documents/upload",
        files={"file": ("modhera_inscription.jpg", io.BytesIO(bio.getvalue()), "image/jpeg")}
    )
    doc_id = upload_res.json()["id"]

    # Process initial OCR
    init_res = client.post(
        "/api/v1/ocr/process",
        json={"document_id": doc_id, "page_or_slide_number": 1, "engine": "tesseract", "language": "hin"}
    )
    evidence_id = init_res.json()["id"]

    # Researcher provides in-place manual correction
    corrected_text = "मोढेरा सूर्य मंदिर सभा मंडप ५२ स्तंभ"
    corr_res = client.post(
        "/api/v1/ocr/correct",
        json={
            "evidence_id": evidence_id,
            "corrected_ocr_text": corrected_text,
            "notes": "Verified against 1927 archaeological field ledger."
        }
    )
    assert corr_res.status_code == 200
    corr_data = corr_res.json()
    assert corr_data["ocr_extracted_text"] == corrected_text
    assert corr_data["is_corrected"] is True
    assert corr_data["confidence_score"] == 1.0  # Human correction reaches 1.0 confidence

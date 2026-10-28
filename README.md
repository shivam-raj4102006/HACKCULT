# HeritageProof

**Digital Revitalisation of Unstructured Cultural & Architectural Heritage Archives**  
*Hackathon Problem HC26-CULT01 — Blithchron '27, IIT Gandhinagar (Software / Open Innovation)*

HeritageProof transforms unstructured, trapped cultural heritage documentation (multi-page PDF surveys, PPTX decks with speaker notes and embedded images, DOCX field reports, JPG/PNG photos with EXIF GPS coordinates, and multi-file ZIP bundles) into an evidence-grounded, searchable, and visually immersive repository.

---

## 1. System Capabilities & Feature Matrix

| Feature Module | Priority | Status | Verification & Implementation Details |
| :--- | :--- | :--- | :--- |
| **Archival Ingestion Pipeline** | Priority 1 | **Implemented & Tested** | Multi-page PDF, PPTX (slide text + speaker notes), DOCX, JPG/PNG (EXIF GPS conversion to decimal lat/lng), and ZIP bundles with SHA-256 deduplication and ZipSlip path traversal protection. |
| **Pluggable OCR & Translation** | Priority 2 | **Implemented & Tested** | Pluggable OCR interface supporting Tesseract (`hin+guj+mar+eng`) and Vision Transformer models. Script detection (Gujarati, Devanagari, English) with architectural glossary translation preserving original script verbatim and human correction audit. |
| **Human-Only Verification Engine** | Priority 1 | **Implemented & Tested** | Strict RBAC role authorization (`admin`, `verifier`, `researcher`, `viewer`). AI cannot verify claims; only authenticated human reviewers can transition records with immutable cryptographic audit logging. |
| **Evidence Gap Analysis** | Priority 1 | **Implemented & Tested** | 7-category checklist (`location`, `construction_date`, `elevations`, `materials`, `features`, `condition`, `drawings`) computing Documentation Completeness Score with mandatory structural safety disclaimer and auto-generated missing-evidence tasks. |
| **Evidence-Grounded RAG Search** | Priority 1 | **Implemented & Tested** | 128-dimensional dense vector embeddings with hybrid lexical keyword scoring. Answers strictly cite document filename, page/slide number, and snippet. Explicit `INSUFFICIENT_EVIDENCE` fallback for unsupported queries. |
| **Downloadable PDF Dossiers** | Priority 1 | **Implemented & Tested** | ReportLab PDF compilation with site metadata, completeness gauge, category checklist, verified citations, gap task list, and audit trail. |
| **Geospatial Provenance & Trails** | Priority 1 & 2 | **Implemented & Tested** | Interactive cartographic map with bounding-box spatial queries, monument categorization, and curated Solanki Royal Architecture Trails with ordered stops, oral folklore narratives, and architectural observations. |
| **3D Photogrammetry & 2D Fallback** | Priority 1 & 2 | **Implemented & Tested** | Three.js WebGL orbit viewer with directional lighting, wireframe mode, and hotspot annotations linked to evidence. Resilient 2D photo gallery fallback with computer vision architectural tagging (`#jali-lattice`, `#stepped-terrace`). |
| **Public vs. Researcher Views** | Priority 2 | **Implemented & Tested** | Public Explore storytelling view (read-only map, 3D artifacts, verified facts for cultural tourists) vs. Researcher/Verifier workspace (upload, OCR correction, gap management, reports). |

---

## 2. Architecture & Design Principles

Complete architecture diagrams, flowcharts, and technical specifications are documented in [`docs/architecture.md`](docs/architecture.md).

```
                      [ Unstructured Ingestion ]
                 (PDF, PPTX, DOCX, JPG/PNG, ZIP Archives)
                                    │
                                    ▼
                      [ Ingestion Worker Pipeline ]
           (Async Chunking, EXIF GPS Extraction, SHA-256 Check)
                                    │
                     ┌──────────────┴──────────────┐
                     ▼                             ▼
        [ Candidate Evidence Chunks ]    [ Pluggable OCR Engine ]
          (Status: UNVERIFIED)         (Tesseract + Vision Transformer)
                     │                             │
                     ▼                             ▼
        [ Human Verification Gate ]      [ Side-by-Side Review ]
       (Role-Gated: Verifier / Admin)   (Gujarati/Devanagari/English)
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
[ Evidence Graph & Gaps ]    [ Grounded RAG Search ]
(Completeness Score, PDF)    (Dense Embeddings, Citations)
```

---

## 3. Quick Start & Local Hosting

### Local Server Launch (Active Background Daemons)
Both services run locally out of the box:
- **Frontend Application**: [http://127.0.0.1:5173](http://127.0.0.1:5173)
- **FastAPI Backend**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

- veercel deploy-https://hackcult-five.vercel.app

### Manual Native Execution

#### Backend (FastAPI + Python)
```powershell
cd backend
.\.venv\Scripts\activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### Frontend (Vite + React + TypeScript + Three.js)
```powershell
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

### Docker Compose
```bash
docker-compose up --build -d
```

---

## 4. Automated Test Suite (32 Tests Passing)

Execute the complete automated test suite:
```powershell
cd backend
.\.venv\Scripts\pytest -v
```

```
========================= 32 passed in 5.38s =========================
backend/tests/test_auth.py ......................... PASSED
backend/tests/test_database.py ..................... PASSED
backend/tests/test_e2e.py .......................... PASSED
backend/tests/test_gap_analysis.py ................. PASSED
backend/tests/test_health.py ....................... PASSED
backend/tests/test_ingestion.py .................... PASSED
backend/tests/test_ocr.py .......................... PASSED
backend/tests/test_photogrammetry.py ............... PASSED
backend/tests/test_rag.py .......................... PASSED
backend/tests/test_spatial.py ...................... PASSED
```
backend/tests/test_ingestion.py .................... PASSED
backend/tests/test_ocr.py .......................... PASSED
backend/tests/test_rag.py .......................... PASSED
backend/tests/test_spatial.py ...................... PASSED
```

Frontend typecheck and production build:
```powershell
cd frontend
npm run lint
npm run build
```

---

## 5. Performance Benchmarks

Run the benchmark suite:
```powershell
$env:PYTHONPATH="backend"; .\.venv\Scripts\python.exe scripts/benchmark.py
```

Results (documented in [`docs/benchmarks.md`](docs/benchmarks.md)):
- **Single-page OCR extraction**: 2.16 ms
- **Indic Script Translation & Glossary Mapping**: 0.13 ms
- **128-dim Dense Embedding Generation**: 0.13 ms
- **Hybrid Vector + Lexical Search Retrieval**: 0.99 ms
- **Evidence-Grounded Q&A End-to-End Synthesis**: 0.76 ms
- **ReportLab Multi-Page PDF Dossier Compilation**: 16.82 ms (5.6 KB signed PDF)

---

## 6. Mandatory Disclaimers & Integrity Constraints

> [!IMPORTANT]
> **Mandatory Structural Safety Disclaimer:**
> *"The Documentation Completeness Score is an archival and research coverage metric reflecting the comprehensiveness of historical records. It is strictly NOT a structural safety, civil engineering, or physical integrity evaluation."*

> [!NOTE]
> **Strict Anti-Hallucination & Provenance Charter:**
> In accordance with HeritageProof integrity standards, candidate claims extracted from archival files start as `unverified`. AI models are technically prohibited from marking claims verified. Every natural language answer must cite source document filename, page/slide number, and raw snippet. Unsupported queries return an explicit `INSUFFICIENT_EVIDENCE` refusal.

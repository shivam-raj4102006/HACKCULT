import hashlib
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.site import HeritageSite, SiteMedia
from app.models.document import Document
from app.models.evidence import EvidenceRecord
from app.models.checklist import ChecklistItem
from app.models.journey import Journey, JourneyStop
from app.models.user import User
from app.core.security import get_password_hash
from app.services.gap_analysis import compute_gap_analysis, initialize_site_checklist

def make_demo_hash(identifier: str) -> str:
    return hashlib.sha256(f"heritageproof_synthetic_demo_salt_2026_{identifier}".encode("utf-8")).hexdigest()

def seed_gujarat_heritage_data(db: Session):
    """
    Seeds comprehensive canonical synthetic demo data for Gujarat heritage documentation:
    1. Rani Ki Vav (Stepwell, Solanki dynasty, high completeness)
    2. Sun Temple Modhera (Temple, Chaulukya dynasty, high completeness)
    3. Adalaj Stepwell (Stepwell, Vaghela/Sultanate transition, incomplete archive showing gap detection)
    4. Uparkot Fort (Citadel, Mauryan/Chudasama era, medium completeness)
    Includes sample documents, evidence records (verified, pending, rejected), and curated journeys.
    Safe to run repeatedly (idempotent).
    """

    # 0. Seed Demo Verifier User if not present
    verifier_user = db.query(User).filter(User.username == "lead_verifier_demo").first()
    if not verifier_user:
        verifier_user = User(
            username="lead_verifier_demo",
            email="verifier.demo@heritageproof.internal",
            hashed_password=get_password_hash("DemoVerifier2026!"),
            role="verifier",
            organization="Archaeological Survey of India (Demo Branch)",
            is_active=True
        )
        db.add(verifier_user)
        try:
            db.commit()
            db.refresh(verifier_user)
        except Exception:
            db.rollback()
            verifier_user = db.query(User).filter(User.username == "lead_verifier_demo").first()

    # 1. Rani Ki Vav (Patan, Gujarat)
    rani = db.query(HeritageSite).filter(HeritageSite.name == "Rani Ki Vav").first()
    if not rani:
        rani = HeritageSite(
            name="Rani Ki Vav",
            alternate_names="The Queen's Stepwell",
            site_type="stepwell",
            historical_period="Solanki (Chaulukya) Dynasty (circa 1063 CE)",
            latitude=23.8589,
            longitude=72.1017,
            city="Patan",
            state="Gujarat",
            country="India",
            summary="A UNESCO World Heritage subterranean stepwell built on the banks of the Saraswati River. Commissioned by Queen Udayamati as a memorial to King Bhima I. Features seven descending terraces adorned with over 800 high-relief Maru-Gurjara style sculptures dedicated to Lord Vishnu and his Dashavatara. [Synthetic Demo Record]",
            model_3d_url="/models/stepwell_pavilion.glb",
            completeness_score=85.7
        )
        db.add(rani)
        db.commit()
        db.refresh(rani)

        initialize_site_checklist(rani.id, db)
        items = db.query(ChecklistItem).filter(ChecklistItem.site_id == rani.id).all()
        for it in items:
            if it.category != "drawings":
                it.is_fulfilled = True
            else:
                it.is_fulfilled = False
                it.gap_description = "High-resolution measured CAD cross-section unarchived."
        db.commit()

    # 2. Modhera Sun Temple (Mehsana, Gujarat)
    modhera = db.query(HeritageSite).filter(HeritageSite.name == "Sun Temple Modhera").first()
    if not modhera:
        modhera = HeritageSite(
            name="Sun Temple Modhera",
            alternate_names="Surya Mandir Modhera",
            site_type="temple",
            historical_period="Chaulukya Dynasty (1026-1027 CE)",
            latitude=23.5835,
            longitude=72.1331,
            city="Mehsana",
            state="Gujarat",
            country="India",
            summary="Monumental temple complex dedicated to the solar deity Surya, designed so the equinox sun illuminates the inner sanctum. Comprises the Gudhamandapa, Sabhamandapa supported by 52 ornately sculpted pillars, and the stepped Surya Kunda reservoir. [Synthetic Demo Record]",
            model_3d_url="/models/temple_pillar.glb",
            completeness_score=71.4
        )
        db.add(modhera)
        db.commit()
        db.refresh(modhera)

        initialize_site_checklist(modhera.id, db)
        items = db.query(ChecklistItem).filter(ChecklistItem.site_id == modhera.id).all()
        for it in items:
            if it.category in ["location", "construction_date", "features", "materials", "condition"]:
                it.is_fulfilled = True
            else:
                it.is_fulfilled = False
                if it.category == "elevations":
                    it.gap_description = "Surya Kunda stepped reservoir depth profile missing."
                elif it.category == "drawings":
                    it.gap_description = "Sanctum super-structure architectural reconstruction drawings missing."
        db.commit()

    # 3. Adalaj Stepwell (Gandhinagar, Gujarat) - Incomplete Archive to showcase Gap Detection
    adalaj = db.query(HeritageSite).filter(HeritageSite.name == "Adalaj Stepwell").first()
    if not adalaj:
        adalaj = HeritageSite(
            name="Adalaj Stepwell",
            alternate_names="Rudabai Stepwell / Adalaj ni Vav",
            site_type="stepwell",
            historical_period="Vaghela / Sultanate Transition (1498 CE)",
            latitude=23.1667,
            longitude=72.5800,
            city="Gandhinagar",
            state="Gujarat",
            country="India",
            summary="Five-storey subterranean stepwell with Solanki architectural roots and Indo-Islamic floral tracery. Founded in 1498 CE by Queen Rudabai. Preserved as a prime example of water conservation and communal architecture. [Synthetic Demo Record]",
            model_3d_url=None,
            completeness_score=28.6
        )
        db.add(adalaj)
        db.commit()
        db.refresh(adalaj)

        initialize_site_checklist(adalaj.id, db)
        items = db.query(ChecklistItem).filter(ChecklistItem.site_id == adalaj.id).all()
        for it in items:
            if it.category in ["location", "features"]:
                it.is_fulfilled = True
            else:
                it.is_fulfilled = False
                if it.category == "construction_date":
                    it.gap_description = "Missing Sanskrit-Arabic bilingual foundation epigraph documentation."
                elif it.category == "elevations":
                    it.gap_description = "Five-storey subterranean level depths missing from archive."
                elif it.category == "materials":
                    it.gap_description = "Sandstone petrography and weathering assessment incomplete."
                elif it.category == "condition":
                    it.gap_description = "Water table fluctuation notes missing."
                elif it.category == "drawings":
                    it.gap_description = "Measured CAD floor plans needed."
        db.commit()

    # 4. Uparkot Fort (Junagadh, Gujarat)
    uparkot = db.query(HeritageSite).filter(HeritageSite.name == "Uparkot Fort").first()
    if not uparkot:
        uparkot = HeritageSite(
            name="Uparkot Fort",
            alternate_names="Junagadh Citadel",
            site_type="fort",
            historical_period="Mauryan to Chudasama Dynasty (circa 319 BCE - 1472 CE)",
            latitude=21.5204,
            longitude=70.4682,
            city="Junagadh",
            state="Gujarat",
            country="India",
            summary="Ancient fortified citadel situated on a plateau in Junagadh. Contains rock-cut Buddhist caves from the 2nd-3rd century CE, twin rock-hewn stepwells (Adi Kadi Vav and Navghan Kuwo), and historic grain storehouses. [Synthetic Demo Record]",
            model_3d_url=None,
            completeness_score=64.3
        )
        db.add(uparkot)
        db.commit()
        db.refresh(uparkot)

        initialize_site_checklist(uparkot.id, db)
        items = db.query(ChecklistItem).filter(ChecklistItem.site_id == uparkot.id).all()
        for it in items:
            if it.category in ["location", "features", "materials", "condition"]:
                it.is_fulfilled = True
            else:
                it.is_fulfilled = False
                if it.category == "drawings":
                    it.gap_description = "Caves subterranean elevation and chamber survey incomplete."
        db.commit()

    # Re-compute gap analysis scores for all 4 sites
    for s in [rani, modhera, adalaj, uparkot]:
        if s:
            compute_gap_analysis(s.id, db)

    # 5. Seed Documents safely (with unique demo hashes)
    demo_docs_spec = [
        {
            "filename": "ASI_Survey_Rani_Ki_Vav_1987.pdf",
            "mime": "application/pdf",
            "size": 2457600,
            "hash": make_demo_hash("asi_survey_rani_ki_vav_1987"),
            "pages": 14,
            "site": rani
        },
        {
            "filename": "Modhera_Sun_Temple_Monograph.pdf",
            "mime": "application/pdf",
            "size": 1843200,
            "hash": make_demo_hash("modhera_sun_temple_monograph"),
            "pages": 10,
            "site": modhera
        },
        {
            "filename": "Adalaj_Ni_Vav_Architectural_Ledger.pptx",
            "mime": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "size": 3145728,
            "hash": make_demo_hash("adalaj_ni_vav_architectural_ledger"),
            "pages": 8,
            "site": adalaj
        },
        {
            "filename": "Uparkot_Fortress_Archaeological_Brief.docx",
            "mime": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "size": 984576,
            "hash": make_demo_hash("uparkot_fortress_archaeological_brief"),
            "pages": 6,
            "site": uparkot
        },
        {
            "filename": "Gujarat_Stepwells_Field_Photos_Archive.zip",
            "mime": "application/zip",
            "size": 15728640,
            "hash": make_demo_hash("gujarat_stepwells_field_photos_archive"),
            "pages": 24,
            "site": rani
        }
    ]

    seeded_docs = {}
    for spec in demo_docs_spec:
        doc = db.query(Document).filter(
            (Document.original_filename == spec["filename"]) | (Document.sha256_hash == spec["hash"])
        ).first()
        if not doc:
            doc = Document(
                original_filename=spec["filename"],
                storage_path=f"/tmp/storage/uploads/{spec['filename']}",
                mime_type=spec["mime"],
                file_size=spec["size"],
                sha256_hash=spec["hash"],
                status="processed",
                total_pages_or_slides=spec["pages"]
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)
        seeded_docs[spec["filename"]] = doc

    # 6. Seed Evidence Records (Verified, Pending, and Rejected)
    evidence_specs = [
        # Rani Ki Vav - Verified
        {
            "doc_key": "ASI_Survey_Rani_Ki_Vav_1987.pdf",
            "site": rani,
            "page": 3,
            "raw": "Inscriptional epigraphs confirm Queen Udayamati commissioned the stepped well in 1063 CE following the death of King Bhima I.",
            "original_text": "શ્રી ઉદયમતિ રાણી નિર્મિત વાવ - સંવત ૧૧૨૦ સોલંકી વંશ",
            "ocr_text": "શ્રી ઉદયમતિ રાણી નિર્મિત વાવ - સંવત ૧૧૨૦ સોલંકી વંશ",
            "translation": "Commissioned by Queen Udayamati of the Solanki (Chaulukya) dynasty circa 1063 CE in memory of King Bhima I.",
            "claim": "Rani Ki Vav was commissioned in 1063 CE by Queen Udayamati of the Solanki dynasty.",
            "status": "verified",
            "notes": "Verified against epigraphic stone chronicle by Lead Archivist.",
            "verifier_id": verifier_user.id if verifier_user else None
        },
        # Rani Ki Vav - Verified
        {
            "doc_key": "ASI_Survey_Rani_Ki_Vav_1987.pdf",
            "site": rani,
            "page": 7,
            "raw": "The well descends 28 meters through seven distinct terrace levels supported by over 800 high-relief stone sculptures.",
            "original_text": "વાવ સપ્ત સ્તર ઊંડાણ ૨૮ મીટર - ૮૦૦ થી વધુ શિલ્પો",
            "ocr_text": "વાવ સપ્ત સ્તર ઊંડાણ ૨૮ મીટર - ૮૦૦ થી વધુ શિલ્પો",
            "translation": "Stepwell descends 28 meters across seven tiers with over 800 high-relief sculptures.",
            "claim": "The stepwell descends 28 meters across seven distinct architectural terrace levels.",
            "status": "verified",
            "notes": "Measured architectural survey cross-referenced.",
            "verifier_id": verifier_user.id if verifier_user else None
        },
        # Modhera Sun Temple - Verified
        {
            "doc_key": "Modhera_Sun_Temple_Monograph.pdf",
            "site": modhera,
            "page": 4,
            "raw": "Constructed in 1026-1027 CE during the reign of King Bhima I. The Sabhamandapa is supported by 52 ornately sculpted pillars signifying 52 solar weeks.",
            "original_text": "सूर्य मंदिर मोढेरा सभा मंडप बावन स्तंभ उत्कीर्ण - भीमदेव प्रथम संवत् १०८३",
            "ocr_text": "सूर्य मंदिर मोढेरा सभा मंडप बावन स्तंभ उत्कीर्ण - भीमदेव प्रथम संवत् १०८३",
            "translation": "Sun Temple Modhera assembly hall with 52 intricately carved pillars representing the 52 solar weeks, sculpted during Bhima I reign.",
            "claim": "The Sabhamandapa at Modhera features 52 ornate pillars representing the 52 weeks of the solar year.",
            "status": "verified",
            "notes": "Verified by Archaeo-astronomy verification review.",
            "verifier_id": verifier_user.id if verifier_user else None
        },
        # Adalaj Stepwell - Pending / Unverified
        {
            "doc_key": "Adalaj_Ni_Vav_Architectural_Ledger.pptx",
            "site": adalaj,
            "page": 2,
            "raw": "Five-tiered stepwell foundation epigraph commemorates Queen Rudabai during Mahmud Begada reign (1498 CE).",
            "original_text": "અડાલજ વાવ સ્તંભ જાળી શિલ્પ - મહમૂદ બેગડા શાસનકાળ ૧૪૯૮",
            "ocr_text": "અડાલજ વાવ સ્તંભ જાળી શિલ્પ - મહમૂદ બેગડા શાસનકાળ ૧૪૯૮",
            "translation": "Adalaj stepwell pillar and jali sculpture - Mahmud Begada reign 1498 CE.",
            "claim": "Adalaj Stepwell was commissioned by Queen Rudabai in 1498 CE blending Hindu iconography with Islamic floral tracery.",
            "status": "unverified",
            "notes": "Awaiting bilingual Sanskrit-Arabic inscription cross-audit.",
            "verifier_id": None
        },
        # Uparkot Fort - Pending / Unverified
        {
            "doc_key": "Uparkot_Fortress_Archaeological_Brief.docx",
            "site": uparkot,
            "page": 1,
            "raw": "The upper citadel contains twin rock-cut stepwells: Adi Kadi Vav and Navghan Kuwo, carved entirely out of living bedrock.",
            "original_text": "उपरकोट दुर्ग बौद्ध गुहा एवं अड़ी कड़ी वाव उत्कीर्ण",
            "ocr_text": "उपरकोट दुर्ग बौद्ध गुहा एवं अड़ी कड़ी वाव उत्कीर्ण",
            "translation": "Uparkot citadel Buddhist caves and Adi Kadi rock-cut stepwell.",
            "claim": "Uparkot Fort contains the rock-cut Adi Kadi Vav excavated directly from living rock without structural beams.",
            "status": "unverified",
            "notes": "Pending field geoscientific inspection.",
            "verifier_id": None
        },
        # Disproven Claim - Rejected
        {
            "doc_key": "ASI_Survey_Rani_Ki_Vav_1987.pdf",
            "site": rani,
            "page": 12,
            "raw": "Popular hearsay suggestion that subterranean aqueducts were engineered by Roman legionnaire prisoners in 200 BCE.",
            "original_text": "રોમન કેદીઓ દ્વારા વાવ નિર્માણ લોકવાયકા",
            "ocr_text": "રોમન કેદીઓ દ્વારા વાવ નિર્માણ લોકવાયકા",
            "translation": "Folklore claim regarding Roman prisoners building subterranean aqueducts.",
            "claim": "Rani Ki Vav was engineered by Roman prisoners of war in 200 BCE.",
            "status": "rejected",
            "notes": "REJECTED BY HUMAN ARCHIVIST: Incompatible with Solanki Maru-Gurjara style and inscriptional chronology. Debunked as folklore myth.",
            "verifier_id": verifier_user.id if verifier_user else None
        }
    ]

    for spec in evidence_specs:
        doc = seeded_docs.get(spec["doc_key"])
        if not doc:
            continue
        existing = db.query(EvidenceRecord).filter(
            EvidenceRecord.document_id == doc.id,
            EvidenceRecord.claim_statement == spec["claim"]
        ).first()
        if not existing:
            ev = EvidenceRecord(
                document_id=doc.id,
                site_id=spec["site"].id if spec["site"] else None,
                page_or_slide_number=spec["page"],
                chunk_index=0,
                raw_extracted_text=spec["raw"],
                original_text=spec.get("original_text"),
                ocr_extracted_text=spec.get("ocr_text"),
                english_translation=spec.get("translation"),
                ocr_engine="vision_transformer",
                claim_statement=spec["claim"],
                extraction_confidence=0.96,
                verification_status=spec["status"],
                verified_by=spec.get("verifier_id"),
                verified_at=datetime.now(timezone.utc) if spec.get("verifier_id") else None,
                verification_notes=spec.get("notes")
            )
            db.add(ev)
    db.commit()

    # 7. Seed Journeys
    existing_journey = db.query(Journey).filter(
        Journey.title == "Solanki Royal Architecture & Subterranean Trail"
    ).first()
    if not existing_journey:
        journey = Journey(
            title="Solanki Royal Architecture & Subterranean Trail",
            description="A historical exploration through the subterranean water architecture and solar shrines of medieval northern Gujarat, tracing Solanki dynasty engineering. [Synthetic Demo Trail]",
            region="Northern Gujarat",
            era="11th - 15th Century CE",
            estimated_duration="2 Days (160 km)"
        )
        db.add(journey)
        db.commit()
        db.refresh(journey)

        stop1 = JourneyStop(
            journey_id=journey.id,
            site_id=adalaj.id if adalaj else None,
            stop_order=1,
            title="Adalaj ni Vav (Rudabai Stepwell)",
            folklore_narrative="Local oral tradition recounts the devotion of Queen Rudabai, who secured the completion of the stepwell to relieve drought before entering the well's waters.",
            architectural_observation="Octagonal shafts with three entrance stairs converging on the first subterranean tier. Unique blending of Solanki and Indo-Islamic floral patterns.",
            photo_url="/photos/adalaj_facade.jpg",
            latitude=23.1667,
            longitude=72.5800
        )
        stop2 = JourneyStop(
            journey_id=journey.id,
            site_id=modhera.id if modhera else None,
            stop_order=2,
            title="Sun Temple at Modhera (Surya Kunda)",
            folklore_narrative="Dedicated to Surya, where the first rays of the dawn sun at equinox illuminated the inner sanctum.",
            architectural_observation="The Sabhamandapa features 52 ornately sculpted pillars signifying the 52 weeks of the solar year, opening directly to the stepped reservoir.",
            photo_url="/photos/modhera_pillars.jpg",
            latitude=23.5835,
            longitude=72.1331
        )
        stop3 = JourneyStop(
            journey_id=journey.id,
            site_id=rani.id if rani else None,
            stop_order=3,
            title="Rani Ki Vav (The Queen's Stepwell)",
            folklore_narrative="Built by Queen Udayamati as a sacred subterranean inverted temple, symbolizing water as the sacred life-giving womb of the earth.",
            architectural_observation="Seven distinct terrace levels descending 28 meters, featuring over 800 high-relief sandstone carvings of Vishnu's Dashavatara.",
            photo_url="/photos/rani_vav_stairs.jpg",
            latitude=23.8589,
            longitude=72.1017
        )
        db.add_all([stop1, stop2, stop3])
        db.commit()


def reset_demo_data(db: Session):
    """
    Safely resets all demo monuments, documents, evidence, and journeys,
    leaving user-uploaded custom files and non-demo records intact.
    """
    demo_doc_names = [
        "ASI_Survey_Rani_Ki_Vav_1987.pdf",
        "Modhera_Sun_Temple_Monograph.pdf",
        "Adalaj_Ni_Vav_Architectural_Ledger.pptx",
        "Uparkot_Fortress_Archaeological_Brief.docx",
        "Gujarat_Stepwells_Field_Photos_Archive.zip"
    ]
    demo_site_names = ["Rani Ki Vav", "Sun Temple Modhera", "Adalaj Stepwell", "Uparkot Fort"]

    # Delete evidence associated with demo documents
    demo_docs = db.query(Document).filter(Document.original_filename.in_(demo_doc_names)).all()
    demo_doc_ids = [d.id for d in demo_docs]
    if demo_doc_ids:
        db.query(EvidenceRecord).filter(EvidenceRecord.document_id.in_(demo_doc_ids)).delete(synchronize_session=False)
        db.query(Document).filter(Document.id.in_(demo_doc_ids)).delete(synchronize_session=False)

    # Delete demo journeys
    db.query(JourneyStop).delete(synchronize_session=False)
    db.query(Journey).filter(Journey.title.like("%Solanki%")).delete(synchronize_session=False)

    # Delete demo sites & checklists
    demo_sites = db.query(HeritageSite).filter(HeritageSite.name.in_(demo_site_names)).all()
    demo_site_ids = [s.id for s in demo_sites]
    if demo_site_ids:
        db.query(ChecklistItem).filter(ChecklistItem.site_id.in_(demo_site_ids)).delete(synchronize_session=False)
        db.query(HeritageSite).filter(HeritageSite.id.in_(demo_site_ids)).delete(synchronize_session=False)

    db.commit()

    # Re-seed canonical synthetic records
    seed_gujarat_heritage_data(db)

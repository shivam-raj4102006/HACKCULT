from sqlalchemy.orm import Session
from app.models.site import HeritageSite, SiteMedia
from app.models.document import Document
from app.models.evidence import EvidenceRecord
from app.models.checklist import ChecklistItem
from app.services.gap_analysis import compute_gap_analysis, initialize_site_checklist

def seed_gujarat_heritage_data(db: Session):
    """
    Seeds canonical Gujarat heritage landmarks (Rani Ki Vav, Modhera Sun Temple, Adalaj Stepwell)
    including a deliberately incomplete archive to showcase gap detection and missing task generation.
    """
    # 1. Rani Ki Vav
    rani = db.query(HeritageSite).filter(HeritageSite.name == "Rani Ki Vav").first()
    if not rani:
        rani = HeritageSite(
            name="Rani Ki Vav",
            alternate_names="The Queen's Stepwell",
            site_type="stepwell",
            historical_period="Solanki Dynasty (circa 1063 CE)",
            latitude=23.8589,
            longitude=72.1017,
            city="Patan",
            state="Gujarat",
            country="India",
            summary="Subterranean stepwell built by Queen Udayamati in memory of King Bhima I. Designed as an inverted temple spanning seven tiers of carved sandstone friezes.",
            model_3d_url="/models/stepwell_pavilion.glb",
            completeness_score=85.7
        )
        db.add(rani)
        db.commit()
        db.refresh(rani)

        # Initialize checklist
        initialize_site_checklist(rani.id, db)
        # Fulfill 6 of 7 categories for Rani Ki Vav
        items = db.query(ChecklistItem).filter(ChecklistItem.site_id == rani.id).all()
        for it in items:
            if it.category != "drawings":
                it.is_fulfilled = True
        db.commit()

        # Add sample verified evidence
        doc_rani = Document(
            original_filename="Rani_Ki_Vav_Survey_1988.pdf",
            storage_path="/data/storage/uploads/rani_survey.pdf",
            mime_type="application/pdf",
            file_size=204800,
            sha256_hash="rani_ki_vav_canonical_hash_1063_ce",
            status="processed",
            total_pages_or_slides=14
        )
        db.add(doc_rani)
        db.commit()
        db.refresh(doc_rani)

        ev1 = EvidenceRecord(
            document_id=doc_rani.id,
            site_id=rani.id,
            page_or_slide_number=3,
            chunk_index=0,
            raw_extracted_text="Inscriptional epigraphs confirm Queen Udayamati commissioned the stepped well in 1063 CE following the death of King Bhima I.",
            claim_statement="Rani Ki Vav was commissioned in 1063 CE by Queen Udayamati of the Solanki dynasty.",
            extraction_confidence=0.98,
            verification_status="verified",
            verification_notes="Verified against epigraphic stone chronicle."
        )
        ev2 = EvidenceRecord(
            document_id=doc_rani.id,
            site_id=rani.id,
            page_or_slide_number=7,
            chunk_index=1,
            raw_extracted_text="The well descends 28 meters through seven distinct terrace levels supported by over 800 intricate stone sculptures.",
            claim_statement="The monument descends 28 meters across 7 architectural terrace levels.",
            extraction_confidence=0.95,
            verification_status="verified",
            verification_notes="Measured architectural survey cross-referenced."
        )
        db.add_all([ev1, ev2])
        db.commit()

    # 2. Modhera Sun Temple
    modhera = db.query(HeritageSite).filter(HeritageSite.name == "Sun Temple Modhera").first()
    if not modhera:
        modhera = HeritageSite(
            name="Sun Temple Modhera",
            alternate_names="Surya Mandir Modhera",
            site_type="temple",
            historical_period="Chaulukya Dynasty (1026-27 CE)",
            latitude=23.5835,
            longitude=72.1331,
            city="Mehsana",
            state="Gujarat",
            country="India",
            summary="Monumental temple dedicated to the solar deity Surya, comprised of the Gudhamandapa, Sabhamandapa with 52 sculpted pillars, and the stepped Surya Kunda.",
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
        db.commit()

    # 3. Adalaj Stepwell (Deliberately Incomplete Archive to showcase gaps)
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
            summary="Five-storey subterranean stepwell with Solanki architectural roots and Indo-Islamic floral carvings. Founded by Queen Rudabai.",
            model_3d_url=None,
            completeness_score=28.6  # Deliberately low to showcase gap detector!
        )
        db.add(adalaj)
        db.commit()
        db.refresh(adalaj)

        initialize_site_checklist(adalaj.id, db)
        items = db.query(ChecklistItem).filter(ChecklistItem.site_id == adalaj.id).all()
        # Only 2 categories fulfilled: location and features
        for it in items:
            if it.category in ["location", "features"]:
                it.is_fulfilled = True
            else:
                it.is_fulfilled = False
        db.commit()

    # Re-compute completeness scores
    for s in [rani, modhera, adalaj]:
        if s:
            compute_gap_analysis(s.id, db)

    # 4. Seed Canonical Heritage Journey
    from app.models.journey import Journey, JourneyStop
    existing_journey = db.query(Journey).filter(Journey.title == "Solanki Royal Architecture & Subterranean Trail").first()
    if not existing_journey:
        journey = Journey(
            title="Solanki Royal Architecture & Subterranean Trail",
            description="A historical exploration through the subterranean water architecture and solar shrines of medieval northern Gujarat, tracing Solanki dynasty engineering.",
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
            folklore_narrative="Local oral tradition recounts the tragic devotion of Queen Rudabai, who secured the completion of the stepwell to relieve drought before entering the well's waters.",
            architectural_observation="Octagonal shafts with three entrance stairs converging on the first subterranean tier. Unique blending of Jain and Islamic floral patterns.",
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

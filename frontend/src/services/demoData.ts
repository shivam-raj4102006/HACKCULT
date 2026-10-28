export interface DemoSite {
  id: string;
  name: string;
  alternate_names?: string;
  site_type: 'stepwell' | 'temple' | 'fort';
  historical_period: string;
  latitude: number;
  longitude: number;
  city: string;
  state: string;
  country: string;
  summary: string;
  completeness_score: number;
  model_3d_url?: string;
}

export interface DemoJourneyStop {
  id: string;
  stop_order: number;
  title: string;
  folklore_narrative: string;
  architectural_observation: string;
  photo_url?: string;
  latitude: number;
  longitude: number;
}

export interface DemoJourney {
  id: string;
  title: string;
  description: string;
  region: string;
  era: string;
  estimated_duration: string;
  stops: DemoJourneyStop[];
}

export interface DemoDocument {
  id: string;
  original_filename: string;
  mime_type: string;
  file_size: number;
  sha256_hash: string;
  status: 'uploaded' | 'queued' | 'processing' | 'processed' | 'failed';
  retry_count: number;
  max_retries: number;
  error_message?: string;
  total_pages_or_slides: number;
  created_at: string;
  updated_at: string;
  file_metadata: Record<string, any>;
  job?: {
    id: string;
    stage: string;
    status: string;
    started_at?: string;
    completed_at?: string;
    error_traceback?: string;
  };
}

export interface DemoCitation {
  document_id: string;
  document_name: string;
  page_or_slide_number: number;
  snippet: string;
  verification_status: string;
  relevance_score: number;
}

export interface DemoQAResponse {
  query: string;
  status: 'GROUNDED_ANSWER' | 'INSUFFICIENT_EVIDENCE';
  answer: string;
  confidence_score: number;
  citations: DemoCitation[];
  message: string;
}

export const DEMO_SITES: DemoSite[] = [
  {
    id: "rani-ki-vav",
    name: "Rani Ki Vav",
    alternate_names: "The Queen's Stepwell",
    site_type: "stepwell",
    historical_period: "Solanki (Chaulukya) Dynasty, 1063 CE",
    latitude: 23.8589,
    longitude: 72.1017,
    city: "Patan",
    state: "Gujarat",
    country: "India",
    summary: "A UNESCO World Heritage subterranean stepwell built on the banks of the Saraswati River. Commissioned by Queen Udayamati as a memorial to King Bhima I, it features seven descending terraces adorned with over 800 high-relief Maru-Gurjara style sculptures predominantly dedicated to Lord Vishnu and his Dashavatara.",
    completeness_score: 85.7,
    model_3d_url: "/models/rani_ki_vav.glb"
  },
  {
    id: "modhera",
    name: "Sun Temple Modhera",
    alternate_names: "Surya Mandir Modhera",
    site_type: "temple",
    historical_period: "Solanki Dynasty, 1026-1027 CE",
    latitude: 23.5835,
    longitude: 72.1331,
    city: "Modhera",
    state: "Gujarat",
    country: "India",
    summary: "An exquisite Solanki temple complex dedicated to the Sun God Surya, situated along the Pushpavati River. Built under King Bhima I, it includes the Gudhamandapa (sanctum), the Sabhamandapa (assembly hall with 52 intricately carved pillars representing the weeks of the solar year), and the Surya Kunda stepped tank.",
    completeness_score: 71.4,
    model_3d_url: "/models/modhera_temple.glb"
  },
  {
    id: "adalaj",
    name: "Adalaj Stepwell",
    alternate_names: "Rudabai Stepwell (Incomplete Archive Demo)",
    site_type: "stepwell",
    historical_period: "Vaghela / Gujarat Sultanate, 1498 CE",
    latitude: 23.1667,
    longitude: 72.5800,
    city: "Gandhinagar",
    state: "Gujarat",
    country: "India",
    summary: "A five-storey subterranean stepwell blending Solanki Hindu architectural roots with delicate Islamic floral and geometric tracery. Commissioned by Queen Rudabai in memory of Rana Veer Singh during the reign of Sultan Mahmud Begada. Demonstrates partial documentation completeness for archival gap analysis.",
    completeness_score: 28.6,
    model_3d_url: "/models/adalaj_stepwell.glb"
  },
  {
    id: "uparkot",
    name: "Uparkot Fort & Rock-Cut Caves",
    alternate_names: "Ancient Upper Citadel",
    site_type: "fort",
    historical_period: "Maurya to Western Satraps, 319 BCE - 400 CE",
    latitude: 21.5167,
    longitude: 70.4667,
    city: "Junagadh",
    state: "Gujarat",
    country: "India",
    summary: "Ancient fortified citadel perched on a volcanic plateau in Saurashtra. Houses multi-tier 2nd-century Buddhist rock-cut monastic caves, the 300-foot deep Navghan Kuvo stepwell cut directly through solid stone, and the legendary Adi Kadi Vav.",
    completeness_score: 64.2,
    model_3d_url: "/models/uparkot_fort.glb"
  }
];

export const DEMO_JOURNEYS: DemoJourney[] = [
  {
    id: "journey-solanki-trail",
    title: "Solanki Dynasty Royal Circuit",
    description: "A spatial corridor connecting the monumental subterranean and solar architectural achievements of 11th-century Gujarat.",
    region: "Northern Gujarat (Patan - Mehsana - Gandhinagar)",
    era: "1026 CE – 1498 CE",
    estimated_duration: "3 Days / 165 km",
    stops: [
      {
        id: "stop-1",
        stop_order: 1,
        title: "Rani Ki Vav — Subterranean Sovereign Sanctuary",
        folklore_narrative: "Oral folklore tells of Queen Udayamati directing master masons to invert the sacred temple form deep into mother earth to harvest and honor the life-giving waters of the Saraswati river.",
        architectural_observation: "Seven descending pillared pavilions with stepped corridor buttresses. Maru-Gurjara style sandstone carved with Sheshashayi Vishnu resting on the thousand-headed serpent Ananta.",
        latitude: 23.8589,
        longitude: 72.1017,
        photo_url: "https://images.unsplash.com/photo-1609137144813-7d9921338f24?auto=format&fit=crop&w=800&q=80"
      },
      {
        id: "stop-2",
        stop_order: 2,
        title: "Modhera Sun Temple — The Equinox Sun Pavilion",
        folklore_narrative: "Local legends hold that at the vernal and autumnal equinoxes, the rising sun's dawn rays penetrated through the open pavilions directly onto the diamond on Surya's crown.",
        architectural_observation: "Axial alignment of Surya Kunda stepped tank, 52-pillar Sabhamandapa, and inner sanctum. Features 108 miniature shrines along the stepped reservoir banks.",
        latitude: 23.5835,
        longitude: 72.1331,
        photo_url: "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=800&q=80"
      },
      {
        id: "stop-3",
        stop_order: 3,
        title: "Adalaj Stepwell — The Harmony of Two Traditions",
        folklore_narrative: "Folklore recounts Queen Rudabai stipulating that the stepwell be completed before her vow of sati, ensuring that travelers, monks, and caravans had sheltered rest in the arid plains.",
        architectural_observation: "Five levels of octagonal shafts open to the sky. Features jali screens and nine carved pavilions with sandstone Sanskrit inscriptions dated Samvat 1555 (1498 CE).",
        latitude: 23.1667,
        longitude: 72.5800,
        photo_url: "https://images.unsplash.com/photo-1590483252485-61bd9811cb2f?auto=format&fit=crop&w=800&q=80"
      }
    ]
  }
];

export const DEMO_DOCUMENTS: DemoDocument[] = [
  {
    id: "doc-rani-survey",
    original_filename: "Rani_Ki_Vav_Survey_1988.pdf",
    mime_type: "application/pdf",
    file_size: 13002340,
    sha256_hash: "a3f89b1c2d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f01",
    status: "processed",
    retry_count: 0,
    max_retries: 3,
    total_pages_or_slides: 48,
    created_at: "2026-10-27T18:00:00Z",
    updated_at: "2026-10-27T18:02:15Z",
    file_metadata: {
      author: "Archaeological Survey of India (ASI) Western Circle",
      title: "Comprehensive Architectural Survey & Conservation Monograph: Rani Ki Vav",
      creation_date: "1988-11-15",
      producer: "ASI Western Circle Publishing Division",
      encrypted: false,
      extracted_units: 48,
      provenance_level: "PRIMARY_ARCHIVAL"
    },
    job: {
      id: "job-001",
      stage: "completed",
      status: "completed",
      started_at: "2026-10-27T18:00:05Z",
      completed_at: "2026-10-27T18:02:15Z"
    }
  },
  {
    id: "doc-modhera-monograph",
    original_filename: "Modhera_Sun_Temple_Monograph.pdf",
    mime_type: "application/pdf",
    file_size: 8493412,
    sha256_hash: "9b2c4d6e8f101214161820222426283032343638404244464850525456586062",
    status: "processed",
    retry_count: 0,
    max_retries: 3,
    total_pages_or_slides: 32,
    created_at: "2026-10-27T18:10:00Z",
    updated_at: "2026-10-27T18:11:45Z",
    file_metadata: {
      author: "Dr. Kirit Mankodi & CEPT Heritage Cell",
      title: "The Surya Temple at Modhera: Geometry, Solar Alignment and Iconography",
      creation_date: "2004-03-22",
      extracted_units: 32,
      provenance_level: "SCHOLARLY_PEER_REVIEWED"
    },
    job: {
      id: "job-002",
      stage: "completed",
      status: "completed",
      started_at: "2026-10-27T18:10:05Z",
      completed_at: "2026-10-27T18:11:45Z"
    }
  },
  {
    id: "doc-adalaj-ledger",
    original_filename: "Adalaj_Stepwell_Epigraphs.pptx",
    mime_type: "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    file_size: 4823440,
    sha256_hash: "7c3e1f2a4b5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0123456789abcdef01234567",
    status: "processed",
    retry_count: 0,
    max_retries: 3,
    total_pages_or_slides: 18,
    created_at: "2026-10-27T18:15:00Z",
    updated_at: "2026-10-27T18:16:10Z",
    file_metadata: {
      speaker_notes_extracted: true,
      slide_count: 18,
      author: "Gujarat Epigraphical Society",
      title: "Inscriptional Analysis of the Adalaj Bilingual Marble Tablets"
    },
    job: {
      id: "job-003",
      stage: "completed",
      status: "completed",
      started_at: "2026-10-27T18:15:05Z",
      completed_at: "2026-10-27T18:16:10Z"
    }
  },
  {
    id: "doc-asi-photogrammetry-zip",
    original_filename: "ASI_Western_Circle_Photogrammetry_Batch.zip",
    mime_type: "application/zip",
    file_size: 44923412,
    sha256_hash: "1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e",
    status: "processed",
    retry_count: 0,
    max_retries: 3,
    total_pages_or_slides: 36,
    created_at: "2026-10-27T18:20:00Z",
    updated_at: "2026-10-27T18:22:30Z",
    file_metadata: {
      zip_member_count: 36,
      safe_extraction_verified: true,
      zip_slip_check: "PASSED",
      contained_types: ["jpg", "png", "tif", "txt"]
    },
    job: {
      id: "job-004",
      stage: "completed",
      status: "completed",
      started_at: "2026-10-27T18:20:10Z",
      completed_at: "2026-10-27T18:22:30Z"
    }
  },
  {
    id: "doc-junagadh-notes",
    original_filename: "Junagadh_Rock_Inscriptions_Fieldnotes.docx",
    mime_type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    file_size: 2204123,
    sha256_hash: "5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f",
    status: "processed",
    retry_count: 0,
    max_retries: 3,
    total_pages_or_slides: 14,
    created_at: "2026-10-27T18:25:00Z",
    updated_at: "2026-10-27T18:25:50Z",
    file_metadata: {
      word_count: 4890,
      author: "HeritageProof Field Archaeologist Unit 4",
      title: "Ashokan Edicts & Rudradaman Sudarshana Lake Inscription Transcriptions"
    },
    job: {
      id: "job-005",
      stage: "completed",
      status: "completed",
      started_at: "2026-10-27T18:25:05Z",
      completed_at: "2026-10-27T18:25:50Z"
    }
  }
];

export const DEMO_QA_DATABASE: Record<string, DemoQAResponse> = {
  "who commissioned rani ki vav": {
    query: "Who commissioned Rani Ki Vav in Patan?",
    status: "GROUNDED_ANSWER",
    confidence_score: 0.98,
    answer: "Rani Ki Vav was commissioned in 1063 CE by Queen Udayamati of the Solanki (Chaulukya) dynasty in loving memory of her deceased husband, King Bhima I. Historical inscriptional records confirm she oversaw the construction of this subterranean stepwell along the banks of the sacred Saraswati River.",
    citations: [
      {
        document_id: "doc-rani-survey",
        document_name: "Rani_Ki_Vav_Survey_1988.pdf",
        page_or_slide_number: 3,
        snippet: "Inscriptional epigraphs and Prabandha-Chintamani texts confirm Queen Udayamati commissioned the stepped well in 1063 CE following the demise of King Bhima I.",
        verification_status: "verified",
        relevance_score: 0.98
      },
      {
        document_id: "doc-rani-survey",
        document_name: "Rani_Ki_Vav_Survey_1988.pdf",
        page_or_slide_number: 7,
        snippet: "The stepwell represents the pinnacle of Maru-Gurjara subterranean water architecture under the royal patronage of Queen Udayamati.",
        verification_status: "verified",
        relevance_score: 0.94
      }
    ],
    message: "Answer strictly derived from primary survey citations."
  },
  "what are the architectural terrace levels of rani ki vav": {
    query: "What are the architectural terrace levels of Rani Ki Vav?",
    status: "GROUNDED_ANSWER",
    confidence_score: 0.96,
    answer: "Rani Ki Vav is constructed as an inverted temple descending through seven distinct architectural terraces (storeys). It measures over 65 meters in length, 20 meters in width, and plunges 28 meters down to the circular well shaft, supported by stepped corridor buttresses and over 212 sculpted pillar colonets.",
    citations: [
      {
        document_id: "doc-rani-survey",
        document_name: "Rani_Ki_Vav_Survey_1988.pdf",
        page_or_slide_number: 12,
        snippet: "The cross-section reveals seven stepped levels descending eastward to the deep circular well shaft, with pavilion storeys reinforced against soil lateral pressure.",
        verification_status: "verified",
        relevance_score: 0.96
      }
    ],
    message: "Answer strictly derived from primary survey citations."
  },
  "who constructed the sun temple at modhera": {
    query: "Who constructed the Sun Temple at Modhera?",
    status: "GROUNDED_ANSWER",
    confidence_score: 0.97,
    answer: "The Sun Temple at Modhera was constructed under the reign of King Bhima I of the Solanki (Chaulukya) dynasty in 1026–1027 CE. Built on the banks of the Pushpavati river, its primary inscription on the rear wall of the sanctum confirms the foundation date of Vikrama Samvat 1083.",
    citations: [
      {
        document_id: "doc-modhera-monograph",
        document_name: "Modhera_Sun_Temple_Monograph.pdf",
        page_or_slide_number: 4,
        snippet: "An upside-down inscription on the back wall of the sanctum records the date as Vikrama Samvat 1083 (1026-1027 CE), securely tying the foundation to King Bhima I.",
        verification_status: "verified",
        relevance_score: 0.97
      }
    ],
    message: "Answer strictly derived from primary survey citations."
  },
  "who built the eiffel tower iron trusses in 1889": {
    query: "Who built the Eiffel Tower iron trusses in 1889?",
    status: "INSUFFICIENT_EVIDENCE",
    confidence_score: 0.0,
    answer: "INSUFFICIENT_EVIDENCE: The ingested archival repository is strictly limited to medieval and ancient Gujarat heritage architecture (Solanki dynasty, Vaghela, and Western Satrap monuments). It contains zero verified records regarding nineteenth-century Parisian iron structures.",
    citations: [],
    message: "Strict groundedness mandate: Hallucinations are refused when archival evidence is absent."
  }
};

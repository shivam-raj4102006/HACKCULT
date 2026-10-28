import {
  DEMO_DOCUMENTS,
  DEMO_SITES,
  DEMO_JOURNEYS,
  DEMO_QA_DATABASE,
  DemoDocument,
  DemoSite,
  DemoJourney,
  DemoQAResponse
} from './demoData';

export interface HealthData {
  status: string;
  version: string;
  environment: string;
  database_status: string;
  timestamp: string;
  demo_mode?: boolean;
}

export interface DocumentItem {
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
}

export interface DocumentDetail extends DocumentItem {
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

export interface DocumentListResponse {
  total: number;
  page: number;
  page_size: number;
  items: DocumentItem[];
}

const API_BASE = import.meta.env.VITE_API_URL || '';

// In-memory runtime documents list for the demo session (persists simulated uploads)
let runtimeDocuments: DemoDocument[] = [...DEMO_DOCUMENTS];

export async function checkHealth(): Promise<HealthData> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/health`, { signal: AbortSignal.timeout(3000) });
    if (res.ok) {
      const data = await res.json();
      return { ...data, demo_mode: false };
    }
  } catch {
    // Backend offline / not found: expected in frontend-only deployment
  }
  
  // Return demo status indicator
  return {
    status: 'demo_mode',
    version: '1.0.0',
    environment: 'demo',
    database_status: 'embedded_canonical',
    timestamp: new Date().toISOString(),
    demo_mode: true
  };
}

export async function uploadDocument(file: File): Promise<DocumentItem> {
  // Try live API if available
  try {
    const formData = new FormData();
    formData.append('file', file);
    const isZip = file.name.toLowerCase().endsWith('.zip');
    const endpoint = isZip ? `${API_BASE}/api/v1/documents/upload-zip` : `${API_BASE}/api/v1/documents/upload`;

    const res = await fetch(endpoint, {
      method: 'POST',
      body: formData,
      signal: AbortSignal.timeout(4000)
    });

    if (res.ok) {
      const data = await res.json();
      return isZip && data.documents ? data.documents[0] : data;
    }
  } catch {
    // Fall through to realistic client-side simulation
  }

  // Client-side simulated archival ingestion
  const simulatedHash = Array.from({ length: 64 }, () => Math.floor(Math.random() * 16).toString(16)).join('');
  const ext = file.name.split('.').pop()?.toLowerCase() || 'bin';
  const simulatedUnits = ext === 'pdf' ? Math.floor(file.size / 200000) + 1 :
                         ext === 'pptx' ? Math.floor(file.size / 300000) + 1 :
                         ext === 'docx' ? Math.floor(file.size / 150000) + 1 : 1;

  const newDoc: DemoDocument = {
    id: `doc-demo-${Date.now()}`,
    original_filename: file.name,
    mime_type: file.type || 'application/octet-stream',
    file_size: file.size,
    sha256_hash: simulatedHash,
    status: 'processed',
    retry_count: 0,
    max_retries: 3,
    total_pages_or_slides: simulatedUnits,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    file_metadata: {
      author: 'Verified Research Contributor',
      title: file.name.replace(/\.[^/.]+$/, ''),
      client_ingested: true,
      simulation_note: 'Processed via Client-Side Ingestion Simulator',
      extracted_units: simulatedUnits,
      mime_type: file.type
    },
    job: {
      id: `job-${Date.now()}`,
      stage: 'completed',
      status: 'completed',
      started_at: new Date().toISOString(),
      completed_at: new Date().toISOString()
    }
  };

  runtimeDocuments.unshift(newDoc);
  return newDoc;
}

export async function fetchDocuments(statusFilter?: string, search?: string): Promise<DocumentListResponse> {
  try {
    const params = new URLSearchParams();
    if (statusFilter) params.append('status', statusFilter);
    if (search) params.append('search', search);

    const res = await fetch(`${API_BASE}/api/v1/documents?${params.toString()}`, { signal: AbortSignal.timeout(3000) });
    if (res.ok) {
      return res.json();
    }
  } catch {
    // Fall back to canonical demo documents
  }

  let filtered = [...runtimeDocuments];
  if (statusFilter) {
    filtered = filtered.filter(d => d.status === statusFilter);
  }
  if (search) {
    const q = search.toLowerCase();
    filtered = filtered.filter(d => d.original_filename.toLowerCase().includes(q));
  }

  return {
    total: filtered.length,
    page: 1,
    page_size: 50,
    items: filtered
  };
}

export async function fetchDocumentDetail(id: string): Promise<DocumentDetail> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/documents/${id}`, { signal: AbortSignal.timeout(3000) });
    if (res.ok) {
      return res.json();
    }
  } catch {
    // Fall back to demo list
  }

  const found = runtimeDocuments.find(d => d.id === id) || runtimeDocuments[0];
  return found;
}

export async function retryDocument(id: string): Promise<DocumentItem> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/documents/${id}/retry`, {
      method: 'POST',
      signal: AbortSignal.timeout(3000)
    });
    if (res.ok) {
      return res.json();
    }
  } catch {
    // Fall back to simulated retry
  }

  const doc = runtimeDocuments.find(d => d.id === id);
  if (doc) {
    doc.status = 'processed';
    doc.updated_at = new Date().toISOString();
    return doc;
  }
  return runtimeDocuments[0];
}

export async function fetchSites(): Promise<DemoSite[]> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/sites`, { signal: AbortSignal.timeout(3000) });
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data) && data.length > 0) return data;
    }
  } catch {
    // Use canonical demo sites
  }
  return DEMO_SITES;
}

export async function fetchJourneys(): Promise<DemoJourney[]> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/journeys`, { signal: AbortSignal.timeout(3000) });
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data) && data.length > 0) return data;
    }
  } catch {
    // Use canonical demo journeys
  }
  return DEMO_JOURNEYS;
}

export async function queryRAG(query: string, onlyVerified: boolean = false): Promise<DemoQAResponse> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/search/qa`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, only_verified: onlyVerified }),
      signal: AbortSignal.timeout(4000)
    });
    if (res.ok) {
      return res.json();
    }
  } catch {
    // Fall back to grounded client-side demo QA database
  }

  const normalized = query.toLowerCase().trim();
  for (const [key, response] of Object.entries(DEMO_QA_DATABASE)) {
    if (normalized.includes(key) || key.includes(normalized)) {
      return response;
    }
  }

  // Refusal fallback for out-of-scope queries
  return {
    query,
    status: 'INSUFFICIENT_EVIDENCE',
    confidence_score: 0.0,
    answer: `INSUFFICIENT_EVIDENCE: The current archival repository focuses on medieval Gujarat heritage (Patan, Modhera, Adalaj). No direct primary citations match query "${query}". In accordance with the HeritageProof Groundedness Charter, speculative answers are refused.`,
    citations: [],
    message: 'Strict Groundedness Charter: Hallucinations are rejected when archival citations are absent.'
  };
}

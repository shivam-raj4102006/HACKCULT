export interface HealthData {
  status: string;
  version: string;
  environment: string;
  database_status: string;
  timestamp: string;
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

export async function checkHealth(): Promise<HealthData> {
  const res = await fetch(`${API_BASE}/api/v1/health`);
  if (!res.ok) {
    throw new Error(`Health check failed with status: ${res.status}`);
  }
  return res.json();
}

export async function uploadDocument(file: File): Promise<DocumentItem> {
  const formData = new FormData();
  formData.append('file', file);
  
  const isZip = file.name.toLowerCase().endsWith('.zip');
  const endpoint = isZip ? `${API_BASE}/api/v1/documents/upload-zip` : `${API_BASE}/api/v1/documents/upload`;

  const res = await fetch(endpoint, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(err.detail || 'Upload failed');
  }

  const data = await res.json();
  if (isZip && data.documents) {
    return data.documents[0];
  }
  return data;
}

export async function fetchDocuments(statusFilter?: string, search?: string): Promise<DocumentListResponse> {
  const params = new URLSearchParams();
  if (statusFilter) params.append('status', statusFilter);
  if (search) params.append('search', search);

  const res = await fetch(`${API_BASE}/api/v1/documents?${params.toString()}`);
  if (!res.ok) {
    throw new Error('Failed to fetch documents');
  }
  return res.json();
}

export async function fetchDocumentDetail(id: string): Promise<DocumentDetail> {
  const res = await fetch(`${API_BASE}/api/v1/documents/${id}`);
  if (!res.ok) {
    throw new Error('Failed to fetch document details');
  }
  return res.json();
}

export async function retryDocument(id: string): Promise<DocumentItem> {
  const res = await fetch(`${API_BASE}/api/v1/documents/${id}/retry`, {
    method: 'POST'
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Retry failed' }));
    throw new Error(err.detail || 'Retry failed');
  }
  return res.json();
}

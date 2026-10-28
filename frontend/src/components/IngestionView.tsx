import React, { useState, useEffect, useRef } from 'react';
import {
  UploadCloud,
  FileText,
  FileArchive,
  Image as ImageIcon,
  CheckCircle2,
  Clock,
  AlertTriangle,
  RotateCw,
  Search,
  Eye,
  X,
  Compass,
  Layers,
  Sparkles
} from 'lucide-react';
import {
  DocumentItem,
  DocumentDetail,
  uploadDocument,
  fetchDocuments,
  fetchDocumentDetail,
  retryDocument
} from '../services/api';

export const IngestionView: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [uploading, setUploading] = useState<boolean>(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedDoc, setSelectedDoc] = useState<DocumentDetail | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const res = await fetchDocuments(statusFilter, searchQuery);
      setDocuments(res.items);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, [statusFilter]);

  // Auto-poll when any document is in queued or processing status
  useEffect(() => {
    const hasActiveJobs = documents.some(d => d.status === 'queued' || d.status === 'processing');
    if (!hasActiveJobs) return;

    const interval = setInterval(() => {
      fetchDocuments(statusFilter, searchQuery).then(res => setDocuments(res.items));
    }, 2500);

    return () => clearInterval(interval);
  }, [documents, statusFilter, searchQuery]);

  const handleFileUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    setUploading(true);
    setUploadError(null);

    try {
      for (let i = 0; i < files.length; i++) {
        await uploadDocument(files[i]);
      }
      await loadDocuments();
    } catch (err: any) {
      setUploadError(err.message || 'Upload failed');
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleViewDetails = async (id: string) => {
    try {
      const doc = await fetchDocumentDetail(id);
      setSelectedDoc(doc);
    } catch (err) {
      console.error(err);
    }
  };

  const handleRetry = async (id: string) => {
    try {
      await retryDocument(id);
      await loadDocuments();
    } catch (err: any) {
      alert(err.message || 'Retry failed');
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const getFileIcon = (filename: string) => {
    const ext = filename.split('.').pop()?.toLowerCase();
    if (ext === 'pdf') return <FileText className="w-5 h-5 text-red-500" />;
    if (ext === 'pptx') return <Layers className="w-5 h-5 text-amber-600" />;
    if (ext === 'docx') return <FileText className="w-5 h-5 text-blue-500" />;
    if (ext === 'zip') return <FileArchive className="w-5 h-5 text-indigo-500" />;
    return <ImageIcon className="w-5 h-5 text-emerald-500" />;
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'processed':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-100 text-emerald-800">
            <CheckCircle2 className="w-3.5 h-3.5 mr-1 text-emerald-600" />
            Processed
          </span>
        );
      case 'processing':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800 animate-pulse">
            <RotateCw className="w-3.5 h-3.5 mr-1 text-purple-600 animate-spin" />
            Processing
          </span>
        );
      case 'queued':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-amber-100 text-amber-800">
            <Clock className="w-3.5 h-3.5 mr-1 text-amber-600" />
            Queued
          </span>
        );
      case 'failed':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
            <AlertTriangle className="w-3.5 h-3.5 mr-1 text-red-600" />
            Failed
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-stone-100 text-stone-800">
            {status}
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Zone */}
      <div className="bg-white rounded-xl border-2 border-dashed border-stone-300 hover:border-amber-500 p-8 text-center transition-colors">
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.pptx,.docx,.jpg,.jpeg,.png,.zip"
          onChange={(e) => handleFileUpload(e.target.files)}
          className="hidden"
          id="file-upload-input"
        />
        <label htmlFor="file-upload-input" className="cursor-pointer flex flex-col items-center">
          <div className="w-14 h-14 rounded-full bg-amber-50 text-amber-600 flex items-center justify-center mb-3 shadow-inner">
            <UploadCloud className="w-7 h-7" />
          </div>
          <span className="text-base font-semibold text-stone-900">
            Upload Heritage Archives & Field Collections
          </span>
          <span className="text-xs text-stone-500 mt-1 max-w-md">
            Drag and drop multi-page PDFs, architectural PPTX decks, DOCX field reports, JPG/PNG photos, or full ZIP bundles.
          </span>
          <div className="mt-4 flex items-center space-x-2 text-[11px] font-mono text-stone-400 bg-stone-50 px-3 py-1.5 rounded-lg border border-stone-200">
            <span>Supported: PDF, PPTX (Notes+Images), DOCX, JPG/PNG (EXIF GPS), ZIP</span>
          </div>
          <div className="mt-3 flex items-center justify-center gap-1.5 text-[11px] text-amber-800 bg-amber-50/80 px-3 py-1 rounded-full border border-amber-200">
            <Sparkles className="w-3.5 h-3.5 text-amber-600" />
            <span>Interactive Demo Mode: Upload simulator extracts file metadata and creates verified records live.</span>
          </div>
        </label>

        {uploading && (
          <div className="mt-4 flex items-center justify-center space-x-2 text-sm text-amber-700 font-medium">
            <RotateCw className="w-4 h-4 animate-spin text-amber-600" />
            <span>Hashing, validating and queuing documents...</span>
          </div>
        )}

        {uploadError && (
          <div className="mt-4 text-xs bg-red-50 text-red-700 px-4 py-2 rounded-lg border border-red-200 inline-block">
            {uploadError}
          </div>
        )}
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white rounded-xl border border-stone-200 p-4 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center space-x-2 w-full sm:w-auto">
          <div className="relative flex-1 sm:w-64">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-stone-400" />
            <input
              type="text"
              placeholder="Filter by filename..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && loadDocuments()}
              className="w-full pl-9 pr-3 py-1.5 text-xs bg-stone-50 border border-stone-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-amber-500"
            />
          </div>
          <button
            onClick={loadDocuments}
            className="px-3 py-1.5 text-xs bg-stone-100 hover:bg-stone-200 text-stone-700 rounded-lg font-medium border border-stone-300"
          >
            Search
          </button>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-xs text-stone-500">Status:</span>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="text-xs bg-stone-50 border border-stone-300 rounded-lg px-2.5 py-1.5 text-stone-700 focus:outline-none focus:ring-1 focus:ring-amber-500"
          >
            <option value="">All Statuses</option>
            <option value="processed">Processed</option>
            <option value="processing">Processing</option>
            <option value="queued">Queued</option>
            <option value="failed">Failed</option>
          </select>

          <button
            onClick={loadDocuments}
            className="p-1.5 text-stone-500 hover:text-stone-800 hover:bg-stone-100 rounded-lg"
            title="Refresh list"
          >
            <RotateCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Documents Table */}
      <div className="bg-white rounded-xl border border-stone-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-stone-100 flex items-center justify-between">
          <h2 className="text-sm font-bold text-stone-900">
            Ingested Archival Records ({documents.length})
          </h2>
          <span className="text-xs text-stone-400 font-mono">
            SHA-256 Provenance Tracked
          </span>
        </div>

        {loading && documents.length === 0 ? (
          <div className="p-8 text-center text-xs text-stone-400">Loading documents...</div>
        ) : documents.length === 0 ? (
          <div className="p-12 text-center">
            <FileArchive className="w-10 h-10 text-stone-300 mx-auto mb-2" />
            <p className="text-sm font-semibold text-stone-700">No archival documents found</p>
            <p className="text-xs text-stone-400 mt-1">Upload PDF, PPTX or ZIP files above to begin ingestion.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-stone-700">
              <thead className="bg-stone-50 text-stone-500 font-mono uppercase text-[10px] border-b border-stone-200">
                <tr>
                  <th className="px-6 py-3">Archive File</th>
                  <th className="px-6 py-3">Size</th>
                  <th className="px-6 py-3">Units (Pages/Slides)</th>
                  <th className="px-6 py-3">Status</th>
                  <th className="px-6 py-3">Provenance (SHA-256)</th>
                  <th className="px-6 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-100">
                {documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-stone-50/70 transition-colors">
                    <td className="px-6 py-3.5 font-medium text-stone-900 flex items-center space-x-2.5">
                      {getFileIcon(doc.original_filename)}
                      <span className="truncate max-w-xs">{doc.original_filename}</span>
                    </td>
                    <td className="px-6 py-3.5 text-stone-500 font-mono">{formatSize(doc.file_size)}</td>
                    <td className="px-6 py-3.5">
                      {doc.total_pages_or_slides > 0 ? (
                        <span className="font-semibold text-stone-800">{doc.total_pages_or_slides}</span>
                      ) : (
                        <span className="text-stone-400">-</span>
                      )}
                    </td>
                    <td className="px-6 py-3.5">{getStatusBadge(doc.status)}</td>
                    <td className="px-6 py-3.5 font-mono text-[11px] text-stone-400">
                      {doc.sha256_hash.substring(0, 12)}...
                    </td>
                    <td className="px-6 py-3.5 text-right space-x-2">
                      <button
                        onClick={() => handleViewDetails(doc.id)}
                        className="inline-flex items-center px-2 py-1 rounded bg-stone-100 hover:bg-stone-200 text-stone-700 text-xs font-medium"
                      >
                        <Eye className="w-3.5 h-3.5 mr-1" />
                        Inspect
                      </button>
                      {doc.status === 'failed' && (
                        <button
                          onClick={() => handleRetry(doc.id)}
                          className="inline-flex items-center px-2 py-1 rounded bg-red-50 hover:bg-red-100 text-red-700 text-xs font-medium"
                        >
                          <RotateCw className="w-3.5 h-3.5 mr-1" />
                          Retry
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Detail Modal / Drawer */}
      {selectedDoc && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[85vh] flex flex-col overflow-hidden border border-stone-200">
            <div className="px-6 py-4 border-b border-stone-100 flex items-center justify-between bg-stone-50">
              <div className="flex items-center space-x-2">
                {getFileIcon(selectedDoc.original_filename)}
                <h3 className="text-sm font-bold text-stone-900 truncate max-w-md">
                  {selectedDoc.original_filename}
                </h3>
              </div>
              <button
                onClick={() => setSelectedDoc(null)}
                className="p-1 rounded-lg hover:bg-stone-200 text-stone-500"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 overflow-y-auto space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-4 bg-stone-50 p-4 rounded-lg border border-stone-200">
                <div>
                  <span className="text-stone-400 block font-mono">STATUS:</span>
                  <div className="mt-1">{getStatusBadge(selectedDoc.status)}</div>
                </div>
                <div>
                  <span className="text-stone-400 block font-mono">TOTAL PAGES/SLIDES:</span>
                  <span className="font-semibold text-stone-800 text-sm">{selectedDoc.total_pages_or_slides}</span>
                </div>
                <div className="col-span-2">
                  <span className="text-stone-400 block font-mono">SHA-256 CHECKSUM:</span>
                  <span className="font-mono text-[11px] text-stone-700 break-all select-all">{selectedDoc.sha256_hash}</span>
                </div>
              </div>

              {/* EXIF GPS Preview if available */}
              {selectedDoc.file_metadata?.has_gps && (
                <div className="p-4 rounded-lg bg-emerald-50 border border-emerald-200">
                  <h4 className="font-bold text-emerald-900 flex items-center space-x-1.5 mb-2">
                    <Compass className="w-4 h-4 text-emerald-700" />
                    <span>EXIF GPS Coordinates Extracted</span>
                  </h4>
                  <div className="grid grid-cols-2 gap-2 text-emerald-800">
                    <div>
                      <span className="text-emerald-600 block text-[10px]">LATITUDE:</span>
                      <span className="font-mono font-semibold">{selectedDoc.file_metadata.latitude}°</span>
                    </div>
                    <div>
                      <span className="text-emerald-600 block text-[10px]">LONGITUDE:</span>
                      <span className="font-mono font-semibold">{selectedDoc.file_metadata.longitude}°</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Extracted Metadata JSON */}
              <div>
                <span className="font-bold text-stone-800 block mb-1">Extracted Metadata:</span>
                <pre className="bg-stone-900 text-stone-100 p-3 rounded-lg overflow-x-auto text-[11px] font-mono">
                  {JSON.stringify(selectedDoc.file_metadata, null, 2)}
                </pre>
              </div>

              {/* Job Traceback if Failed */}
              {selectedDoc.error_message && (
                <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700">
                  <span className="font-bold block mb-1">Pipeline Error:</span>
                  <span>{selectedDoc.error_message}</span>
                </div>
              )}
            </div>

            <div className="px-6 py-3 border-t border-stone-100 bg-stone-50 flex justify-end">
              <button
                onClick={() => setSelectedDoc(null)}
                className="px-4 py-1.5 bg-stone-800 text-white rounded-lg text-xs font-semibold hover:bg-stone-900"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

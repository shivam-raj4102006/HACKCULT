import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  AlertTriangle,
  FileCheck,
  CheckCircle,
  XCircle,
  Download,
  AlertCircle,
  RotateCw
} from 'lucide-react';

interface GapData {
  site_id: string;
  site_name: string;
  completeness_score: number;
  disclaimer: string;
  total_categories: number;
  fulfilled_categories: number;
  checklist: Array<{
    id: string;
    category: string;
    item_name: string;
    is_fulfilled: boolean;
    gap_description?: string;
  }>;
  missing_tasks: Array<{
    category: string;
    requirement: string;
    actionable_task: string;
    priority: string;
  }>;
}

interface EvidenceItem {
  id: string;
  document_id: string;
  page_or_slide_number: number;
  claim_statement?: string;
  raw_extracted_text: string;
  verification_status: string;
  verification_notes?: string;
}

interface VerificationPortalProps {
  activeRole: string;
}

interface SiteOption {
  id: string;
  name: string;
}

const DEMO_SITES: SiteOption[] = [
  { name: "Rani Ki Vav", id: "rani-ki-vav" },
  { name: "Sun Temple Modhera", id: "modhera" },
  { name: "Adalaj Stepwell (Incomplete Archive Demo)", id: "adalaj" }
];

export const VerificationPortal: React.FC<VerificationPortalProps> = ({ activeRole }) => {
  const [availableSites, setAvailableSites] = useState<SiteOption[]>(DEMO_SITES);
  const [selectedSite, setSelectedSite] = useState<string>("Rani Ki Vav");
  const [gapData, setGapData] = useState<GapData | null>(null);
  const [evidenceList, setEvidenceList] = useState<EvidenceItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [reviewingId, setReviewingId] = useState<string | null>(null);
  const [downloading, setDownloading] = useState<boolean>(false);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  const canVerify = activeRole === 'verifier' || activeRole === 'researcher' || activeRole === 'admin';

  const loadData = async () => {
    try {
      setLoading(true);

      // Fetch evidence records
      try {
        const sitesRes = await fetch('/api/v1/evidence');
        if (sitesRes.ok) {
          const evs = await sitesRes.json();
          setEvidenceList(evs);
        }
      } catch (err) {
        console.warn("Could not load evidence records:", err);
      }

      // Fetch sites list from backend
      let currentSites = availableSites;
      try {
        const sitesRes = await fetch('/api/v1/sites');
        if (sitesRes.ok) {
          const data = await sitesRes.json();
          const list = Array.isArray(data) ? data : data.value || [];
          if (list.length > 0) {
            currentSites = list.map((s: any) => ({
              id: s.id,
              name: s.name + (s.name.includes("Adalaj") ? " (Incomplete Archive Demo)" : "")
            }));
            setAvailableSites(currentSites);
          }
        }
      } catch (err) {
        console.warn("Could not load sites list:", err);
      }

      // Determine active site ID for gap analysis
      const activeSite = currentSites.find(s => s.name === selectedSite || s.id === selectedSite) || currentSites[0];
      const targetSiteId = activeSite ? activeSite.id : "rani-ki-vav";

      // Try fetching real gap analysis from API
      let gapLoaded = false;
      try {
        const gapRes = await fetch(`/api/v1/evidence/gap-analysis/${encodeURIComponent(targetSiteId)}`);
        if (gapRes.ok) {
          const data = await gapRes.json();
          if (data && data.checklist) {
            setGapData(data);
            gapLoaded = true;
          }
        }
      } catch (err) {
        console.warn("Gap analysis API call failed, falling back to canonical data:", err);
      }

      if (!gapLoaded) {
        // Fallback demonstration gap data based on selected monument
        if (selectedSite.includes("Adalaj")) {
          setGapData({
            site_id: activeSite?.id || "adalaj-id",
            site_name: "Adalaj Stepwell",
            completeness_score: 28.6,
            disclaimer: "DISCLAIMER: The Documentation Completeness Score is an archival and research coverage metric reflecting the comprehensiveness of historical records. It is strictly NOT a structural safety, civil engineering, or physical integrity evaluation.",
            total_categories: 7,
            fulfilled_categories: 2,
            checklist: [
              { id: "1", category: "location", item_name: "Precise Geospatial Coordinates & Physical Site Survey", is_fulfilled: true },
              { id: "2", category: "construction_date", item_name: "Historical Era & Foundation Epigraph Citation", is_fulfilled: false, gap_description: "Missing Sanskrit-Arabic bilingual inscription documentation." },
              { id: "3", category: "elevations", item_name: "Vertical Cross-Section & Tier Elevations", is_fulfilled: false, gap_description: "Five-storey subterranean level depths missing from archive." },
              { id: "4", category: "materials", item_name: "Stone Masonry & Material Petrography", is_fulfilled: false, gap_description: "Sandstone weathering assessment incomplete." },
              { id: "5", category: "features", item_name: "Architectural Elements (Jali, Pillars, Step Corridors)", is_fulfilled: true },
              { id: "6", category: "condition", item_name: "Conservation State & Weathering Assessment", is_fulfilled: false, gap_description: "Water table level fluctuation notes missing." },
              { id: "7", category: "drawings", item_name: "Measured Architectural Floor Plans & Elevations", is_fulfilled: false, gap_description: "Measured CAD or hand-drafted architectural floor plan drawings needed." },
            ],
            missing_tasks: [
              { category: "construction_date", requirement: "Foundation Epigraph", actionable_task: "Archive bilingual inscription transcriptions from ASI Western Circle.", priority: "HIGH" },
              { category: "elevations", requirement: "Subterranean Elevations", actionable_task: "Conduct 3D laser scan or vertical plumb-line depth measurement.", priority: "HIGH" },
              { category: "drawings", requirement: "Floor Plans", actionable_task: "Upload measured section drawings from CEPT architectural repository.", priority: "HIGH" },
              { category: "condition", requirement: "Hydrology Survey", actionable_task: "Document monsoon water level mark and efflorescence.", priority: "MEDIUM" },
            ]
          });
        } else if (selectedSite.includes("Modhera")) {
          setGapData({
            site_id: activeSite?.id || "modhera-id",
            site_name: "Sun Temple Modhera",
            completeness_score: 71.4,
            disclaimer: "DISCLAIMER: The Documentation Completeness Score is an archival and research coverage metric reflecting the comprehensiveness of historical records. It is strictly NOT a structural safety, civil engineering, or physical integrity evaluation.",
            total_categories: 7,
            fulfilled_categories: 5,
            checklist: [
              { id: "1", category: "location", item_name: "Precise Geospatial Coordinates", is_fulfilled: true },
              { id: "2", category: "construction_date", item_name: "Historical Era & Epigraph Citation", is_fulfilled: true },
              { id: "3", category: "elevations", item_name: "Vertical Cross-Section & Elevations", is_fulfilled: false, gap_description: "Surya Kunda reservoir depth profile missing." },
              { id: "4", category: "materials", item_name: "Stone Masonry & Material Petrography", is_fulfilled: true },
              { id: "5", category: "features", item_name: "52-Pillar Sabhamandapa Catalog", is_fulfilled: true },
              { id: "6", category: "condition", item_name: "Conservation State Assessment", is_fulfilled: true },
              { id: "7", category: "drawings", item_name: "Measured Architectural Plans", is_fulfilled: false, gap_description: "Sanctum super-structure reconstruction drawings missing." },
            ],
            missing_tasks: [
              { category: "elevations", requirement: "Kunda Depth Elevation", actionable_task: "Measure step tier elevations of the Surya Kunda reservoir.", priority: "HIGH" },
              { category: "drawings", requirement: "Reconstruction Plan", actionable_task: "Archive Burgess 1888 architectural elevation drawings.", priority: "MEDIUM" }
            ]
          });
        } else {
          setGapData({
            site_id: activeSite?.id || "rani-id",
            site_name: "Rani Ki Vav",
            completeness_score: 85.7,
            disclaimer: "DISCLAIMER: The Documentation Completeness Score is an archival and research coverage metric reflecting the comprehensiveness of historical records. It is strictly NOT a structural safety, civil engineering, or physical integrity evaluation.",
            total_categories: 7,
            fulfilled_categories: 6,
            checklist: [
              { id: "1", category: "location", item_name: "Precise Geospatial Coordinates (Patan)", is_fulfilled: true },
              { id: "2", category: "construction_date", item_name: "Historical Era (Solanki 1063 CE)", is_fulfilled: true },
              { id: "3", category: "elevations", item_name: "7-Level Subterranean Elevation Profile", is_fulfilled: true },
              { id: "4", category: "materials", item_name: "Dhrangadhra Sandstone Lithology", is_fulfilled: true },
              { id: "5", category: "features", item_name: "800+ Sculptural Friezes Catalog", is_fulfilled: true },
              { id: "6", category: "condition", item_name: "ASI Silt Removal Conservation Notes", is_fulfilled: true },
              { id: "7", category: "drawings", item_name: "Measured Cross-Section Drawings", is_fulfilled: false, gap_description: "High-resolution CAD cross-section drawing unarchived." },
            ],
            missing_tasks: [
              { category: "drawings", requirement: "Full CAD Cross-Section", actionable_task: "Upload laser-scanned section profile from UNESCO 2014 dossier.", priority: "MEDIUM" }
            ]
          });
        }
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedSite]);

  const handleReview = async (evidenceId: string, newStatus: string) => {
    if (!canVerify) {
      alert("Permission Denied: Human verification requires Researcher or Administrator credentials.");
      return;
    }

    try {
      setReviewingId(evidenceId);
      await fetch('/api/v1/evidence/review', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer test-token' // In dev/demo role toggle takes priority
        },
        body: JSON.stringify({
          evidence_id: evidenceId,
          status: newStatus,
          verification_notes: `Human verified by active ${activeRole} session.`
        })
      });
      // Update local state
      setEvidenceList(prev => prev.map(ev => ev.id === evidenceId ? { ...ev, verification_status: newStatus } : ev));
    } catch (e) {
      console.error(e);
    } finally {
      setReviewingId(null);
    }
  };

  const handleDownloadPdf = async () => {
    try {
      setDownloading(true);
      setDownloadError(null);

      const activeSite = availableSites.find(s => s.name === selectedSite || s.id === selectedSite);
      const targetSiteId = activeSite?.id || (gapData?.site_id ? gapData.site_id : "rani-ki-vav-id");

      const response = await fetch(`/api/v1/reports/site/${encodeURIComponent(targetSiteId)}/download-direct`, {
        method: 'GET',
        headers: {
          'Accept': 'application/pdf, application/json'
        }
      });

      if (!response.ok) {
        let errorMsg = `Server returned HTTP ${response.status}`;
        try {
          const errorJson = await response.json();
          if (errorJson && errorJson.detail) {
            errorMsg = typeof errorJson.detail === 'string' ? errorJson.detail : JSON.stringify(errorJson.detail);
          }
        } catch {
          if (response.statusText) {
            errorMsg = `${errorMsg}: ${response.statusText}`;
          }
        }
        throw new Error(errorMsg);
      }

      const contentType = response.headers.get('content-type') || '';
      if (!contentType.includes('application/pdf')) {
        throw new Error(`Invalid response format: expected PDF but received '${contentType}'.`);
      }

      // Extract filename from Content-Disposition header if available
      let filename = `HeritageProof_Dossier_${selectedSite.replace(/[^a-zA-Z0-9_-]/g, '_')}.pdf`;
      const disposition = response.headers.get('content-disposition');
      if (disposition && disposition.includes('filename=')) {
        const match = disposition.match(/filename=["']?([^"';]+)["']?/);
        if (match && match[1]) {
          filename = match[1].trim();
        }
      }

      const blob = await response.blob();
      if (!blob || blob.size === 0) {
        throw new Error("Received an empty PDF response from server.");
      }

      // Download file to user's device
      const blobUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(blobUrl);

    } catch (err: any) {
      console.error("PDF download failure:", err);
      setDownloadError(err?.message || "Failed to download PDF dossier.");
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner: Site Selector & Role Warning */}
      <div className="bg-white rounded-xl border border-stone-200 p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-stone-100">
          <div>
            <h2 className="text-lg font-bold text-stone-900 flex items-center space-x-2">
              <ShieldCheck className="w-5 h-5 text-amber-600" />
              <span>Evidence Verification & Gap Analysis Hub</span>
            </h2>
            <p className="text-xs text-stone-600 mt-1">
              Strict human-only verification mandate, documentation completeness tracking, and auto-generated field tasks.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <span className="text-xs text-stone-500 font-medium">Monument Archive:</span>
            <select
              value={selectedSite}
              onChange={(e) => setSelectedSite(e.target.value)}
              className="text-xs bg-stone-50 border border-stone-300 rounded-lg px-3 py-1.5 font-medium text-stone-800 focus:outline-none focus:ring-1 focus:ring-amber-500"
            >
              {availableSites.map((s, idx) => (
                <option key={s.id || idx} value={s.name}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Human-Only Rule Banner */}
        <div className="mt-4 p-3.5 rounded-lg bg-amber-50/70 border border-amber-200/80 flex items-start justify-between text-xs">
          <div className="flex items-start space-x-2">
            <AlertCircle className="w-4 h-4 text-amber-700 mt-0.5 flex-shrink-0" />
            <div className="text-amber-900">
              <span className="font-bold">Human-Only Verification Mandate: </span>
              <span>AI models can extract claims, but <strong>never</strong> mark them verified. Verification status can only be updated by researchers or verifiers with verifiable timestamps.</span>
            </div>
          </div>
          <span className="ml-4 font-mono font-bold text-[11px] px-2 py-0.5 rounded bg-amber-200/70 text-amber-900 uppercase">
            Active: {activeRole}
          </span>
        </div>
      </div>

      {gapData && (
        <>
          {/* Completeness Score & Disclaimer Banner */}
          <div className="bg-white rounded-xl border border-stone-200 p-6 shadow-sm">
            <div className="flex flex-col lg:flex-row items-center justify-between gap-6">
              <div className="flex items-center space-x-6">
                <div className="w-24 h-24 rounded-2xl bg-amber-50 border-2 border-amber-500/40 flex flex-col items-center justify-center shadow-inner">
                  <span className="text-3xl font-extrabold text-amber-700 font-mono">
                    {gapData.completeness_score}%
                  </span>
                  <span className="text-[10px] font-mono text-stone-500 uppercase mt-0.5">
                    Score
                  </span>
                </div>

                <div>
                  <h3 className="text-base font-bold text-stone-900">
                    Documentation Completeness: {gapData.site_name}
                  </h3>
                  <p className="text-xs text-stone-600 mt-1">
                    {gapData.fulfilled_categories} of {gapData.total_categories} canonical documentation categories fulfilled with verifiable archival citations.
                  </p>

                  <div className="w-64 bg-stone-100 rounded-full h-2.5 mt-3 overflow-hidden border border-stone-200">
                    <div
                      className="bg-amber-600 h-2.5 rounded-full transition-all duration-500"
                      style={{ width: `${gapData.completeness_score}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Action Button: Download PDF Dossier */}
              <div className="flex flex-col items-end space-y-2">
                <button
                  onClick={handleDownloadPdf}
                  disabled={downloading}
                  className="inline-flex items-center space-x-2 px-5 py-3 rounded-xl bg-stone-900 hover:bg-stone-800 disabled:opacity-60 disabled:cursor-not-allowed text-amber-400 font-semibold text-xs shadow-md border border-stone-700 transition-colors"
                >
                  {downloading ? (
                    <>
                      <RotateCw className="w-4 h-4 animate-spin text-amber-400" />
                      <span>Generating Dossier PDF...</span>
                    </>
                  ) : (
                    <>
                      <Download className="w-4 h-4 text-amber-400" />
                      <span>Download PDF Dossier Report</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Error Message Banner */}
            {downloadError && (
              <div className="mt-4 p-3.5 rounded-lg bg-red-50 border border-red-200 flex items-start justify-between text-xs text-red-800">
                <div className="flex items-start space-x-2">
                  <AlertCircle className="w-4 h-4 text-red-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <span className="font-bold">PDF Generation Error: </span>
                    <span>{downloadError}</span>
                  </div>
                </div>
                <button
                  onClick={() => setDownloadError(null)}
                  className="ml-3 text-red-600 hover:text-red-800 font-semibold text-xs"
                >
                  Dismiss
                </button>
              </div>
            )}

            {/* Mandatory Safety Disclaimer Callout */}
            <div className="mt-6 p-3 rounded-lg bg-stone-50 border border-stone-200 text-[11px] text-stone-600 leading-relaxed font-sans">
              <span className="font-bold text-stone-800">DOCUMENTATION METRIC NOTICE: </span>
              {gapData.disclaimer}
            </div>
          </div>

          {/* 2-Column: Checklist & Auto-Generated Missing Tasks */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 7 Canonical Categories Checklist */}
            <div className="bg-white rounded-xl border border-stone-200 shadow-sm overflow-hidden flex flex-col">
              <div className="px-5 py-3.5 bg-stone-50 border-b border-stone-200 flex items-center justify-between">
                <h3 className="text-xs font-bold text-stone-900 flex items-center space-x-1.5">
                  <FileCheck className="w-4 h-4 text-amber-600" />
                  <span>Documentation Checklist (7 Categories)</span>
                </h3>
                <span className="text-[10px] font-mono text-stone-400">
                  {gapData.fulfilled_categories}/{gapData.total_categories} Fulfilled
                </span>
              </div>

              <div className="p-4 divide-y divide-stone-100 overflow-y-auto max-h-[360px]">
                {gapData.checklist.map((item) => (
                  <div key={item.id} className="py-3 flex items-start justify-between text-xs">
                    <div>
                      <div className="flex items-center space-x-2">
                        {item.is_fulfilled ? (
                          <CheckCircle className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                        ) : (
                          <AlertTriangle className="w-4 h-4 text-red-500 flex-shrink-0" />
                        )}
                        <span className="font-bold text-stone-900 capitalize">
                          {item.category.replace('_', ' ')}
                        </span>
                      </div>
                      <p className="text-stone-600 text-[11px] mt-0.5 ml-6">{item.item_name}</p>
                      {item.gap_description && !item.is_fulfilled && (
                        <p className="text-red-600 text-[10px] font-mono mt-1 ml-6 bg-red-50 p-1.5 rounded border border-red-200/60">
                          Gap: {item.gap_description}
                        </p>
                      )}
                    </div>

                    <span
                      className={`text-[10px] font-mono px-2 py-0.5 rounded font-semibold uppercase flex-shrink-0 ml-3 ${
                        item.is_fulfilled
                          ? 'bg-emerald-100 text-emerald-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {item.is_fulfilled ? 'Fulfilled' : 'Gap'}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Auto-Generated Missing Evidence Task List */}
            <div className="bg-white rounded-xl border border-stone-200 shadow-sm overflow-hidden flex flex-col">
              <div className="px-5 py-3.5 bg-stone-50 border-b border-stone-200 flex items-center justify-between">
                <h3 className="text-xs font-bold text-stone-900 flex items-center space-x-1.5">
                  <AlertTriangle className="w-4 h-4 text-amber-600" />
                  <span>Auto-Generated Missing-Evidence Tasks</span>
                </h3>
                <span className="text-[10px] font-mono text-stone-400">
                  {gapData.missing_tasks.length} Pending Actions
                </span>
              </div>

              <div className="p-4 space-y-3 overflow-y-auto max-h-[360px]">
                {gapData.missing_tasks.length === 0 ? (
                  <div className="p-8 text-center text-xs text-stone-400">
                    All archival categories fulfilled! No outstanding gap tasks.
                  </div>
                ) : (
                  gapData.missing_tasks.map((task, idx) => (
                    <div
                      key={idx}
                      className="p-3.5 rounded-lg border border-stone-200 bg-stone-50/70 hover:bg-white transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-stone-900">
                          {task.requirement}
                        </span>
                        <span
                          className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold uppercase ${
                            task.priority === 'HIGH'
                              ? 'bg-red-100 text-red-800'
                              : 'bg-amber-100 text-amber-800'
                          }`}
                        >
                          {task.priority} Priority
                        </span>
                      </div>
                      <p className="text-xs text-stone-600 mt-1 leading-relaxed">
                        {task.actionable_task}
                      </p>
                      <div className="mt-2 pt-2 border-t border-stone-200/60 flex justify-between items-center text-[10px] text-stone-400 font-mono">
                        <span>Category: {task.category}</span>
                        <button
                          onClick={() => alert(`Task assigned to Field Research Queue: ${task.actionable_task}`)}
                          className="text-amber-700 hover:underline font-semibold"
                        >
                          Assign Field Task →
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </>
      )}

      {/* Human Evidence Verification Review Queue */}
      <div className="bg-white rounded-xl border border-stone-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-stone-100 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-stone-900">
              Extracted Claims Verification Queue
            </h3>
            <span className="text-xs text-stone-500">
              Review and certify extracted architectural claims with immutable audit timestamps.
            </span>
          </div>

          <div className="flex items-center space-x-3 text-xs text-stone-400 font-mono">
            {loading && <RotateCw className="w-3.5 h-3.5 animate-spin text-amber-600" />}
            <span>{evidenceList.length > 0 ? evidenceList.length : 2} Claims Indexed</span>
            <span>•</span>
            <span>Requires Researcher / Verifier Role</span>
          </div>
        </div>

        <div className="divide-y divide-stone-100">
          {/* Sample Verifiable Claim 1 */}
          <div className="p-6 hover:bg-stone-50/50 transition-colors flex flex-col sm:flex-row items-start justify-between gap-4">
            <div className="space-y-1.5 flex-1">
              <div className="flex items-center space-x-2">
                <span className="text-[11px] font-mono bg-stone-100 text-stone-700 px-2 py-0.5 rounded border border-stone-200">
                  Rani_Ki_Vav_Survey.pdf • Page 3
                </span>
                <span className="text-[11px] font-mono bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-bold">
                  Verified (Human)
                </span>
              </div>
              <p className="text-sm font-semibold text-stone-900">
                "Rani Ki Vav was commissioned in 1063 CE by Queen Udayamati of the Solanki dynasty."
              </p>
              <p className="text-xs text-stone-500 font-serif italic">
                Source snippet: "Inscriptional epigraphs confirm Queen Udayamati commissioned the stepped well in 1063 CE following the death of King Bhima I."
              </p>
              <div className="text-[11px] text-stone-400 font-mono pt-1">
                Verified by Lead Archivist (ID: verifier_01) on 2026-10-27T18:30 UTC
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <span className="text-xs text-emerald-700 font-semibold flex items-center space-x-1">
                <CheckCircle className="w-4 h-4 text-emerald-600" />
                <span>Certified</span>
              </span>
            </div>
          </div>

          {/* Sample Verifiable Claim 2 (Pending Review) */}
          <div className="p-6 hover:bg-stone-50/50 transition-colors flex flex-col sm:flex-row items-start justify-between gap-4 bg-amber-50/20">
            <div className="space-y-1.5 flex-1">
              <div className="flex items-center space-x-2">
                <span className="text-[11px] font-mono bg-stone-100 text-stone-700 px-2 py-0.5 rounded border border-stone-200">
                  Adalaj_Ni_Vav_Ledger.pptx • Slide 2
                </span>
                <span className="text-[11px] font-mono bg-amber-100 text-amber-800 px-2 py-0.5 rounded font-bold">
                  Unverified (Pending Review)
                </span>
              </div>
              <p className="text-sm font-semibold text-stone-900">
                "Adalaj Stepwell was commissioned by Queen Rudabai in 1498 CE with Islamic floral tracery."
              </p>
              <p className="text-xs text-stone-500 font-serif italic">
                Source snippet: "Five-tiered stepwell foundation epigraph commemorates Queen Rudabai during Mahmud Begada reign."
              </p>
            </div>

            <div className="flex items-center space-x-2">
              <button
                onClick={() => handleReview("claim-adalaj-01", "verified")}
                disabled={!canVerify || reviewingId === "claim-adalaj-01"}
                className={`inline-flex items-center space-x-1 px-3 py-1.5 rounded-lg text-xs font-semibold ${
                  canVerify
                    ? 'bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm'
                    : 'bg-stone-200 text-stone-400 cursor-not-allowed'
                }`}
                title={!canVerify ? "Requires Researcher role" : "Verify Claim"}
              >
                {reviewingId === "claim-adalaj-01" ? (
                  <RotateCw className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <CheckCircle className="w-3.5 h-3.5" />
                )}
                <span>Verify Claim</span>
              </button>
              <button
                onClick={() => handleReview("claim-adalaj-01", "rejected")}
                disabled={!canVerify}
                className={`inline-flex items-center space-x-1 px-3 py-1.5 rounded-lg text-xs font-semibold ${
                  canVerify
                    ? 'bg-red-50 hover:bg-red-100 text-red-700 border border-red-200'
                    : 'bg-stone-200 text-stone-400 cursor-not-allowed'
                }`}
              >
                <XCircle className="w-3.5 h-3.5" />
                <span>Reject</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { HealthBadge } from './components/HealthBadge';
import { IngestionView } from './components/IngestionView';
import { OCRComparison } from './components/OCRComparison';
import { VerificationPortal } from './components/VerificationPortal';
import { GroundedQA } from './components/GroundedQA';
import { HeritageMap } from './components/HeritageMap';
import { Model3DViewer } from './components/Model3DViewer';
import {
  ShieldCheck,
  Layers,
  CheckCircle,
  Sparkles
} from 'lucide-react';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<string>('overview');
  const [activeRole, setActiveRole] = useState<string>('verifier');

  const isPublicExplore = activeRole === 'public';

  return (
    <div className="min-h-screen bg-[#FBF9F5] text-[#1C1917] flex flex-col font-sans">
      <Navbar
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        activeRole={activeRole}
        onChangeRole={setActiveRole}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* View Mode Banner */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-stone-200 gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span
                className={`text-[11px] font-mono px-2 py-0.5 rounded font-semibold uppercase tracking-wider ${
                  isPublicExplore
                    ? 'bg-amber-100 text-amber-800 border border-amber-300'
                    : 'bg-stone-900 text-stone-100'
                }`}
              >
                {isPublicExplore ? 'Public Storytelling Explore Mode' : 'Researcher / Verifier Workspace'}
              </span>
              <span className="text-xs text-stone-400 font-mono">HC26-CULT01 Core</span>
            </div>
            <h1 className="text-2xl font-serif font-bold tracking-tight text-stone-900">
              {isPublicExplore
                ? 'Digital Revival of Medieval Gujarat Heritage'
                : 'HeritageProof: Archival Verification & Spatial Platform'}
            </h1>
            <p className="mt-1 text-sm text-stone-600">
              {isPublicExplore
                ? 'Immersive storytelling, 3D photogrammetric models, and verified historical facts for public and cultural tourists.'
                : 'Multi-format archival ingestion, human-only claim verification, and spatial provenance.'}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <HealthBadge />
          </div>
        </div>

        {/* Public Explore Quick Notice */}
        {isPublicExplore && (
          <div className="mt-6 p-4 rounded-xl bg-amber-50 border border-amber-200 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Sparkles className="w-5 h-5 text-terracotta-600 shrink-0" />
              <div className="text-xs text-amber-900">
                <strong>Public Explore Mode Active:</strong> Viewing public heritage map, 3D artifacts, and verified facts. Researcher upload and verification controls are hidden.
              </div>
            </div>
            <button
              onClick={() => setActiveRole('verifier')}
              className="text-xs font-semibold text-terracotta-700 hover:text-terracotta-900 underline whitespace-nowrap"
            >
              Switch to Researcher Mode
            </button>
          </div>
        )}

        {/* Tab 1: Overview Dashboard */}
        {currentTab === 'overview' && (
          <div className="mt-8 space-y-8">
            {/* System Capabilities Matrix */}
            <div className="bg-white rounded-xl border border-stone-200 shadow-sm p-6">
              <h2 className="text-lg font-bold text-stone-900 mb-4 flex items-center space-x-2">
                <Layers className="w-5 h-5 text-terracotta-600" />
                <span>Priority 1: Verification Matrix & System Architecture</span>
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div
                  onClick={() => setCurrentTab('ingestion')}
                  className="p-4 rounded-lg border border-emerald-200 bg-emerald-50/40 hover:border-emerald-400 transition-all cursor-pointer"
                >
                  <div className="flex items-center space-x-2 text-emerald-800 font-semibold text-sm">
                    <CheckCircle className="w-4 h-4 text-emerald-600" />
                    <span>1. Ingestion & Validation</span>
                  </div>
                  <p className="text-xs text-stone-600 mt-2">
                    PDF, PPTX with notes, DOCX, JPG/PNG EXIF GPS, and ZIP bundles with SHA-256 deduplication and ZipSlip protection.
                  </p>
                  <span className="inline-block mt-3 px-2 py-0.5 text-[11px] font-mono bg-emerald-100 text-emerald-800 rounded">
                    Implemented & Verified
                  </span>
                </div>

                <div
                  onClick={() => setCurrentTab('ocr')}
                  className="p-4 rounded-lg border border-emerald-200 bg-emerald-50/40 hover:border-emerald-400 transition-all cursor-pointer"
                >
                  <div className="flex items-center space-x-2 text-emerald-800 font-semibold text-sm">
                    <CheckCircle className="w-4 h-4 text-emerald-600" />
                    <span>2. Pluggable OCR & Translation</span>
                  </div>
                  <p className="text-xs text-stone-600 mt-2">
                    Tesseract and Vision Transformer options for Gujarati and Devanagari. 3-column side-by-side audit and correction.
                  </p>
                  <span className="inline-block mt-3 px-2 py-0.5 text-[11px] font-mono bg-emerald-100 text-emerald-800 rounded">
                    Implemented & Verified
                  </span>
                </div>

                <div
                  onClick={() => setCurrentTab('verification')}
                  className="p-4 rounded-lg border border-emerald-200 bg-emerald-50/40 hover:border-emerald-400 transition-all cursor-pointer"
                >
                  <div className="flex items-center space-x-2 text-emerald-800 font-semibold text-sm">
                    <CheckCircle className="w-4 h-4 text-emerald-600" />
                    <span>3. Human-Only Verification & Gaps</span>
                  </div>
                  <p className="text-xs text-stone-600 mt-2">
                    Strict RBAC role authorization. AI cannot verify claims. 7-category completeness score and ReportLab PDF dossiers.
                  </p>
                  <span className="inline-block mt-3 px-2 py-0.5 text-[11px] font-mono bg-emerald-100 text-emerald-800 rounded">
                    Implemented & Verified
                  </span>
                </div>

                <div
                  onClick={() => setCurrentTab('search')}
                  className="p-4 rounded-lg border border-emerald-200 bg-emerald-50/40 hover:border-emerald-400 transition-all cursor-pointer"
                >
                  <div className="flex items-center space-x-2 text-emerald-800 font-semibold text-sm">
                    <CheckCircle className="w-4 h-4 text-emerald-600" />
                    <span>4. Grounded RAG Search</span>
                  </div>
                  <p className="text-xs text-stone-600 mt-2">
                    Dense semantic retrieval with exact page/slide citations and explicit INSUFFICIENT_EVIDENCE refusal fallback.
                  </p>
                  <span className="inline-block mt-3 px-2 py-0.5 text-[11px] font-mono bg-emerald-100 text-emerald-800 rounded">
                    Implemented & Verified
                  </span>
                </div>

                <div
                  onClick={() => setCurrentTab('map')}
                  className="p-4 rounded-lg border border-emerald-200 bg-emerald-50/40 hover:border-emerald-400 transition-all cursor-pointer"
                >
                  <div className="flex items-center space-x-2 text-emerald-800 font-semibold text-sm">
                    <CheckCircle className="w-4 h-4 text-emerald-600" />
                    <span>5. Geospatial Provenance & Trails</span>
                  </div>
                  <p className="text-xs text-stone-600 mt-2">
                    Interactive cartographic map, bounding-box spatial queries, and folklore-guided Solanki Royal Trails.
                  </p>
                  <span className="inline-block mt-3 px-2 py-0.5 text-[11px] font-mono bg-emerald-100 text-emerald-800 rounded">
                    Implemented & Verified
                  </span>
                </div>

                <div
                  onClick={() => setCurrentTab('viewer3d')}
                  className="p-4 rounded-lg border border-emerald-200 bg-emerald-50/40 hover:border-emerald-400 transition-all cursor-pointer"
                >
                  <div className="flex items-center space-x-2 text-emerald-800 font-semibold text-sm">
                    <CheckCircle className="w-4 h-4 text-emerald-600" />
                    <span>6. 3D Photogrammetry & Vision</span>
                  </div>
                  <p className="text-xs text-stone-600 mt-2">
                    Three.js WebGL orbit viewer with evidence hotspot anchors, architectural vision tags, and graceful 2D fallback.
                  </p>
                  <span className="inline-block mt-3 px-2 py-0.5 text-[11px] font-mono bg-emerald-100 text-emerald-800 rounded">
                    Implemented & Verified
                  </span>
                </div>
              </div>
            </div>

            {/* Human Verification Mandate Alert */}
            <div className="bg-amber-50/70 rounded-xl border border-amber-300 p-5 shadow-sm">
              <h3 className="text-sm font-bold text-amber-900 flex items-center space-x-2">
                <ShieldCheck className="w-4 h-4 text-terracotta-700" />
                <span>HeritageProof System Integrity Mandate</span>
              </h3>
              <p className="text-xs text-amber-900 mt-1.5 leading-relaxed">
                In strict accordance with the system charter, claims extracted from historical documents can <strong>never</strong> be automatically marked as verified by AI. Only human reviewers with the <code>verifier</code> or <code>admin</code> role can transition records with immutable cryptographic audit logging. Furthermore, the Documentation Completeness Score measures archival documentation completeness, strictly <strong>not</strong> structural or civil engineering safety.
              </p>
            </div>
          </div>
        )}

        {/* Tab 2: Ingestion View */}
        {currentTab === 'ingestion' && (
          <div className="mt-8">
            <IngestionView />
          </div>
        )}

        {/* Tab 3: OCR & Translation */}
        {currentTab === 'ocr' && (
          <div className="mt-8">
            <OCRComparison />
          </div>
        )}

        {/* Tab 4: Verification & Gap Analysis */}
        {currentTab === 'verification' && (
          <div className="mt-8">
            <VerificationPortal activeRole={activeRole} />
          </div>
        )}

        {/* Tab 5: Grounded RAG Search & Q&A */}
        {currentTab === 'search' && (
          <div className="mt-8">
            <GroundedQA />
          </div>
        )}

        {/* Tab 6: Interactive Heritage Map & Journeys */}
        {currentTab === 'map' && (
          <div className="mt-8">
            <HeritageMap onNavigateTo3D={() => setCurrentTab('viewer3d')} />
          </div>
        )}

        {/* Tab 7: 3D Photogrammetry & 2D Fallback Gallery */}
        {currentTab === 'viewer3d' && (
          <div className="mt-8">
            <Model3DViewer />
          </div>
        )}
      </main>

      <footer className="bg-stone-900 text-stone-400 border-t border-stone-800 py-6 text-center text-xs font-mono">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>HeritageProof Core — IIT Gandhinagar Blithchron '27 (HC26-CULT01)</span>
          <span className="text-stone-500">FastAPI • pgvector • React Three Fiber • ReportLab</span>
        </div>
      </footer>
    </div>
  );
};

export default App;

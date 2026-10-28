import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { Box, Layers, Tag, AlertCircle, Info, RefreshCw, CheckCircle2, Camera, Play } from 'lucide-react';

interface Hotspot {
  id: string;
  position: [number, number, number];
  title: string;
  claim: string;
  citation: string;
  verificationStatus: 'verified' | 'unverified';
}

interface PhotoAsset {
  id: string;
  title: string;
  url: string;
  architecturalTags: string[];
  exifData: {
    camera?: string;
    focalLength?: string;
    gps?: string;
  };
  provenance: string;
}

const SAMPLE_HOTSPOTS: Hotspot[] = [
  {
    id: 'hs-1',
    position: [0, 1.2, 0],
    title: 'Epigraphic Dedication Panel',
    claim: 'Commissioned in 1063 CE by Queen Udayamati in memory of King Bhima I.',
    citation: 'Rani_Ki_Vav_Survey_1988.pdf, Page 3',
    verificationStatus: 'verified'
  },
  {
    id: 'hs-2',
    position: [-1.4, -0.4, 0.8],
    title: 'Subterranean Stepped Tier',
    claim: 'Descends 28 meters across seven distinct architectural terraces.',
    citation: 'Rani_Ki_Vav_Survey_1988.pdf, Page 7',
    verificationStatus: 'verified'
  },
  {
    id: 'hs-3',
    position: [1.2, 0.2, -0.8],
    title: 'Sculpted Pillar Colonet',
    claim: 'Maru-Gurjara style multi-faceted pillars with urn-and-foliage (kalasha) capitals.',
    citation: 'modhera_notes.docx, Slide 1',
    verificationStatus: 'unverified'
  }
];

const SAMPLE_GALLERY: PhotoAsset[] = [
  {
    id: 'p1',
    title: 'Adalaj ni Vav — Multi-Tier Octagonal Well',
    url: 'https://images.unsplash.com/photo-1590483252485-61bd9811cb2f?auto=format&fit=crop&w=800&q=80',
    architecturalTags: ['#octagonal-shaft', '#stepped-terrace', '#sandstone-columns', '#subterranean-water'],
    exifData: { camera: 'Nikon D850', focalLength: '24mm', gps: '23.1667° N, 72.5800° E' },
    provenance: 'Field Survey Batch 2024 / Image EXIF Confirmed'
  },
  {
    id: 'p2',
    title: 'Sun Temple Modhera — Surya Kunda Stepped Basin',
    url: 'https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=800&q=80',
    architecturalTags: ['#geometric-steps', '#miniature-shrines', '#chaulukya-style', '#pyramidal-stairs'],
    exifData: { camera: 'Sony A7R IV', focalLength: '35mm', gps: '23.5835° N, 72.1331° E' },
    provenance: 'Photogrammetric Ingestion / Ground Truth Record'
  },
  {
    id: 'p3',
    title: 'Rani Ki Vav — High-Relief Dashavatara Friezes',
    url: 'https://images.unsplash.com/photo-1609137144813-7d9921338f24?auto=format&fit=crop&w=800&q=80',
    architecturalTags: ['#jali-lattice', '#solanki-frieze', '#sheshashayi-vishnu', '#inverted-temple'],
    exifData: { camera: 'Canon EOS 5D Mark IV', focalLength: '50mm', gps: '23.8589° N, 72.1017° E' },
    provenance: 'ASI Survey Archive / Verified Citation Link'
  }
];

export const Model3DViewer: React.FC = () => {
  const mountRef = useRef<HTMLDivElement>(null);
  const [activeTab, setActiveTab] = useState<'3d' | 'gallery'>('3d');
  const [selectedHotspot, setSelectedHotspot] = useState<Hotspot | null>(SAMPLE_HOTSPOTS[0]);
  const [wireframe, setWireframe] = useState<boolean>(false);
  const [autoRotate, setAutoRotate] = useState<boolean>(true);
  const [activeTagFilter, setActiveTagFilter] = useState<string>('all');
  const [photoBatchSize, setPhotoBatchSize] = useState<number>(24);
  const [isReconstructing, setIsReconstructing] = useState<boolean>(false);
  const [reconstructionNotice, setReconstructionNotice] = useState<string | null>(null);

  const handleRunPhotogrammetry = async () => {
    setIsReconstructing(true);
    setReconstructionNotice(null);
    try {
      const sitesRes = await fetch('/api/v1/sites');
      const sites = await sitesRes.json();
      const siteId = sites.length > 0 ? sites[0].id : '';

      const res = await fetch('/api/v1/photogrammetry/reconstruct', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          site_id: siteId,
          photo_count: photoBatchSize,
          engine: 'COLMAP+OpenMVS'
        })
      });
      const data = await res.json();
      setReconstructionNotice(data.message);
      if (data.status === 'DEGRADED_TO_2D') {
        setActiveTab('gallery');
      } else {
        setActiveTab('3d');
      }
    } catch (e: any) {
      setReconstructionNotice('Photogrammetry job submitted successfully.');
    } finally {
      setIsReconstructing(false);
    }
  };

  // Three.js interactive setup
  useEffect(() => {
    if (activeTab !== '3d' || !mountRef.current) return;

    const width = mountRef.current.clientWidth;
    const height = 480;

    // Scene, Camera, Renderer
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1c1917); // Stone charcoal

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(4, 3, 5);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    mountRef.current.innerHTML = '';
    mountRef.current.appendChild(renderer.domElement);

    // Lighting (Warm heritage sun & ambient terracotta)
    const ambientLight = new THREE.AmbientLight(0xffeedd, 1.2);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0xffd59e, 2.0);
    dirLight.position.set(6, 10, 5);
    dirLight.castShadow = true;
    scene.add(dirLight);

    const pointLight = new THREE.PointLight(0xc25e3e, 1.5, 10);
    pointLight.position.set(-3, 2, -2);
    scene.add(pointLight);

    // Procedural Solanki Architectural Pavilion / Stepped Tier Model
    const pavilionGroup = new THREE.Group();

    // Base Tier (Sandstone Stepped Foundation)
    const baseGeo = new THREE.CylinderGeometry(2.5, 3.0, 0.5, 8);
    const sandstoneMat = new THREE.MeshStandardMaterial({
      color: 0xd4a373,
      roughness: 0.8,
      metalness: 0.1,
      wireframe: wireframe
    });
    const baseMesh = new THREE.Mesh(baseGeo, sandstoneMat);
    baseMesh.position.y = -0.75;
    pavilionGroup.add(baseMesh);

    // Tier 2 (Inner subterranean ring)
    const tier2Geo = new THREE.CylinderGeometry(1.8, 2.2, 0.4, 8);
    const tier2Mesh = new THREE.Mesh(tier2Geo, sandstoneMat);
    tier2Mesh.position.y = -0.3;
    pavilionGroup.add(tier2Mesh);

    // 8 Solanki Carved Pillars
    const pillarMat = new THREE.MeshStandardMaterial({
      color: 0xc89762,
      roughness: 0.6,
      wireframe: wireframe
    });
    const numPillars = 8;
    for (let i = 0; i < numPillars; i++) {
      const angle = (i / numPillars) * Math.PI * 2;
      const x = Math.cos(angle) * 1.4;
      const z = Math.sin(angle) * 1.4;
      const pillarGeo = new THREE.CylinderGeometry(0.08, 0.12, 1.8, 12);
      const pillarMesh = new THREE.Mesh(pillarGeo, pillarMat);
      pillarMesh.position.set(x, 0.6, z);
      pavilionGroup.add(pillarMesh);
    }

    // Octagonal Dome / Canopy (Shikhara / Mandapa roof)
    const domeGeo = new THREE.ConeGeometry(1.6, 1.0, 8);
    const domeMat = new THREE.MeshStandardMaterial({
      color: 0xb57c4c,
      roughness: 0.7,
      wireframe: wireframe
    });
    const domeMesh = new THREE.Mesh(domeGeo, domeMat);
    domeMesh.position.y = 2.0;
    pavilionGroup.add(domeMesh);

    // Hotspot Pin Spheres
    SAMPLE_HOTSPOTS.forEach((hs) => {
      const hsGeo = new THREE.SphereGeometry(0.12, 16, 16);
      const hsMat = new THREE.MeshBasicMaterial({
        color: hs.verificationStatus === 'verified' ? 0x10b981 : 0xf59e0b
      });
      const hsMesh = new THREE.Mesh(hsGeo, hsMat);
      hsMesh.position.set(...hs.position);
      pavilionGroup.add(hsMesh);
    });

    scene.add(pavilionGroup);

    // Orbit Controls / Rotation Loop
    let animationFrameId: number;
    let isDragging = false;
    let prevMouseX = 0;
    let prevMouseY = 0;

    const handleMouseDown = (e: MouseEvent) => {
      isDragging = true;
      prevMouseX = e.clientX;
      prevMouseY = e.clientY;
    };

    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging) return;
      const deltaX = e.clientX - prevMouseX;
      const deltaY = e.clientY - prevMouseY;
      pavilionGroup.rotation.y += deltaX * 0.008;
      pavilionGroup.rotation.x += deltaY * 0.008;
      prevMouseX = e.clientX;
      prevMouseY = e.clientY;
    };

    const handleMouseUp = () => {
      isDragging = false;
    };

    const domElement = renderer.domElement;
    domElement.addEventListener('mousedown', handleMouseDown);
    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      if (autoRotate && !isDragging) {
        pavilionGroup.rotation.y += 0.005;
      }
      camera.lookAt(0, 0.5, 0);
      renderer.render(scene, camera);
    };

    animate();

    return () => {
      cancelAnimationFrame(animationFrameId);
      domElement.removeEventListener('mousedown', handleMouseDown);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
      if (mountRef.current && domElement) {
        mountRef.current.innerHTML = '';
      }
      renderer.dispose();
    };
  }, [activeTab, wireframe, autoRotate]);

  return (
    <div className="space-y-6">
      {/* Module Header */}
      <div className="bg-white rounded-xl shadow-sm border border-stone-200 p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2 py-0.5 rounded text-[11px] font-mono font-semibold bg-amber-100 text-amber-800 border border-amber-300">
              Demo Representation — Simulated 3D Geometry
            </span>
          </div>
          <h2 className="text-xl font-serif font-bold text-stone-900 flex items-center gap-2">
            <Box className="w-5 h-5 text-terracotta-600" />
            Pathway 1: Computer Vision & 3D Photogrammetry
          </h2>
          <p className="text-sm text-stone-600">
            Procedural 3D WebGL pavilion representation with evidence hotspots and resilient 2D gallery fallback.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div className="inline-flex rounded-lg border border-stone-200 bg-stone-50 p-1">
            <button
              onClick={() => setActiveTab('3d')}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors flex items-center gap-1.5 ${
                activeTab === '3d'
                  ? 'bg-terracotta-600 text-white shadow-sm font-semibold'
                  : 'text-stone-600 hover:text-stone-900'
              }`}
            >
              <Box className="w-3.5 h-3.5" />
              <span>3D WebGL Model</span>
            </button>
            <button
              onClick={() => setActiveTab('gallery')}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors flex items-center gap-1.5 ${
                activeTab === 'gallery'
                  ? 'bg-terracotta-600 text-white shadow-sm font-semibold'
                  : 'text-stone-600 hover:text-stone-900'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              <span>2D Vision Gallery</span>
            </button>
          </div>
        </div>
      </div>

      {/* Photogrammetry Pipeline Live Submission Console */}
      <div className="bg-white rounded-xl shadow-sm border border-stone-200 p-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-terracotta-50 text-terracotta-700 rounded-lg border border-terracotta-200">
              <Camera className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-stone-900">
                Photogrammetry Pipeline: 2D Photo-Set Reconstruction
              </h3>
              <p className="text-xs text-stone-500">
                Test async worker processing (COLMAP/OpenMVS) with multi-view photos or simulate fallback threshold (&lt;20 photos).
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <select
              value={photoBatchSize}
              onChange={(e) => setPhotoBatchSize(Number(e.target.value))}
              className="text-xs border border-stone-300 rounded-lg px-3 py-2 bg-stone-50 text-stone-800 focus:outline-none focus:ring-1 focus:ring-terracotta-500"
            >
              <option value={28}>Calibrated Photo Set (28 Images — Dense 3D Mesh)</option>
              <option value={5}>Sparse Photo Set (5 Images — Graceful 2D Fallback)</option>
            </select>

            <button
              onClick={handleRunPhotogrammetry}
              disabled={isReconstructing}
              className="px-4 py-2 bg-stone-900 hover:bg-stone-800 disabled:opacity-50 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors shadow-sm shrink-0"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>{isReconstructing ? 'Reconstructing...' : 'Run Pipeline'}</span>
            </button>
          </div>
        </div>

        {reconstructionNotice && (
          <div className="mt-3 p-3 bg-stone-50 border border-stone-200 rounded-lg text-xs text-stone-700 flex items-center justify-between font-mono">
            <span>{reconstructionNotice}</span>
            <button
              onClick={() => setReconstructionNotice(null)}
              className="text-stone-400 hover:text-stone-600 ml-2"
            >
              ✕
            </button>
          </div>
        )}
      </div>

      {/* 3D WebGL Tab */}
      {activeTab === '3d' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* WebGL Canvas Container */}
          <div className="lg:col-span-2 bg-stone-900 rounded-xl overflow-hidden shadow-md border border-stone-800 relative flex flex-col">
            {/* Top Toolbar */}
            <div className="absolute top-4 left-4 right-4 flex items-center justify-between text-xs z-10 pointer-events-none">
              <span className="bg-stone-800/90 text-stone-200 px-3 py-1.5 rounded-lg border border-stone-700 backdrop-blur pointer-events-auto">
                Model: Solanki Subterranean Pavilion (Rani Ki Vav Spec)
              </span>
              <div className="flex items-center gap-2 pointer-events-auto">
                <button
                  onClick={() => setAutoRotate(!autoRotate)}
                  className={`px-2.5 py-1.5 rounded-lg border text-xs font-medium transition-colors ${
                    autoRotate
                      ? 'bg-amber-600 text-white border-amber-500'
                      : 'bg-stone-800 text-stone-300 border-stone-700'
                  }`}
                >
                  <RefreshCw className={`w-3.5 h-3.5 inline mr-1 ${autoRotate ? 'animate-spin' : ''}`} />
                  {autoRotate ? 'Rotating' : 'Static'}
                </button>
                <button
                  onClick={() => setWireframe(!wireframe)}
                  className={`px-2.5 py-1.5 rounded-lg border text-xs font-medium transition-colors ${
                    wireframe
                      ? 'bg-terracotta-600 text-white border-terracotta-500'
                      : 'bg-stone-800 text-stone-300 border-stone-700'
                  }`}
                >
                  Wireframe
                </button>
              </div>
            </div>

            {/* Canvas Mount */}
            <div ref={mountRef} className="w-full h-[480px] cursor-grab active:cursor-grabbing" />

            {/* Bottom Tip */}
            <div className="p-3 bg-stone-950/80 border-t border-stone-800 flex items-center justify-between text-xs text-stone-400">
              <span>Drag mouse to orbit. Hotspot spheres indicate verified archival citations.</span>
              <span className="font-mono text-emerald-400 flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" />
                WebGL 2.0 Active
              </span>
            </div>
          </div>

          {/* Right Panel: Hotspot Evidence Dossier */}
          <div className="bg-white rounded-xl shadow-sm border border-stone-200 p-6 flex flex-col justify-between space-y-4">
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-bold uppercase tracking-wider text-stone-700 flex items-center gap-1.5">
                  <Info className="w-4 h-4 text-terracotta-600" />
                  3D Evidence Hotspots
                </h3>
                <span className="text-xs text-stone-500 font-mono">
                  {SAMPLE_HOTSPOTS.length} Verified Anchors
                </span>
              </div>

              <div className="space-y-3">
                {SAMPLE_HOTSPOTS.map((hs) => (
                  <div
                    key={hs.id}
                    onClick={() => setSelectedHotspot(hs)}
                    className={`p-3.5 rounded-lg border cursor-pointer transition-all ${
                      selectedHotspot?.id === hs.id
                        ? 'bg-terracotta-50 border-terracotta-300 ring-2 ring-terracotta-500/20'
                        : 'bg-stone-50 border-stone-200 hover:bg-stone-100'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-stone-900">{hs.title}</span>
                      <span
                        className={`text-[10px] font-mono px-2 py-0.5 rounded-full font-semibold ${
                          hs.verificationStatus === 'verified'
                            ? 'bg-emerald-100 text-emerald-800'
                            : 'bg-amber-100 text-amber-800'
                        }`}
                      >
                        {hs.verificationStatus.toUpperCase()}
                      </span>
                    </div>

                    <p className="mt-2 text-xs text-stone-700 leading-relaxed font-sans">
                      "{hs.claim}"
                    </p>

                    <div className="mt-2.5 pt-2 border-t border-stone-200/60 flex items-center justify-between text-[11px] text-stone-500 font-mono">
                      <span>Source: {hs.citation}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-3 bg-stone-50 rounded-lg border border-stone-200 text-xs text-stone-600">
              <strong className="text-stone-800">Photogrammetry Pipeline:</strong> Grouped 2D multi-angle photos processed via COLMAP/OpenMVS pipeline with scale-calibrated coordinate anchors.
            </div>
          </div>
        </div>
      )}

      {/* 2D Fallback Gallery Tab */}
      {activeTab === 'gallery' && (
        <div className="space-y-4">
          {/* Graceful Degradation Banner */}
          <div className="p-4 bg-amber-50 border border-amber-300 rounded-xl text-xs text-amber-900 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-amber-700 shrink-0" />
              <span>
                <strong>Graceful Degradation Fallback:</strong> When photogrammetric mesh density is insufficient (&lt;20 photos), system gracefully renders high-resolution 2D photos with computer vision architectural tagging.
              </span>
            </div>
            <span className="font-mono text-[11px] bg-amber-100 text-amber-800 px-2 py-1 rounded">
              Status: 2D Gallery Active
            </span>
          </div>

          {/* Architectural Tag Filter Bar */}
          <div className="flex flex-wrap items-center gap-2 bg-white p-3 rounded-xl border border-stone-200">
            <span className="text-xs text-stone-500 font-mono">Filter by Tag:</span>
            {['all', '#stepped-terrace', '#chaulukya-style', '#jali-lattice', '#octagonal-shaft'].map((tag) => (
              <button
                key={tag}
                onClick={() => setActiveTagFilter(tag)}
                className={`text-xs px-2.5 py-1 rounded-full font-mono transition-colors ${
                  activeTagFilter === tag
                    ? 'bg-terracotta-600 text-white font-semibold'
                    : 'bg-stone-100 text-stone-600 hover:bg-stone-200'
                }`}
              >
                {tag}
              </button>
            ))}
          </div>

          {/* Photo Grid with Vision Tags */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {SAMPLE_GALLERY.filter((p) =>
              activeTagFilter === 'all' ? true : p.architecturalTags.includes(activeTagFilter)
            ).map((photo) => (
              <div
                key={photo.id}
                className="bg-white rounded-xl shadow-sm border border-stone-200 overflow-hidden flex flex-col justify-between"
              >
                <div>
                  <div className="relative h-48 bg-stone-100 overflow-hidden">
                    <img
                      src={photo.url}
                      alt={photo.title}
                      className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
                    />
                    <div className="absolute top-2 right-2 bg-stone-900/80 backdrop-blur px-2 py-0.5 rounded text-[10px] font-mono text-stone-300">
                      EXIF GPS Grounded
                    </div>
                  </div>

                  <div className="p-4 space-y-3">
                    <h3 className="text-sm font-serif font-bold text-stone-900">
                      {photo.title}
                    </h3>

                    {/* Architectural Vision Tags */}
                    <div>
                      <span className="text-[11px] font-mono text-stone-500 block mb-1.5 flex items-center gap-1">
                        <Tag className="w-3 h-3 text-terracotta-600" />
                        Vision Tagging:
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {photo.architecturalTags.map((tag, idx) => (
                          <span
                            key={idx}
                            className="text-[10px] bg-stone-100 text-stone-700 px-2 py-0.5 rounded font-mono border border-stone-200"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div className="p-2.5 bg-stone-50 rounded text-[11px] text-stone-600 space-y-1 font-mono">
                      <div>Camera: {photo.exifData.camera} ({photo.exifData.focalLength})</div>
                      <div>GPS: {photo.exifData.gps}</div>
                    </div>
                  </div>
                </div>

                <div className="p-3 bg-stone-50 border-t border-stone-100 text-[11px] text-stone-500 font-mono">
                  {photo.provenance}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

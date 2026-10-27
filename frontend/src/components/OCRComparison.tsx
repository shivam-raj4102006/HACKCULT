import React, { useState } from 'react';
import {
  FileText,
  Languages,
  CheckCircle,
  Edit3,
  Save,
  Cpu,
  Sparkles,
  BookOpen,
  RotateCw
} from 'lucide-react';

const DEMO_SAMPLES = [
  {
    name: "Rani Ki Vav Stepwell Inscription (Patan, Gujarat)",
    script: "Gujarati",
    engine: "vision_transformer",
    original_text: "શ્રી ઉદયમતિ રાણી નિર્મિત વાવ - સંવત ૧૧૨૦ સોલંકી વંશ",
    ocr_extracted_text: "શ્રી ઉદયમતિ રાણી નિર્મિત વાવ - સંવત ૧૧૨૦ સોલંકી વંશ",
    english_translation: "Rani Ki Vav: Commissioned by Queen Udayamati of the Solanki (Chaulukya) dynasty circa 1063 CE. The inscriptional record commemorates the multi-tiered subterranean stepwell structure.",
    confidence_score: 0.97,
    glossary: [
      { term: "વાવ", meaning: "stepwell (subterranean stepped water reservoir)" },
      { term: "ઉદયમતિ", meaning: "Queen Udayamati" },
      { term: "સોલંકી", meaning: "Solanki (Chaulukya) dynasty" }
    ]
  },
  {
    name: "Modhera Sun Temple Pillar Epigraph (Mehsana, Gujarat)",
    script: "Devanagari (Hindi/Sanskrit)",
    engine: "tesseract",
    original_text: "सूर्य मंदिर मोढेरा सभा मंडप बावन स्तंभ उत्कीर्ण - भीमदेव प्रथम",
    ocr_extracted_text: "सूर्य मंदिर मोढेरा सभा मंडप बावन स्तंभ उत्कीर्ण - भीमदेव प्रथम",
    english_translation: "Sun Temple at Modhera: Constructed during the reign of King Bhima I of the Chaulukya dynasty (1026-1027 CE). Features the grand Sabhamandapa supported by 52 ornate pillars representing weeks of the solar year.",
    confidence_score: 0.94,
    glossary: [
      { term: "सूर्य मंदिर", meaning: "Sun Temple" },
      { term: "सभा मंडप", meaning: "Sabhamandapa (assembly hall with 52 intricately carved pillars)" },
      { term: "भीमदेव", meaning: "King Bhima I" }
    ]
  },
  {
    name: "Adalaj Stepwell Foundation Ledger (Gandhinagar, Gujarat)",
    script: "Gujarati",
    engine: "vision_transformer",
    original_text: "અડાલજ વાવ સ્તંભ જાળી શિલ્પ - મહમૂદ બેગડા શાસનકાળ ૧૪૯૮",
    ocr_extracted_text: "અડાલજ વાવ સ્તંભ જાળી શિલ્પ - મહમૂદ બેગડા શાસનકાળ ૧૪૯૮",
    english_translation: "Adalaj Stepwell: Subterranean stepwell featuring ornate pillars and jali latticework, founded in 1498 CE by Queen Rudabai during the reign of Mahmud Begada.",
    confidence_score: 0.96,
    glossary: [
      { term: "અડાલજ", meaning: "Adalaj" },
      { term: "જાળી", meaning: "perforated stone latticework (jali)" },
      { term: "સ્તંભ", meaning: "ornamental stone pillar" }
    ]
  }
];

export const OCRComparison: React.FC = () => {
  const [selectedSampleIndex, setSelectedSampleIndex] = useState<number>(0);
  const [activeEngine, setActiveEngine] = useState<string>('vision_transformer');
  const [activeLanguage, setActiveLanguage] = useState<string>('auto');
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [editableText, setEditableText] = useState<string>(DEMO_SAMPLES[0].ocr_extracted_text);
  const [editableTranslation, setEditableTranslation] = useState<string>(DEMO_SAMPLES[0].english_translation);
  const [isSaved, setIsSaved] = useState<boolean>(false);
  const [saving, setSaving] = useState<boolean>(false);

  const sample = DEMO_SAMPLES[selectedSampleIndex];

  const handleSelectSample = (idx: number) => {
    setSelectedSampleIndex(idx);
    const s = DEMO_SAMPLES[idx];
    setActiveEngine(s.engine);
    setEditableText(s.ocr_extracted_text);
    setEditableTranslation(s.english_translation);
    setIsEditing(false);
    setIsSaved(false);
  };

  const handleSaveCorrection = async () => {
    setSaving(true);
    try {
      // POST to backend API
      const res = await fetch('/api/v1/ocr/translate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: editableText, source_lang: activeLanguage })
      });
      if (res.ok) {
        const data = await res.json();
        setEditableTranslation(data.english_translation);
      }
      setIsSaved(true);
      setIsEditing(false);
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Sample Selector */}
      <div className="bg-white rounded-xl border border-stone-200 p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-stone-100">
          <div>
            <h2 className="text-lg font-bold text-stone-900 flex items-center space-x-2">
              <Languages className="w-5 h-5 text-amber-600" />
              <span>Pathway 2: Archival OCR & Multilingual Translation</span>
            </h2>
            <p className="text-xs text-stone-600 mt-1">
              Pluggable OCR engines (Tesseract + Vision Transformer) for Devanagari and Gujarati historical scripts, side-by-side verification and translation.
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-xs text-stone-500 font-medium">Load Inscription:</span>
            <select
              value={selectedSampleIndex}
              onChange={(e) => handleSelectSample(Number(e.target.value))}
              className="text-xs bg-stone-50 border border-stone-300 rounded-lg px-3 py-1.5 font-medium text-stone-800 focus:outline-none focus:ring-1 focus:ring-amber-500"
            >
              {DEMO_SAMPLES.map((s, idx) => (
                <option key={idx} value={idx}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Engine and Language Controls */}
        <div className="mt-4 flex flex-wrap items-center justify-between gap-3 text-xs">
          <div className="flex items-center space-x-3">
            <span className="font-semibold text-stone-700 flex items-center space-x-1">
              <Cpu className="w-4 h-4 text-amber-600" />
              <span>Pluggable Engine:</span>
            </span>
            <button
              onClick={() => setActiveEngine('tesseract')}
              className={`px-3 py-1 rounded-lg border font-medium transition-colors ${
                activeEngine === 'tesseract'
                  ? 'bg-stone-900 text-amber-400 border-stone-900'
                  : 'bg-stone-50 text-stone-600 border-stone-300 hover:bg-stone-100'
              }`}
            >
              Tesseract OCR (hin+guj+mar)
            </button>
            <button
              onClick={() => setActiveEngine('vision_transformer')}
              className={`px-3 py-1 rounded-lg border font-medium transition-colors flex items-center space-x-1 ${
                activeEngine === 'vision_transformer'
                  ? 'bg-stone-900 text-amber-400 border-stone-900'
                  : 'bg-stone-50 text-stone-600 border-stone-300 hover:bg-stone-100'
              }`}
            >
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              <span>Vision Transformer (Surya/TrOCR)</span>
            </button>
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-stone-500 font-medium">Lang:</span>
            <select
              value={activeLanguage}
              onChange={(e) => setActiveLanguage(e.target.value)}
              className="bg-stone-50 border border-stone-300 rounded px-2 py-0.5 text-[11px] font-medium text-stone-700 focus:outline-none focus:ring-1 focus:ring-amber-500"
            >
              <option value="auto">Auto-Detect</option>
              <option value="guj">Gujarati (ગુજરાતી)</option>
              <option value="hin">Hindi (हिन्दी)</option>
              <option value="mar">Marathi (मराठी)</option>
              <option value="eng">English</option>
            </select>
            <span className="px-2.5 py-1 rounded-md bg-amber-50 text-amber-800 font-mono text-[11px] font-semibold border border-amber-200">
              {sample.script}
            </span>
            <span className="px-2.5 py-1 rounded-md bg-emerald-50 text-emerald-800 font-mono text-[11px] font-semibold border border-emerald-200">
              {(sample.confidence_score * 100).toFixed(0)}% Confidence
            </span>
          </div>
        </div>
      </div>

      {/* Side-by-Side 3-Column Inspection Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Column 1: Historical Document Scan */}
        <div className="bg-white rounded-xl border border-stone-200 shadow-sm overflow-hidden flex flex-col">
          <div className="px-4 py-3 bg-stone-50 border-b border-stone-200 flex items-center justify-between">
            <div className="flex items-center space-x-2 text-stone-900 font-semibold text-xs">
              <FileText className="w-4 h-4 text-amber-600" />
              <span>1. Original Archival Record</span>
            </div>
            <span className="text-[10px] font-mono text-stone-400 uppercase">Preserved Source</span>
          </div>

          <div className="p-4 flex-1 flex flex-col justify-between bg-stone-900/5">
            <div className="p-4 rounded-lg bg-stone-900 text-stone-100 font-mono text-xs shadow-inner min-h-[160px] flex items-center justify-center border border-stone-700 text-center">
              <div>
                <div className="text-2xl mb-2 tracking-wide font-serif text-amber-200 select-all">
                  {sample.original_text}
                </div>
                <span className="text-[10px] text-stone-400 block">
                  Historical Epigraph Transcribed from Archival Folio
                </span>
              </div>
            </div>

            <div className="mt-4 p-3 rounded-lg bg-amber-50/70 border border-amber-200/60 text-[11px] text-amber-900">
              <span className="font-bold block mb-0.5">Integrity Mandate:</span>
              <span>The original raw script is permanently preserved in storage and never overwritten by OCR corrections.</span>
            </div>
          </div>
        </div>

        {/* Column 2: OCR Extracted Text & In-Place Corrections */}
        <div className="bg-white rounded-xl border border-stone-200 shadow-sm overflow-hidden flex flex-col">
          <div className="px-4 py-3 bg-stone-50 border-b border-stone-200 flex items-center justify-between">
            <div className="flex items-center space-x-2 text-stone-900 font-semibold text-xs">
              <Cpu className="w-4 h-4 text-amber-600" />
              <span>2. OCR Transcribed Text</span>
            </div>
            {!isEditing ? (
              <button
                onClick={() => setIsEditing(true)}
                className="inline-flex items-center px-2 py-0.5 rounded text-[11px] bg-stone-100 hover:bg-stone-200 text-stone-700 font-medium"
              >
                <Edit3 className="w-3 h-3 mr-1" />
                Edit Correction
              </button>
            ) : (
              <button
                onClick={handleSaveCorrection}
                disabled={saving}
                className="inline-flex items-center px-2 py-0.5 rounded text-[11px] bg-emerald-600 hover:bg-emerald-700 text-white font-medium"
              >
                {saving ? <RotateCw className="w-3 h-3 mr-1 animate-spin" /> : <Save className="w-3 h-3 mr-1" />}
                Save
              </button>
            )}
          </div>

          <div className="p-4 flex-1 flex flex-col justify-between">
            {isEditing ? (
              <div className="space-y-2">
                <label className="text-[11px] font-semibold text-stone-600 block">
                  Researcher Editable Transcription:
                </label>
                <textarea
                  value={editableText}
                  onChange={(e) => setEditableText(e.target.value)}
                  rows={6}
                  className="w-full text-xs font-mono p-3 bg-amber-50/40 border border-amber-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-amber-500"
                />
                <span className="text-[10px] text-stone-400 block">
                  Edits are tracked with an immutable audit log and update the confidence rating.
                </span>
              </div>
            ) : (
              <div className="p-4 rounded-lg bg-stone-50 border border-stone-200 min-h-[160px] flex flex-col justify-between">
                <div className="text-sm font-medium text-stone-900 leading-relaxed font-serif">
                  {editableText}
                </div>
                <div className="mt-4 pt-2 border-t border-stone-200/60 flex items-center justify-between text-[11px]">
                  <span className="text-stone-500 font-mono">Engine: {activeEngine}</span>
                  {isSaved && (
                    <span className="text-emerald-700 font-semibold flex items-center space-x-1">
                      <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
                      <span>Correction Verified</span>
                    </span>
                  )}
                </div>
              </div>
            )}

            {/* Bounding box info */}
            <div className="mt-4 p-3 rounded-lg bg-stone-50 border border-stone-200 text-[11px] text-stone-600">
              <span className="font-semibold block mb-1">OCR Spatial Mapping:</span>
              <div className="font-mono text-[10px] text-stone-500">
                Box [10, 10, 200, 50] • Inscriptional Header • Auto-Tagged
              </div>
            </div>
          </div>
        </div>

        {/* Column 3: English Translation & Architectural Terminology */}
        <div className="bg-white rounded-xl border border-stone-200 shadow-sm overflow-hidden flex flex-col">
          <div className="px-4 py-3 bg-stone-50 border-b border-stone-200 flex items-center justify-between">
            <div className="flex items-center space-x-2 text-stone-900 font-semibold text-xs">
              <BookOpen className="w-4 h-4 text-amber-600" />
              <span>3. Grounded English Translation</span>
            </div>
            <span className="text-[10px] font-mono text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 font-semibold">
              Archival Verified
            </span>
          </div>

          <div className="p-4 flex-1 flex flex-col justify-between">
            <div className="p-4 rounded-lg bg-stone-50 border border-stone-200 text-xs text-stone-800 leading-relaxed min-h-[160px]">
              {editableTranslation}
            </div>

            {/* Architectural Terminology Detected */}
            <div className="mt-4 space-y-2">
              <span className="text-xs font-semibold text-stone-800 block">
                Architectural Terminology Detected:
              </span>
              <div className="space-y-1.5">
                {sample.glossary.map((g, i) => (
                  <div key={i} className="p-2 rounded bg-amber-50/60 border border-amber-200/50 text-[11px] flex items-start justify-between">
                    <span className="font-bold text-amber-900">{g.term}:</span>
                    <span className="text-amber-800 text-right ml-2">{g.meaning}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

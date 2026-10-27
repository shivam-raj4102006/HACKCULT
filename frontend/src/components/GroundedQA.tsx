import React, { useState } from 'react';
import { Search, ShieldAlert, CheckCircle2, AlertCircle, BookOpen, Sparkles, Filter } from 'lucide-react';

interface Citation {
  document_id: string;
  document_name: string;
  page_or_slide_number: number;
  snippet: string;
  verification_status: string;
  relevance_score: number;
}

interface QAResponse {
  query: string;
  status: 'GROUNDED_ANSWER' | 'INSUFFICIENT_EVIDENCE';
  answer: string;
  confidence_score: number;
  citations: Citation[];
  message: string;
}

export const GroundedQA: React.FC = () => {
  const [query, setQuery] = useState('');
  const [onlyVerified, setOnlyVerified] = useState(false);
  const [loading, setLoading] = useState(false);
  const [qaResult, setQaResult] = useState<QAResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const suggestedQueries = [
    "Who commissioned Rani Ki Vav in Patan?",
    "What are the architectural terrace levels of Rani Ki Vav?",
    "Who constructed the Sun Temple at Modhera?",
    "Who built the Eiffel Tower iron trusses in 1889?"
  ];

  const handleAsk = async (textToAsk?: string) => {
    const q = textToAsk || query;
    if (!q.trim()) return;
    if (textToAsk) setQuery(textToAsk);

    setLoading(true);
    setError(null);

    try {
      const res = await fetch('/api/v1/search/qa', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: q,
          only_verified: onlyVerified
        })
      });

      if (!res.ok) {
        throw new Error(`Server returned ${res.status}`);
      }

      const data: QAResponse = await res.json();
      setQaResult(data);
    } catch (err: any) {
      setError(err.message || 'Failed to query RAG engine');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-stone-200 p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
          <div>
            <h2 className="text-xl font-serif font-bold text-stone-900 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-terracotta-600" />
              Evidence-Grounded Search & Natural-Language Q&A
            </h2>
            <p className="text-sm text-stone-600">
              Strictly grounded in ingested archival records with page-level citations. Refuses to hallucinate when evidence is absent.
            </p>
          </div>
          <div className="flex items-center gap-2 bg-stone-50 border border-stone-200 px-3 py-1.5 rounded-lg text-xs font-medium text-stone-700">
            <Filter className="w-3.5 h-3.5 text-stone-500" />
            <label className="flex items-center gap-1.5 cursor-pointer">
              <input
                type="checkbox"
                checked={onlyVerified}
                onChange={(e) => setOnlyVerified(e.target.checked)}
                className="rounded border-stone-300 text-terracotta-600 focus:ring-terracotta-500"
              />
              <span>Verified Claims Only</span>
            </label>
          </div>
        </div>

        {/* Search Bar */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleAsk();
          }}
          className="flex gap-2"
        >
          <div className="relative flex-1">
            <Search className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-stone-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask an archival question (e.g. 'Who commissioned Rani Ki Vav in Patan?')..."
              className="w-full pl-10 pr-4 py-3 rounded-lg border border-stone-300 focus:outline-none focus:ring-2 focus:ring-terracotta-500 text-stone-900 bg-white"
            />
          </div>
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="px-6 py-3 bg-terracotta-600 hover:bg-terracotta-700 disabled:opacity-50 text-white font-medium rounded-lg transition-colors flex items-center gap-2 shadow-sm"
          >
            {loading ? 'Synthesizing...' : 'Search & Answer'}
          </button>
        </form>

        {/* Suggested Queries */}
        <div className="mt-4 flex flex-wrap items-center gap-2">
          <span className="text-xs text-stone-500 font-medium">Suggested queries:</span>
          {suggestedQueries.map((sq, idx) => (
            <button
              key={idx}
              onClick={() => handleAsk(sq)}
              className="text-xs bg-stone-100 hover:bg-stone-200 text-stone-700 px-2.5 py-1 rounded-full transition-colors border border-stone-200"
            >
              {sq}
            </button>
          ))}
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Result Display */}
      {qaResult && (
        <div className="space-y-6">
          {qaResult.status === 'GROUNDED_ANSWER' ? (
            <div className="bg-white rounded-xl shadow-sm border border-stone-200 p-6 space-y-6">
              {/* Answer Card */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Grounded Archival Answer
                  </span>
                  <span className="text-xs font-mono text-stone-500">
                    Confidence: {(qaResult.confidence_score * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="p-4 bg-stone-50 rounded-lg border border-stone-200">
                  <p className="text-base text-stone-900 leading-relaxed font-sans">
                    {qaResult.answer}
                  </p>
                </div>
              </div>

              {/* Citations */}
              <div>
                <h3 className="text-sm font-semibold uppercase tracking-wider text-stone-600 mb-3 flex items-center gap-2">
                  <BookOpen className="w-4 h-4 text-terracotta-600" />
                  Primary Archival Citations ({qaResult.citations.length})
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {qaResult.citations.map((c, idx) => (
                    <div
                      key={idx}
                      className="p-4 rounded-lg border border-stone-200 bg-white hover:border-terracotta-300 transition-all flex flex-col justify-between"
                    >
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="font-semibold text-xs text-stone-800 truncate" title={c.document_name}>
                            {c.document_name}
                          </span>
                          <span className="text-[11px] bg-stone-100 text-stone-600 font-mono px-2 py-0.5 rounded">
                            Page / Slide {c.page_or_slide_number}
                          </span>
                        </div>
                        <p className="text-xs text-stone-600 italic bg-stone-50 p-2.5 rounded border border-stone-100">
                          "{c.snippet}"
                        </p>
                      </div>
                      <div className="mt-3 pt-2 border-t border-stone-100 flex items-center justify-between text-[11px]">
                        <span
                          className={`px-2 py-0.5 rounded-full font-medium ${
                            c.verification_status === 'verified'
                              ? 'bg-emerald-100 text-emerald-700'
                              : 'bg-amber-100 text-amber-700'
                          }`}
                        >
                          {c.verification_status.toUpperCase()}
                        </span>
                        <span className="text-stone-400 font-mono">
                          Relevance: {(c.relevance_score * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            /* Insufficient Evidence Fallback */
            <div className="bg-amber-50 rounded-xl border border-amber-300 p-6 shadow-sm">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-amber-100 text-amber-800 rounded-lg shrink-0">
                  <ShieldAlert className="w-6 h-6" />
                </div>
                <div className="space-y-2">
                  <h3 className="text-base font-semibold text-amber-900">
                    HeritageProof Archival Integrity: Insufficient Evidence
                  </h3>
                  <p className="text-sm text-amber-800 leading-relaxed">
                    {qaResult.answer}
                  </p>
                  <div className="pt-2">
                    <p className="text-xs text-amber-700">
                      Query: <span className="font-mono font-medium">"{qaResult.query}"</span>
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

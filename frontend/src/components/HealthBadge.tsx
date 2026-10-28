import React, { useEffect, useState } from 'react';
import { Sparkles, CheckCircle2, Info } from 'lucide-react';
import { checkHealth, HealthData } from '../services/api';

export const HealthBadge: React.FC = () => {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [showInfo, setShowInfo] = useState<boolean>(false);

  const fetchStatus = async () => {
    try {
      const data = await checkHealth();
      setHealth(data);
    } catch {
      setHealth({
        status: 'demo_mode',
        version: '1.0.0',
        environment: 'demo',
        database_status: 'embedded_canonical',
        timestamp: new Date().toISOString(),
        demo_mode: true
      });
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const isDemo = !health || health.demo_mode || health.status !== 'healthy';

  if (isDemo) {
    return (
      <div className="relative">
        <div
          onClick={() => setShowInfo(!showInfo)}
          className="cursor-pointer inline-flex items-center space-x-2 text-xs bg-stone-900/90 text-stone-200 px-3.5 py-1.5 rounded-full border border-stone-700 shadow-sm backdrop-blur hover:border-amber-500/50 transition-colors"
          title="Click to view Demo Mode architecture details"
        >
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="font-semibold text-stone-100">Frontend Online</span>
          <span className="text-stone-500 font-mono">•</span>
          <span className="font-mono text-amber-400 bg-amber-950/80 px-2 py-0.5 rounded text-[10px] border border-amber-600/30">
            Demo Mode
          </span>
          <Info className="w-3.5 h-3.5 text-stone-400 ml-1" />
        </div>

        {showInfo && (
          <div className="absolute right-0 mt-2 w-80 bg-stone-900 border border-stone-700 text-stone-200 p-4 rounded-xl shadow-xl z-50 text-xs">
            <div className="flex items-center justify-between pb-2 mb-2 border-b border-stone-800">
              <span className="font-bold text-amber-400 flex items-center gap-1.5">
                <Sparkles className="w-4 h-4 text-amber-400" />
                HeritageProof Demo Mode
              </span>
              <button
                onClick={() => setShowInfo(false)}
                className="text-stone-400 hover:text-white"
              >
                ✕
              </button>
            </div>
            <p className="text-stone-300 leading-relaxed">
              This interactive demonstration showcase features verified medieval Gujarat archival data (Rani Ki Vav, Modhera Sun Temple, Adalaj Stepwell), interactive Three.js 3D spatial models, and grounded citation Q&A without requiring a live backend cluster.
            </p>
            <div className="mt-3 pt-2 border-t border-stone-800 flex items-center justify-between text-[10px] font-mono text-stone-400">
              <span>Status: Online</span>
              <span>Build: v1.0 Production</span>
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="inline-flex items-center space-x-3 text-xs bg-stone-900/90 text-stone-200 px-4 py-2 rounded-xl border border-stone-700 shadow-sm backdrop-blur">
      <div className="flex items-center space-x-1.5">
        <CheckCircle2 className="w-4 h-4 text-emerald-400" />
        <span className="font-medium text-emerald-400">Backend API: {health.status}</span>
      </div>
      <span className="text-stone-600">•</span>
      <div>
        <span className="text-stone-400">DB:</span>{' '}
        <span className="font-mono text-stone-300">{health.database_status}</span>
      </div>
      <span className="text-stone-600">•</span>
      <div>
        <span className="text-stone-400">v{health.version}</span>
      </div>
    </div>
  );
};

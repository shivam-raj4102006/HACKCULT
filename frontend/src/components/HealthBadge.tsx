import React, { useEffect, useState } from 'react';
import { CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react';
import { checkHealth, HealthData } from '../services/api';

export const HealthBadge: React.FC = () => {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await checkHealth();
      setHealth(data);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Backend unreachable';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading && !health) {
    return (
      <div className="inline-flex items-center space-x-2 text-xs bg-stone-100 text-stone-600 px-3 py-1.5 rounded-full border border-stone-200">
        <RefreshCw className="w-3.5 h-3.5 animate-spin" />
        <span>Connecting to HeritageProof Core...</span>
      </div>
    );
  }

  if (error || !health) {
    return (
      <div className="inline-flex items-center space-x-2 text-xs bg-red-50 text-red-700 px-3 py-1.5 rounded-full border border-red-200">
        <AlertCircle className="w-3.5 h-3.5 text-red-500" />
        <span>Core Offline ({error || 'Unknown error'})</span>
        <button
          onClick={fetchStatus}
          className="ml-2 hover:underline font-semibold"
          title="Retry connection"
        >
          Retry
        </button>
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
        <span className="text-stone-400">Env:</span>{' '}
        <span className="font-mono text-amber-300">{health.environment}</span>
      </div>
      <span className="text-stone-600">•</span>
      <div>
        <span className="text-stone-400">v{health.version}</span>
      </div>
    </div>
  );
};

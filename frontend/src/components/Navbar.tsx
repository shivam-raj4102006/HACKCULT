import React from 'react';
import { Shield, BookOpen, MapPin, Database, Box, Languages } from 'lucide-react';

interface NavbarProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  activeRole: string;
  onChangeRole: (role: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentTab,
  onSelectTab,
  activeRole,
  onChangeRole,
}) => {
  return (
    <header className="bg-stone-900 text-stone-100 border-b border-stone-800 sticky top-0 z-50 shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-lg bg-amber-600 flex items-center justify-center text-white shadow-inner">
              <Shield className="w-6 h-6" />
            </div>
            <div>
              <span className="text-xl font-bold tracking-tight text-white">HeritageProof</span>
              <span className="ml-2 text-xs font-mono uppercase bg-stone-800 text-amber-400 px-2 py-0.5 rounded border border-amber-500/30">
                Core v1.0
              </span>
            </div>
          </div>

          <nav className="flex space-x-1">
            <button
              onClick={() => onSelectTab('overview')}
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                currentTab === 'overview'
                  ? 'bg-stone-800 text-amber-400 border border-stone-700'
                  : 'text-stone-300 hover:bg-stone-800/60 hover:text-white'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => onSelectTab('ingestion')}
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center space-x-1.5 ${
                currentTab === 'ingestion'
                  ? 'bg-stone-800 text-amber-400 border border-stone-700'
                  : 'text-stone-300 hover:bg-stone-800/60 hover:text-white'
              }`}
            >
              <Database className="w-4 h-4" />
              <span>Ingestion</span>
            </button>
            <button
              onClick={() => onSelectTab('ocr')}
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center space-x-1.5 ${
                currentTab === 'ocr'
                  ? 'bg-stone-800 text-amber-400 border border-stone-700'
                  : 'text-stone-300 hover:bg-stone-800/60 hover:text-white'
              }`}
            >
              <Languages className="w-4 h-4" />
              <span>OCR & Translation</span>
            </button>
            <button
              onClick={() => onSelectTab('verification')}
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center space-x-1.5 ${
                currentTab === 'verification'
                  ? 'bg-stone-800 text-amber-400 border border-stone-700'
                  : 'text-stone-300 hover:bg-stone-800/60 hover:text-white'
              }`}
            >
              <Shield className="w-4 h-4" />
              <span>Verification</span>
            </button>
            <button
              onClick={() => onSelectTab('search')}
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center space-x-1.5 ${
                currentTab === 'search'
                  ? 'bg-stone-800 text-amber-400 border border-stone-700'
                  : 'text-stone-300 hover:bg-stone-800/60 hover:text-white'
              }`}
            >
              <BookOpen className="w-4 h-4" />
              <span>Grounded Q&A</span>
            </button>
            <button
              onClick={() => onSelectTab('map')}
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center space-x-1.5 ${
                currentTab === 'map'
                  ? 'bg-stone-800 text-amber-400 border border-stone-700'
                  : 'text-stone-300 hover:bg-stone-800/60 hover:text-white'
              }`}
            >
              <MapPin className="w-4 h-4" />
              <span>Heritage Map</span>
            </button>
            <button
              onClick={() => onSelectTab('viewer3d')}
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center space-x-1.5 ${
                currentTab === 'viewer3d'
                  ? 'bg-stone-800 text-amber-400 border border-stone-700'
                  : 'text-stone-300 hover:bg-stone-800/60 hover:text-white'
              }`}
            >
              <Box className="w-4 h-4" />
              <span>3D Artifacts</span>
            </button>
          </nav>

          <div className="flex items-center space-x-3">
            <span className="text-xs text-stone-400 font-mono">Role:</span>
            <select
              value={activeRole}
              onChange={(e) => onChangeRole(e.target.value)}
              className="bg-stone-800 text-xs text-amber-300 border border-stone-700 rounded px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-amber-500"
            >
              <option value="verifier">Verifier (Human Review)</option>
              <option value="researcher">Researcher</option>
              <option value="admin">Administrator</option>
              <option value="public">Public</option>
            </select>
          </div>
        </div>
      </div>
    </header>
  );
};

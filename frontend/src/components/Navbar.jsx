import React from 'react';
import { ShieldAlert, Activity, Users, Radio, AlertTriangle } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab }) {
  return (
    <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-50 px-6 py-3 flex items-center justify-between">
      <div className="flex items-center space-x-3">
        <div className="bg-red-500/10 border border-red-500/30 p-2 rounded-lg text-red-500">
          <ShieldAlert className="w-6 h-6" />
        </div>
        <div>
          <h1 className="font-bold text-base md:text-lg text-slate-100 leading-tight">
            AI/ML Mine Safety & Evacuation
          </h1>
          <p className="text-xs text-slate-400">
            Unified Geotechnical & Atmospheric Hazard Monitoring
          </p>
        </div>
      </div>

      {/* Tabs */}
      <nav className="flex items-center space-x-2">
        <button
          onClick={() => setActiveTab('overview')}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
            activeTab === 'overview'
              ? 'bg-blue-600 text-white'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
          }`}
        >
          Overview
        </button>
        <button
          onClick={() => setActiveTab('open_pit')}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
            activeTab === 'open_pit'
              ? 'bg-blue-600 text-white'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
          }`}
        >
          Open-Pit
        </button>
        <button
          onClick={() => setActiveTab('underground')}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
            activeTab === 'underground'
              ? 'bg-blue-600 text-white'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
          }`}
        >
          Underground
        </button>
      </nav>

      {/* Real-Time Status Pill */}
      <div className="hidden sm:flex items-center space-x-2 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 px-3 py-1 rounded-full text-xs font-medium">
        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
        <span>Telemetry Stream Active</span>
      </div>
    </header>
  );
}

import React, { useState } from 'react';
import {
  Menu,
  RefreshCw,
} from 'lucide-react';
import SimulationControls from './SimulationControls';

const VIEW_TITLES = {
  overview: { title: 'Command Center Overview', subtitle: 'Real-time mine geotechnical and atmospheric status' },
  open_pit: { title: 'Open-Pit Mining Module', subtitle: 'Slope movement, rockfall detection & rainfall monitoring' },
  underground: { title: 'Underground Mining Module', subtitle: 'Toxic gas concentrations, fire hazard & ventilation airflow' },
  sensors: { title: 'Live Sensor Telemetry', subtitle: 'Multi-parameter high-frequency sensor readings & thresholds' },
  workers: { title: 'Worker Monitoring & Geofencing', subtitle: 'Active shift personnel, coordinates & safety zones' },
  alerts: { title: 'Emergency Response & Evacuation', subtitle: 'Critical hazard alerts, targeted dispatch & evacuation tallies' },
  analytics: { title: 'Historical Analytics & Trends', subtitle: 'Longitudinal sensor dynamics and incident statistics' },
  settings: { title: 'System Configuration', subtitle: 'API parameters, simulation engine & safety thresholds' },
};

export default function Header({
  currentView,
  setIsMobileOpen,
  isConnected,
  onRefresh,
}) {
  const meta = VIEW_TITLES[currentView] || { title: 'Dashboard', subtitle: '' };

  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-30 px-4 md:px-6 flex items-center justify-between">
      {/* Left: Mobile Toggle & Page Title */}
      <div className="flex items-center space-x-3">
        <button
          onClick={() => setIsMobileOpen(true)}
          className="lg:hidden p-2 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div>
          <h2 className="text-sm md:text-base font-bold text-slate-100 leading-tight">
            {meta.title}
          </h2>
          <p className="text-[11px] text-slate-400 hidden sm:block">
            {meta.subtitle}
          </p>
        </div>
      </div>

      {/* Right: Comprehensive Simulation Controls & Connection Status */}
      <div className="flex items-center space-x-2 md:space-x-3">
        {/* Full-Featured Simulation Control Bar */}
        <div className="hidden md:block">
          <SimulationControls onActionComplete={onRefresh} />
        </div>

        {/* Refresh Button */}
        <button
          onClick={onRefresh}
          className="p-2 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition"
          title="Refresh Dashboard Data"
        >
          <RefreshCw className="w-4 h-4" />
        </button>

        {/* WebSocket Connection Indicator */}
        <div
          className={`flex items-center space-x-2 px-3 py-1.5 rounded-full text-[11px] font-medium border ${
            isConnected
              ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
              : 'bg-red-500/10 border-red-500/30 text-red-400'
          }`}
        >
          <span
            className={`w-2 h-2 rounded-full ${
              isConnected ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'
            }`}
          />
          <span className="hidden sm:inline">
            {isConnected ? 'Live WS Connected' : 'Reconnecting...'}
          </span>
        </div>
      </div>
    </header>
  );
}

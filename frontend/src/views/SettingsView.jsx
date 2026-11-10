import React, { useState } from 'react';
import {
  Settings,
  Server,
  Radio,
  Sliders,
  ShieldAlert,
  CheckCircle2,
  RefreshCw,
  Info,
  ExternalLink,
} from 'lucide-react';
import { getHealth } from '../services/api';

export default function SettingsView({ isConnected }) {
  const [healthStatus, setHealthStatus] = useState(null);
  const [isChecking, setIsChecking] = useState(false);

  const checkBackendHealth = async () => {
    setIsChecking(true);
    try {
      const data = await getHealth();
      setHealthStatus(data);
    } catch (err) {
      setHealthStatus({ status: 'unreachable', error: err.message });
    } finally {
      setIsChecking(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl">
      {/* Top Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl">
        <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
          <Settings className="w-5 h-5 text-blue-400" />
          <span>System Settings & Architecture Diagnostics</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Network endpoints, statutory threshold matrices, and prototype architecture specifications
        </p>
      </div>

      {/* Backend & WebSocket Diagnostics */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
        <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center justify-between">
          <span className="flex items-center gap-2">
            <Server className="w-4 h-4 text-emerald-400" />
            <span>Backend API & Telemetry Channel</span>
          </span>
          <button
            onClick={checkBackendHealth}
            disabled={isChecking}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-xl transition flex items-center gap-1.5"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isChecking ? 'animate-spin' : ''}`} />
            <span>Test Health Endpoint</span>
          </button>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
          <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800">
            <span className="text-slate-500 block text-[10px] uppercase font-sans">REST API Gateway</span>
            <span className="text-slate-200 font-bold">http://localhost:8000</span>
            <div className="mt-2 text-[11px] text-slate-400 font-sans flex items-center gap-1">
              <span>Swagger UI: </span>
              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noreferrer"
                className="text-blue-400 hover:underline flex items-center gap-0.5"
              >
                /docs <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>

          <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800">
            <span className="text-slate-500 block text-[10px] uppercase font-sans">WebSocket Telemetry Stream</span>
            <span className="text-slate-200 font-bold">ws://localhost:8000/ws/telemetry</span>
            <div className="mt-2 text-[11px] font-sans flex items-center gap-1.5">
              <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'}`} />
              <span className={isConnected ? 'text-emerald-400' : 'text-red-400'}>
                {isConnected ? 'Connection Active (Full-Duplex)' : 'Disconnected'}
              </span>
            </div>
          </div>
        </div>

        {healthStatus && (
          <div className="bg-slate-950/80 border border-slate-800 p-3.5 rounded-xl text-xs font-mono text-slate-300">
            <div className="font-sans font-bold text-slate-200 mb-1">Health Response:</div>
            <pre className="text-[11px] text-emerald-400">{JSON.stringify(healthStatus, null, 2)}</pre>
          </div>
        )}
      </div>

      {/* Statutory Safety Thresholds Reference */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
        <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
          <Sliders className="w-4 h-4 text-amber-400" />
          <span>Statutory Safety Thresholds Matrix</span>
        </h3>
        <p className="text-xs text-slate-400">
          Industrial mining standards (DGMS / USBM / OSHA) utilized by the centralized risk engine:
        </p>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 text-slate-400 text-[10px] uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-4 py-2.5">Hazard Parameter</th>
                <th className="px-4 py-2.5">Sector</th>
                <th className="px-4 py-2.5">Safe Baseline</th>
                <th className="px-4 py-2.5">Warning (Level 3-4)</th>
                <th className="px-4 py-2.5">Critical Evacuation (Level 5)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
              <tr>
                <td className="px-4 py-2 text-slate-200 font-sans font-medium">Methane (CH4)</td>
                <td className="px-4 py-2 text-slate-400 font-sans">Underground</td>
                <td className="px-4 py-2 text-emerald-400">&lt; 0.50 %</td>
                <td className="px-4 py-2 text-amber-400">0.80 - 1.20 %</td>
                <td className="px-4 py-2 text-red-400 font-bold">&ge; 1.25 % (Mandatory Stop)</td>
              </tr>
              <tr>
                <td className="px-4 py-2 text-slate-200 font-sans font-medium">Carbon Monoxide (CO)</td>
                <td className="px-4 py-2 text-slate-400 font-sans">Underground</td>
                <td className="px-4 py-2 text-emerald-400">&lt; 10.0 ppm</td>
                <td className="px-4 py-2 text-amber-400">25.0 - 45.0 ppm</td>
                <td className="px-4 py-2 text-red-400 font-bold">&ge; 50.0 ppm</td>
              </tr>
              <tr>
                <td className="px-4 py-2 text-slate-200 font-sans font-medium">Oxygen (O2)</td>
                <td className="px-4 py-2 text-slate-400 font-sans">Underground</td>
                <td className="px-4 py-2 text-emerald-400">20.8 - 20.9 %</td>
                <td className="px-4 py-2 text-amber-400">18.0 - 19.4 %</td>
                <td className="px-4 py-2 text-red-400 font-bold">&le; 17.0 % (Asphyxiation)</td>
              </tr>
              <tr>
                <td className="px-4 py-2 text-slate-200 font-sans font-medium">Slope Crack Movement</td>
                <td className="px-4 py-2 text-slate-400 font-sans">Open-Pit</td>
                <td className="px-4 py-2 text-emerald-400">&lt; 1.0 mm</td>
                <td className="px-4 py-2 text-amber-400">5.0 - 10.0 mm</td>
                <td className="px-4 py-2 text-red-400 font-bold">&ge; 12.0 mm (Wall Failure)</td>
              </tr>
              <tr>
                <td className="px-4 py-2 text-slate-200 font-sans font-medium">Vibration PPV</td>
                <td className="px-4 py-2 text-slate-400 font-sans">Open-Pit</td>
                <td className="px-4 py-2 text-emerald-400">&lt; 5.0 mm/s</td>
                <td className="px-4 py-2 text-amber-400">15.0 - 22.0 mm/s</td>
                <td className="px-4 py-2 text-red-400 font-bold">&ge; 25.0 mm/s</td>
              </tr>
              <tr>
                <td className="px-4 py-2 text-slate-200 font-sans font-medium">Precipitation Rate</td>
                <td className="px-4 py-2 text-slate-400 font-sans">Open-Pit</td>
                <td className="px-4 py-2 text-emerald-400">&lt; 10.0 mm/h</td>
                <td className="px-4 py-2 text-amber-400">25.0 - 50.0 mm/h</td>
                <td className="px-4 py-2 text-red-400 font-bold">&ge; 55.0 mm/h</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Academic Prototype Notice */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl text-xs text-slate-400 space-y-2">
        <div className="flex items-center gap-2 text-slate-200 font-bold">
          <Info className="w-4 h-4 text-blue-400" />
          <span>Project Information & Academic Scope</span>
        </div>
        <p>
          This dashboard forms the presentation and management interface for the research project titled
          <strong> "AI/ML-Powered Mining Safety and Worker Evacuation System"</strong>.
          It integrates simulated high-frequency multi-sensor streams, dual-engine risk modeling, spatial ray-casting
          geofencing, and targeted two-way worker emergency evacuation routing.
        </p>
      </div>
    </div>
  );
}

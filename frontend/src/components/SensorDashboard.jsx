import React from 'react';
import { CloudRain, Activity, Move, Flame, Wind, Gauge } from 'lucide-react';

export default function SensorDashboard({ activeTab }) {
  // Telemetry cards layout
  return (
    <div>
      <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center justify-between">
        <span>Live Sensor Telemetry & Hazards</span>
        <span className="text-xs text-slate-500">Sampling Rate: 2.0s</span>
      </h3>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {/* Open-Pit: Rainfall */}
        <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-3">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-medium">Rainfall</span>
            <CloudRain className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-lg font-bold text-slate-100">2.4 <span className="text-xs text-slate-400 font-normal">mm/h</span></div>
          <p className="text-[10px] text-emerald-400 mt-1">Normal Rate</p>
        </div>

        {/* Open-Pit: Ground Vibration */}
        <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-3">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-medium">Vibration (PPV)</span>
            <Activity className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-lg font-bold text-slate-100">0.8 <span className="text-xs text-slate-400 font-normal">mm/s</span></div>
          <p className="text-[10px] text-emerald-400 mt-1">Safe Baseline</p>
        </div>

        {/* Open-Pit: Slope Displacement */}
        <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-3">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-medium">Slope Crack</span>
            <Move className="w-4 h-4 text-yellow-400" />
          </div>
          <div className="text-lg font-bold text-slate-100">0.12 <span className="text-xs text-slate-400 font-normal">mm</span></div>
          <p className="text-[10px] text-emerald-400 mt-1">Stable</p>
        </div>

        {/* Underground: CH4 Methane */}
        <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-3">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-medium">Methane (CH4)</span>
            <Flame className="w-4 h-4 text-orange-400" />
          </div>
          <div className="text-lg font-bold text-slate-100">0.18 <span className="text-xs text-slate-400 font-normal">%</span></div>
          <p className="text-[10px] text-emerald-400 mt-1">Threshold: &lt; 1.25%</p>
        </div>

        {/* Underground: CO Carbon Monoxide */}
        <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-3">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-medium">Carbon Monoxide</span>
            <Gauge className="w-4 h-4 text-red-400" />
          </div>
          <div className="text-lg font-bold text-slate-100">8.5 <span className="text-xs text-slate-400 font-normal">ppm</span></div>
          <p className="text-[10px] text-emerald-400 mt-1">Threshold: &lt; 50 ppm</p>
        </div>

        {/* Underground: Ventilation Velocity */}
        <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-3">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-medium">Air Velocity</span>
            <Wind className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-lg font-bold text-slate-100">1.8 <span className="text-xs text-slate-400 font-normal">m/s</span></div>
          <p className="text-[10px] text-emerald-400 mt-1">Airflow Optimal</p>
        </div>
      </div>
    </div>
  );
}

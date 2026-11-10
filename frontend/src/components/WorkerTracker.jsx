import React from 'react';
import { Users, UserCheck, AlertCircle, HardHat } from 'lucide-react';

export default function WorkerTracker() {
  const sampleWorkers = [
    { id: 1, code: 'WRK-1001', name: 'R. Kumar', role: 'Excavator Operator', zone: 'Pit Bench #3', status: 'active' },
    { id: 2, code: 'WRK-1002', name: 'A. Sharma', role: 'Drill Technician', zone: 'Level -250m Stope', status: 'active' },
    { id: 3, code: 'WRK-1003', name: 'M. Singh', role: 'Blaster', zone: 'Pit Bench #4 East', status: 'active' },
    { id: 4, code: 'WRK-1004', name: 'S. Patel', role: 'Ventilation Tech', zone: 'Shaft 2 Intake', status: 'active' },
  ];

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-slate-200 flex items-center space-x-2">
          <Users className="w-4 h-4 text-blue-400" />
          <span>Active Worker Roster</span>
        </h3>
        <span className="text-xs bg-blue-500/10 text-blue-400 px-2.5 py-0.5 rounded-full font-medium">
          4 On Duty
        </span>
      </div>

      {/* Worker List */}
      <div className="space-y-2.5 overflow-y-auto max-h-[480px] pr-1">
        {sampleWorkers.map((w) => (
          <div
            key={w.id}
            className="bg-slate-950/60 border border-slate-800 rounded-lg p-3 flex items-center justify-between hover:border-slate-700 transition"
          >
            <div className="flex items-center space-x-3">
              <div className="bg-slate-800 p-2 rounded-lg text-slate-300">
                <HardHat className="w-4 h-4" />
              </div>
              <div>
                <p className="text-xs font-semibold text-slate-100">{w.name} ({w.code})</p>
                <p className="text-[11px] text-slate-400">{w.role} • {w.zone}</p>
              </div>
            </div>
            <div className="text-right">
              <span className="inline-flex items-center text-[10px] font-medium text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1.5 animate-pulse"></span>
                Active
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-auto pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
        <span>Geofence Status:</span>
        <span className="text-emerald-400 font-medium">All Personnel in Safe Zones</span>
      </div>
    </div>
  );
}

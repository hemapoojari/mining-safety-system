import React, { useState } from 'react';
import { AlertOctagon, BellRing, CheckCircle2, ChevronRight } from 'lucide-react';

export default function EmergencyAlerts() {
  const [activeAlert, setActiveAlert] = useState(null);

  // When there are no critical alerts, render a slim standby banner
  if (!activeAlert) {
    return (
      <div className="bg-slate-900/50 border-b border-slate-800/80 px-6 py-2 flex items-center justify-between text-xs text-slate-400">
        <div className="flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>Automated Hazard Scanning: No Critical Evacuation Alerts Active</span>
        </div>
        <div className="text-slate-500 text-[11px]">
          Targeted Alert Dispatch Ready
        </div>
      </div>
    );
  }

  return (
    <div className="bg-red-950/80 border-b border-red-700/60 px-6 py-3 flex flex-wrap items-center justify-between gap-3 text-red-200">
      <div className="flex items-center space-x-3">
        <div className="bg-red-600 p-2 rounded-lg text-white animate-bounce">
          <AlertOctagon className="w-5 h-5" />
        </div>
        <div>
          <p className="font-bold text-sm text-red-100 flex items-center space-x-2">
            <span>CRITICAL RISK DETECTED: {activeAlert.zone_name}</span>
            <span className="bg-red-600/40 border border-red-500 text-[10px] px-2 py-0.5 rounded uppercase">
              Level 5 Evacuate
            </span>
          </p>
          <p className="text-xs text-red-300">
            {activeAlert.message} • Targeted dispatch sent to {activeAlert.workers_count} personnel.
          </p>
        </div>
      </div>

      <div className="flex items-center space-x-3">
        <div className="text-xs bg-red-900/60 border border-red-700 px-3 py-1.5 rounded-lg">
          <span className="font-semibold text-white">ACK Status:</span> 2 / 2 Evacuating
        </div>
      </div>
    </div>
  );
}

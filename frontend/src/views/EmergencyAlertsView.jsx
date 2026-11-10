import React, { useState, useEffect } from 'react';
import {
  AlertOctagon,
  BellRing,
  CheckCircle2,
  AlertTriangle,
  Clock,
  ShieldCheck,
  UserCheck,
  LifeBuoy,
  XCircle,
  PlusCircle,
  RefreshCw,
} from 'lucide-react';
import {
  getActiveAlerts,
  getAlertHistory,
  getAlertEvacuationStatus,
  acknowledgeAlert,
  resolveAlert,
  triggerEmergencyAlert,
} from '../services/api';

export default function EmergencyAlertsView({
  activeAlerts = [],
  zones = [],
  workers = [],
  onRefresh,
}) {
  const [selectedAlertId, setSelectedAlertId] = useState(
    activeAlerts.length > 0 ? activeAlerts[0].id : null
  );
  const [evacDetail, setEvacDetail] = useState(null);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);
  const [historyAlerts, setHistoryAlerts] = useState([]);
  const [isTriggerModalOpen, setIsTriggerModalOpen] = useState(false);

  // Trigger modal state
  const [triggerZoneId, setTriggerZoneId] = useState(zones.length > 0 ? zones[0].id : 1);
  const [triggerRiskTier, setTriggerRiskTier] = useState('Critical');
  const [triggerHazardType, setTriggerHazardType] = useState('toxic_gas');
  const [triggerMessage, setTriggerMessage] = useState('Critical atmospheric gas breach detected. Evacuate immediately.');

  // Fetch evacuation roster when selectedAlertId changes
  useEffect(() => {
    if (selectedAlertId) {
      loadEvacuationStatus(selectedAlertId);
    } else if (activeAlerts.length > 0) {
      setSelectedAlertId(activeAlerts[0].id);
    }
  }, [selectedAlertId, activeAlerts]);

  // Fetch alert history
  useEffect(() => {
    getAlertHistory({ limit: 10 })
      .then((res) => setHistoryAlerts(res || []))
      .catch((err) => console.error('Failed to load alert history:', err));
  }, []);

  const loadEvacuationStatus = async (alertId) => {
    setIsLoadingDetail(true);
    try {
      const data = await getAlertEvacuationStatus(alertId);
      setEvacDetail(data);
    } catch (err) {
      console.error('Failed to load evacuation status:', err);
    } finally {
      setIsLoadingDetail(false);
    }
  };

  const handleWorkerAck = async (workerId, newStatus) => {
    if (!selectedAlertId) return;
    try {
      await acknowledgeAlert(selectedAlertId, {
        worker_id: workerId,
        status: newStatus,
        notes: `Simulated worker action: ${newStatus}`,
      });
      await loadEvacuationStatus(selectedAlertId);
      if (onRefresh) onRefresh();
    } catch (err) {
      alert(`Status update failed: ${err.message}`);
    }
  };

  const handleResolveAlert = async (alertId) => {
    if (!confirm('Are you sure you want to resolve this emergency alert? All worker statuses will be normalized.')) {
      return;
    }
    try {
      await resolveAlert(alertId);
      setSelectedAlertId(null);
      setEvacDetail(null);
      if (onRefresh) onRefresh();
    } catch (err) {
      alert(`Failed to resolve alert: ${err.message}`);
    }
  };

  const handleTriggerSubmit = async (e) => {
    e.preventDefault();
    try {
      await triggerEmergencyAlert({
        zone_id: parseInt(triggerZoneId),
        risk_tier: triggerRiskTier,
        hazard_type: triggerHazardType,
        message: triggerMessage,
      });
      setIsTriggerModalOpen(false);
      if (onRefresh) onRefresh();
    } catch (err) {
      alert(`Trigger failed: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Action Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-sm font-bold text-slate-100 uppercase tracking-wider flex items-center gap-2">
            <AlertOctagon className="w-5 h-5 text-red-500" />
            <span>Emergency Command & Evacuation Control Center</span>
          </h2>
          <p className="text-xs text-slate-400">
            Real-time incident response, targeted worker routing, and 2-way evacuation tracking
          </p>
        </div>

        <button
          onClick={() => setIsTriggerModalOpen(true)}
          className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white text-xs font-bold rounded-xl transition shadow-lg shadow-red-600/30 flex items-center gap-1.5"
        >
          <PlusCircle className="w-4 h-4" />
          <span>Manual Alarm Trigger</span>
        </button>
      </div>

      {/* Main Grid: Active Incidents & Live Evacuation Roster */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Active Alerts Selector */}
        <div className="lg:col-span-5 space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
            Active Emergency Incidents ({activeAlerts.length})
          </h3>

          {activeAlerts.length === 0 ? (
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 text-center shadow-xl">
              <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto mb-2" />
              <h4 className="font-bold text-sm text-slate-200">No Active Emergency Alerts</h4>
              <p className="text-xs text-slate-400 mt-1">
                All open-pit benches and underground stopes are operating under safe statutory guidelines.
              </p>
            </div>
          ) : (
            activeAlerts.map((alert) => {
              const isSelected = selectedAlertId === alert.id;
              return (
                <div
                  key={alert.id}
                  onClick={() => setSelectedAlertId(alert.id)}
                  className={`bg-slate-900 border rounded-2xl p-4 shadow-xl cursor-pointer transition ${
                    isSelected
                      ? 'border-red-500 shadow-red-950/40 bg-red-950/10'
                      : 'border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-mono text-xs font-bold text-red-400">
                      {alert.alert_code}
                    </span>
                    <div className="flex items-center gap-1.5">
                      {alert.affected_workers_count > alert.acknowledged_count && (
                        <span className="bg-amber-500/20 text-amber-300 border border-amber-500/50 text-[10px] font-bold px-2 py-0.5 rounded-full animate-pulse flex items-center gap-1" title="Unacknowledged by workers">
                          <BellRing className="w-2.5 h-2.5" />
                          <span>{alert.affected_workers_count - alert.acknowledged_count} Un-ACK</span>
                        </span>
                      )}
                      <span className="bg-red-600 text-white font-bold text-[10px] px-2 py-0.5 rounded-full uppercase animate-pulse">
                        {alert.risk_tier} Level
                      </span>
                    </div>
                  </div>

                  <p className="font-bold text-sm text-slate-100 mb-1">
                    {alert.zone_name}
                  </p>
                  <p className="text-xs text-slate-300 line-clamp-2 mb-3">
                    {alert.message}
                  </p>

                  {/* Micro Progress Bar */}
                  <div className="space-y-1">
                    <div className="flex justify-between text-[11px] text-slate-400">
                      <span>Evacuation Progress</span>
                      <span className="font-semibold text-emerald-400">
                        {alert.evacuated_safe_count} / {alert.affected_workers_count} Safe
                      </span>
                    </div>
                    <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden flex">
                      <div
                        style={{
                          width: `${(alert.evacuated_safe_count / Math.max(1, alert.affected_workers_count)) * 100}%`,
                        }}
                        className="bg-emerald-500 transition-all duration-300"
                      />
                      <div
                        style={{
                          width: `${(alert.trapped_count / Math.max(1, alert.affected_workers_count)) * 100}%`,
                        }}
                        className="bg-red-600 transition-all duration-300"
                      />
                    </div>
                  </div>

                  <div className="mt-3 pt-2.5 border-t border-slate-800 flex items-center justify-between text-[10px] text-slate-500">
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {new Date(alert.created_at).toLocaleTimeString()}
                    </span>
                    <span className="text-slate-400 font-medium">Click to manage &rarr;</span>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Right: Selected Alert Detail & Worker Evacuation Roster */}
        <div className="lg:col-span-7">
          {evacDetail ? (
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-5">
              {/* Incident Header */}
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-4">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-mono text-xs font-bold text-red-400">
                      {evacDetail.alert_code}
                    </span>
                    <span className="text-xs font-bold px-2 py-0.5 rounded bg-red-600/30 text-red-300 border border-red-500/50 uppercase">
                      Targeted Incident
                    </span>
                  </div>
                  <h3 className="text-base font-bold text-slate-100">
                    {evacDetail.zone_name} • {evacDetail.hazard_type.replace('_', ' ').toUpperCase()}
                  </h3>
                </div>

                <button
                  onClick={() => handleResolveAlert(evacDetail.alert_id)}
                  className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-xl transition shadow flex items-center gap-1.5"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Resolve & Stand Down</span>
                </button>
              </div>

              {/* Progress Counters Tally */}
              <div className="grid grid-cols-4 gap-2 text-center">
                <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-2.5">
                  <span className="text-[10px] text-slate-400 block uppercase">Total at Risk</span>
                  <span className="text-lg font-bold font-mono text-slate-100">
                    {evacDetail.affected_workers_count}
                  </span>
                </div>
                <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-2.5">
                  <span className="text-[10px] text-blue-400 block uppercase">ACK Received</span>
                  <span className="text-lg font-bold font-mono text-blue-400">
                    {evacDetail.acknowledged_count}
                  </span>
                </div>
                <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-2.5">
                  <span className="text-[10px] text-emerald-400 block uppercase">Safe / In Shelter</span>
                  <span className="text-lg font-bold font-mono text-emerald-400">
                    {evacDetail.evacuated_safe_count}
                  </span>
                </div>
                <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-2.5">
                  <span className="text-[10px] text-red-400 block uppercase">Trapped / Alert</span>
                  <span className="text-lg font-bold font-mono text-red-400">
                    {evacDetail.trapped_count}
                  </span>
                </div>
              </div>

                  {/* Evacuation Route Card */}
                  {evacDetail.route_details && (() => {
                    let route = null;
                    try {
                      route = typeof evacDetail.route_details === 'string' ? JSON.parse(evacDetail.route_details) : evacDetail.route_details;
                    } catch (e) { route = null; }
                    if (!route) return null;
                    const isBlocked = route.route_status === 'UNSAFE_BLOCKED';

                    return (
                      <div className={`p-3.5 rounded-xl border text-xs ${
                        isBlocked
                          ? 'bg-red-950/30 border-red-500/50 text-red-200'
                          : 'bg-amber-950/20 border-amber-500/40 text-amber-200'
                      }`}>
                        <div className="flex items-center justify-between font-bold uppercase tracking-wider mb-1">
                          <span className="flex items-center gap-1.5">
                            <LifeBuoy className="w-4 h-4 text-amber-400" />
                            <span>Evacuation Escapeway & Destination</span>
                          </span>
                          <span className={`px-2 py-0.5 rounded text-[10px] ${
                            isBlocked ? 'bg-red-600 text-white animate-pulse' : 'bg-emerald-600 text-white'
                          }`}>
                            {isBlocked ? 'ROUTE BLOCKED - SHELTER' : 'VERIFIED CLEAR'}
                          </span>
                        </div>
                        <p className="font-semibold text-slate-100 mb-0.5">
                          Target Refuge: {route.destination_name}
                        </p>
                        <p className="text-[11px] text-slate-300 mb-1.5">
                          Distance: {route.distance_meters}m • Est. Time: {route.est_evacuation_minutes} mins
                        </p>
                        <p className="text-[11px] bg-slate-950/60 p-2 rounded text-slate-300 font-mono">
                          {route.instructions}
                        </p>
                      </div>
                    );
                  })()}

                  {/* Affected Workers Roster with 2-Way ACK Simulation Controls */}
                  <div>
                    <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2.5 flex items-center justify-between">
                      <span>Targeted Personnel Evacuation Status ({evacDetail.workers.length})</span>
                      <span className="text-[10px] text-slate-400 font-normal">
                        Simulated Wearable 2-Way ACK Controls
                      </span>
                    </h4>

                    <div className="space-y-2 max-h-[360px] overflow-y-auto pr-1">
                      {evacDetail.workers.length === 0 ? (
                        <p className="text-xs text-slate-500 italic py-4 text-center">
                          No workers localized in this zone during alert trigger.
                        </p>
                      ) : (
                        evacDetail.workers.map((w) => {
                          const isSafe = w.status === 'safe';
                          const isAck = w.status === 'acknowledged';
                          const isEvac = w.status === 'evacuating';
                          const isTrapped = w.status === 'trapped';
                          const isAlertSent = w.status === 'notified';

                          return (
                            <div
                              key={w.worker_id}
                              className={`bg-slate-950/70 border rounded-xl p-3 flex flex-wrap items-center justify-between gap-3 ${
                                isAlertSent ? 'border-amber-500/40 bg-amber-950/10' : 'border-slate-800'
                              }`}
                            >
                              <div>
                                <div className="flex items-center gap-2">
                                  <span className="font-bold text-xs text-slate-100">
                                    {w.full_name}
                                  </span>
                                  <span className="font-mono text-[10px] text-slate-400">
                                    ({w.worker_code})
                                  </span>
                                  {isAlertSent && (
                                    <span className="text-[9px] font-bold px-1.5 py-0.2 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40 animate-pulse">
                                      Awaiting ACK
                                    </span>
                                  )}
                                  {isSafe && (
                                    <span className="text-[9px] font-bold px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                                      Reached Safe Zone
                                    </span>
                                  )}
                                </div>
                                <p className="text-[11px] text-slate-400">
                                  {w.role} • Status: <strong className="capitalize text-slate-200">{w.status.replace('_', ' ')}</strong>
                                </p>
                              </div>

                              {/* Interactive 2-Way Status & ACK Simulation Buttons */}
                              <div className="flex items-center gap-1.5">
                                <button
                                  onClick={() => handleWorkerAck(w.worker_id, 'acknowledged')}
                                  className={`px-2 py-1 text-[10px] rounded-lg font-medium transition ${
                                    isAck
                                      ? 'bg-blue-600 text-white font-bold'
                                      : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                                  }`}
                                  title="Simulate worker acknowledging receipt of emergency evacuation alarm"
                                >
                                  Acknowledge
                                </button>

                                <button
                                  onClick={() => handleWorkerAck(w.worker_id, 'evacuating')}
                                  className={`px-2 py-1 text-[10px] rounded-lg font-medium transition ${
                                    isEvac
                                      ? 'bg-orange-600 text-white font-bold'
                                      : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                                  }`}
                                  title="Simulate worker in transit along escape route"
                                >
                                  Evacuating
                                </button>

                                <button
                                  onClick={() => handleWorkerAck(w.worker_id, 'safe')}
                                  className={`px-2 py-1 text-[10px] rounded-lg font-medium transition ${
                                    isSafe
                                      ? 'bg-emerald-600 text-white font-bold'
                                      : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                                  }`}
                                  title="Confirm worker has arrived at safe muster ground or hermetic refuge chamber"
                                >
                                  Safe in Refuge
                                </button>

                                <button
                                  onClick={() => handleWorkerAck(w.worker_id, 'trapped')}
                                  className={`px-2 py-1 text-[10px] rounded-lg font-medium transition ${
                                    isTrapped
                                      ? 'bg-red-600 text-white font-bold animate-pulse'
                                      : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                                  }`}
                                  title="Worker triggered emergency beacon: Trapped or Needs Rescue"
                                >
                                  Trapped / SOS
                                </button>
                              </div>
                            </div>
                          );
                        })
                      )}
                    </div>
                  </div>
                </div>
              ) : (
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 text-center text-slate-400">
              <ShieldCheck className="w-10 h-10 text-slate-600 mx-auto mb-2" />
              <p className="text-xs">Select an active emergency incident from the left to inspect evacuation status.</p>
            </div>
          )}
        </div>
      </div>

      {/* Manual Trigger Modal */}
      {isTriggerModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl">
            <h3 className="text-base font-bold text-slate-100 mb-1 flex items-center gap-2">
              <AlertOctagon className="w-5 h-5 text-red-500" />
              <span>Manual Emergency Evacuation Trigger</span>
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Instantly broadcast a targeted emergency alarm to all personnel situated in the selected zone.
            </p>

            <form onSubmit={handleTriggerSubmit} className="space-y-3.5">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Target Zone</label>
                <select
                  value={triggerZoneId}
                  onChange={(e) => setTriggerZoneId(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-red-500"
                >
                  {zones.map((z) => (
                    <option key={z.id} value={z.id}>
                      {z.name} ({z.mine_type})
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Risk Level</label>
                  <select
                    value={triggerRiskTier}
                    onChange={(e) => setTriggerRiskTier(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-red-500"
                  >
                    <option value="Critical">Critical (Immediate Evac)</option>
                    <option value="High">High (Precautionary)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Hazard Type</label>
                  <select
                    value={triggerHazardType}
                    onChange={(e) => setTriggerHazardType(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-red-500"
                  >
                    <option value="toxic_gas">Toxic Gas Surge</option>
                    <option value="slope_failure">Slope Failure</option>
                    <option value="rockfall">Rockfall Hazard</option>
                    <option value="fire_hazard">Mine Fire</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Emergency Broadcast Message</label>
                <textarea
                  rows="3"
                  required
                  value={triggerMessage}
                  onChange={(e) => setTriggerMessage(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-red-500"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsTriggerModalOpen(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium rounded-xl transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white text-xs font-bold rounded-xl transition shadow-lg shadow-red-600/30"
                >
                  Broadcast Alarm
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

import React, { useState } from 'react';
import {
  Users,
  UserPlus,
  Search,
  Filter,
  MapPin,
  HardHat,
  Phone,
  Radio,
  CheckCircle2,
  AlertTriangle,
  Move,
} from 'lucide-react';
import { registerWorker, updateWorkerLocation } from '../services/api';

const STATUS_BADGES = {
  active: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40',
  evacuating: 'bg-orange-500/20 text-orange-400 border-orange-500/40 animate-pulse',
  safe: 'bg-green-500/20 text-green-400 border-green-500/40',
  trapped: 'bg-red-500/20 text-red-400 border-red-500/40 animate-bounce',
  off_duty: 'bg-slate-700/30 text-slate-400 border-slate-700',
};

export default function WorkerTrackingView({
  workers = [],
  zones = [],
  onRefresh,
}) {
  const [search, setSearch] = useState('');
  const [zoneFilter, setZoneFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [isRegisterOpen, setIsRegisterOpen] = useState(false);
  const [isSimulatingMove, setIsSimulatingMove] = useState(false);

  // New worker form state
  const [newCode, setNewCode] = useState('');
  const [newName, setNewName] = useState('');
  const [newRole, setNewRole] = useState('Miner');
  const [newPhone, setNewPhone] = useState('');
  const [newZoneId, setNewZoneId] = useState('');

  const filtered = workers.filter((w) => {
    const matchesSearch =
      w.worker_code.toLowerCase().includes(search.toLowerCase()) ||
      w.full_name.toLowerCase().includes(search.toLowerCase()) ||
      (w.role && w.role.toLowerCase().includes(search.toLowerCase()));

    const matchesZone = zoneFilter === 'all' || (w.zone_id && String(w.zone_id) === String(zoneFilter));
    const matchesStatus = statusFilter === 'all' || w.status === statusFilter;

    return matchesSearch && matchesZone && matchesStatus;
  });

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      await registerWorker({
        worker_code: newCode,
        full_name: newName,
        role: newRole,
        phone: newPhone,
        zone_id: newZoneId ? parseInt(newZoneId) : null,
        current_lat: 23.7450,
        current_lng: 86.4150,
        elevation_or_level: 'Surface Station',
        status: 'active',
      });
      setIsRegisterOpen(false);
      setNewCode('');
      setNewName('');
      setNewRole('Miner');
      setNewPhone('');
      setNewZoneId('');
      if (onRefresh) onRefresh();
    } catch (err) {
      alert(`Registration failed: ${err.message}`);
    }
  };

  const handleSimulateMovement = async () => {
    setIsSimulatingMove(true);
    try {
      // Step all workers slightly in coordinates
      for (const w of workers.slice(0, 5)) {
        if (!w.current_lat || !w.current_lng) continue;
        const deltaLat = (Math.random() - 0.5) * 0.0004;
        const deltaLng = (Math.random() - 0.5) * 0.0004;
        await updateWorkerLocation(w.id, {
          current_lat: parseFloat((w.current_lat + deltaLat).toFixed(6)),
          current_lng: parseFloat((w.current_lng + deltaLng).toFixed(6)),
          elevation_or_level: w.elevation_or_level,
        });
      }
      if (onRefresh) onRefresh();
    } catch (err) {
      console.error('Movement simulation failed:', err);
    } finally {
      setIsSimulatingMove(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Simulation Notice Banner */}
      <div className="bg-sky-950/30 border border-sky-800/40 rounded-xl p-3 flex items-center justify-between text-xs text-sky-200">
        <div className="flex items-center gap-2">
          <Radio className="w-4 h-4 text-sky-400 animate-pulse flex-shrink-0" />
          <span>
            <strong>Simulated Worker Telemetry Feed:</strong> Worker GPS coordinates (Open-Pit) and sub-surface beacon markers (Underground) are synthetically generated for demonstration and evacuation testing.
          </span>
        </div>
        <span className="text-[10px] bg-sky-900/60 px-2 py-0.5 rounded text-sky-300 font-mono">
          Demo Prototype
        </span>
      </div>

      {/* Header and Controls */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl flex flex-wrap items-center justify-between gap-4">
        {/* Search */}
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search worker ID, name, or job role..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 transition"
          />
        </div>

        {/* Filters and Actions */}
        <div className="flex items-center space-x-2">
          {/* Zone Filter */}
          <select
            value={zoneFilter}
            onChange={(e) => setZoneFilter(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-blue-500"
          >
            <option value="all">All Mine Zones</option>
            {zones.map((z) => (
              <option key={z.id} value={z.id}>
                {z.name}
              </option>
            ))}
          </select>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-blue-500"
          >
            <option value="all">All Statuses</option>
            <option value="active">Active</option>
            <option value="evacuating">Evacuating</option>
            <option value="safe">Safe</option>
            <option value="trapped">Trapped</option>
          </select>

          {/* Simulate Walking */}
          <button
            onClick={handleSimulateMovement}
            disabled={isSimulatingMove}
            className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-xl transition flex items-center gap-1.5 disabled:opacity-50"
            title="Simulate live GPS/BLE worker movement and geofence updates"
          >
            <Move className={`w-3.5 h-3.5 ${isSimulatingMove ? 'animate-spin' : ''}`} />
            <span>Simulate Walk</span>
          </button>

          {/* Register Worker Button */}
          <button
            onClick={() => setIsRegisterOpen(true)}
            className="px-3.5 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold rounded-xl transition shadow-lg shadow-blue-600/30 flex items-center gap-1.5"
          >
            <UserPlus className="w-4 h-4" />
            <span>Register Miner</span>
          </button>
        </div>
      </div>

      {/* Workers Roster Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-5 py-3.5">Worker Code & Name</th>
                <th className="px-5 py-3.5">Assigned Zone</th>
                <th className="px-5 py-3.5">Job Role</th>
                <th className="px-5 py-3.5">Coordinates & Level</th>
                <th className="px-5 py-3.5">Contact</th>
                <th className="px-5 py-3.5">Safety Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filtered.map((w) => (
                <tr key={w.id} className="hover:bg-slate-800/40 transition">
                  {/* Worker Code & Name */}
                  <td className="px-5 py-3.5">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-slate-800 rounded-xl text-slate-300">
                        <HardHat className="w-4 h-4" />
                      </div>
                      <div>
                        <span className="font-bold text-slate-100 block">{w.full_name}</span>
                        <span className="font-mono text-[11px] text-slate-400">{w.worker_code}</span>
                      </div>
                    </div>
                  </td>

                  {/* Zone */}
                  <td className="px-5 py-3.5 font-medium text-slate-300">
                    {w.zone_name || 'Unassigned / Surface'}
                  </td>

                  {/* Role */}
                  <td className="px-5 py-3.5 text-slate-400">
                    {w.role}
                  </td>

                  {/* Coordinates & Level */}
                  <td className="px-5 py-3.5 font-mono text-[11px] text-slate-400">
                    <div>{w.current_lat && w.current_lng ? `${w.current_lat}, ${w.current_lng}` : '--'}</div>
                    <div className="text-slate-500 text-[10px]">{w.elevation_or_level || 'Ground'}</div>
                  </td>

                  {/* Contact */}
                  <td className="px-5 py-3.5 text-slate-400 font-mono text-[11px]">
                    {w.phone || '--'}
                  </td>

                  {/* Status Badge */}
                  <td className="px-5 py-3.5">
                    <span
                      className={`inline-flex items-center text-[10px] font-bold px-2.5 py-1 rounded-full border uppercase ${
                        STATUS_BADGES[w.status] || STATUS_BADGES.active
                      }`}
                    >
                      {w.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Register Worker Modal */}
      {isRegisterOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl">
            <h3 className="text-base font-bold text-slate-100 mb-1 flex items-center gap-2">
              <UserPlus className="w-5 h-5 text-blue-400" />
              <span>Register New Mine Personnel</span>
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Enroll worker with role, emergency phone, and initial mining sector geofence.
            </p>

            <form onSubmit={handleRegister} className="space-y-3.5">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Worker Code</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. WRK-2001"
                  value={newCode}
                  onChange={(e) => setNewCode(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-blue-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Full Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Ramesh Patel"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Job Role</label>
                  <select
                    value={newRole}
                    onChange={(e) => setNewRole(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-blue-500"
                  >
                    <option value="Miner">Miner</option>
                    <option value="Excavator Operator">Excavator Operator</option>
                    <option value="Drill Technician">Drill Technician</option>
                    <option value="Blaster">Blaster</option>
                    <option value="Ventilation Inspector">Ventilation Inspector</option>
                    <option value="Safety Officer">Safety Officer</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Assigned Zone</label>
                  <select
                    value={newZoneId}
                    onChange={(e) => setNewZoneId(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-blue-500"
                  >
                    <option value="">Unassigned</option>
                    {zones.map((z) => (
                      <option key={z.id} value={z.id}>
                        {z.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Emergency Phone</label>
                <input
                  type="text"
                  placeholder="+91-9876543210"
                  value={newPhone}
                  onChange={(e) => setNewPhone(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-blue-500 font-mono"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-3">
                <button
                  type="button"
                  onClick={() => setIsRegisterOpen(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium rounded-xl transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold rounded-xl transition shadow-lg shadow-blue-600/30"
                >
                  Register Worker
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

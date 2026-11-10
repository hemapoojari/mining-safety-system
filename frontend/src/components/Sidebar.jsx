import React from 'react';
import {
  LayoutDashboard,
  Mountain,
  Flame,
  Activity,
  Users,
  AlertOctagon,
  BarChart3,
  Settings,
  ShieldAlert,
  ChevronLeft,
  ChevronRight,
  Menu,
  X,
} from 'lucide-react';

const NAV_ITEMS = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard },
  { id: 'open_pit', label: 'Open-Pit Mining', icon: Mountain },
  { id: 'underground', label: 'Underground Mining', icon: Flame },
  { id: 'sensors', label: 'Live Sensors', icon: Activity },
  { id: 'workers', label: 'Worker Tracking', icon: Users },
  { id: 'alerts', label: 'Emergency Alerts', icon: AlertOctagon },
  { id: 'analytics', label: 'Analytics & Trends', icon: BarChart3 },
  { id: 'settings', label: 'System Settings', icon: Settings },
];

export default function Sidebar({
  currentView,
  setCurrentView,
  activeAlertCount = 0,
  isCollapsed,
  setIsCollapsed,
  isMobileOpen,
  setIsMobileOpen,
}) {
  return (
    <>
      {/* Mobile Backdrop */}
      {isMobileOpen && (
        <div
          onClick={() => setIsMobileOpen(false)}
          className="fixed inset-0 z-40 bg-slate-950/80 backdrop-blur-sm lg:hidden"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed lg:static top-0 bottom-0 left-0 z-50 flex flex-col bg-slate-900 border-r border-slate-800 transition-all duration-300 ${
          isCollapsed ? 'w-20' : 'w-64'
        } ${isMobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}
      >
        {/* Brand Header */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-slate-800">
          <div className="flex items-center space-x-3 overflow-hidden">
            <div className="bg-red-500/10 border border-red-500/30 p-2 rounded-xl text-red-500 shrink-0">
              <ShieldAlert className="w-5 h-5" />
            </div>
            {!isCollapsed && (
              <div className="leading-tight">
                <span className="font-bold text-sm tracking-wide text-slate-100 uppercase">
                  Mine Safety
                </span>
                <span className="block text-[10px] text-slate-400 font-mono">
                  Evacuation Hub
                </span>
              </div>
            )}
          </div>

          {/* Collapse Toggle (Desktop) */}
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="hidden lg:flex p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition"
            title={isCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
          >
            {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>

          {/* Close Button (Mobile) */}
          <button
            onClick={() => setIsMobileOpen(false)}
            className="lg:hidden p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation List */}
        <nav className="flex-1 overflow-y-auto p-3 space-y-1.5">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = currentView === item.id;
            const isAlertItem = item.id === 'alerts';

            return (
              <button
                key={item.id}
                onClick={() => {
                  setCurrentView(item.id);
                  setIsMobileOpen(false);
                }}
                className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl font-medium text-xs transition relative group ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/25'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'
                }`}
                title={isCollapsed ? item.label : undefined}
              >
                <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-white' : 'text-slate-400 group-hover:text-slate-200'}`} />
                {!isCollapsed && <span className="truncate">{item.label}</span>}

                {/* Emergency Alert Badge */}
                {isAlertItem && activeAlertCount > 0 && (
                  <span
                    className={`shrink-0 ml-auto inline-flex items-center justify-center font-bold text-[10px] rounded-full animate-pulse ${
                      isCollapsed
                        ? 'absolute top-1 right-1 w-2.5 h-2.5 bg-red-500'
                        : 'px-2 py-0.5 bg-red-600 text-white'
                    }`}
                  >
                    {!isCollapsed && activeAlertCount}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Bottom Safety Status Pill */}
        <div className="p-3 border-t border-slate-800">
          {!isCollapsed ? (
            <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-3">
              <div className="flex items-center justify-between text-[11px] font-medium text-slate-400 mb-1">
                <span>System Status</span>
                <span className="text-emerald-400 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
                  Live
                </span>
              </div>
              <p className="text-[10px] text-slate-500 font-mono truncate">
                Telemetry Engine Active
              </p>
            </div>
          ) : (
            <div className="flex justify-center">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" title="System Live" />
            </div>
          )}
        </div>
      </aside>
    </>
  );
}

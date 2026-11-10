import React, { useState, useEffect, useCallback } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import OverviewView from './views/OverviewView';
import OpenPitView from './views/OpenPitView';
import UndergroundView from './views/UndergroundView';
import LiveSensorsView from './views/LiveSensorsView';
import WorkerTrackingView from './views/WorkerTrackingView';
import EmergencyAlertsView from './views/EmergencyAlertsView';
import AnalyticsView from './views/AnalyticsView';
import SettingsView from './views/SettingsView';

import {
  getZones,
  getWorkers,
  getCurrentSensorReadings,
  getActiveAlerts,
} from './services/api';
import { wsService } from './services/websocket';

export default function App() {
  const [currentView, setCurrentView] = useState('overview');
  const [zones, setZones] = useState([]);
  const [workers, setWorkers] = useState([]);
  const [currentReadings, setCurrentReadings] = useState([]);
  const [activeAlerts, setActiveAlerts] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Responsive Sidebar States
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  // Load all initial state from backend
  const loadInitialData = useCallback(async () => {
    try {
      const [zonesData, workersData, readingsData, alertsData] = await Promise.all([
        getZones().catch(() => []),
        getWorkers().catch(() => []),
        getCurrentSensorReadings().catch(() => []),
        getActiveAlerts().catch(() => []),
      ]);

      setZones(zonesData || []);
      setWorkers(workersData || []);
      setCurrentReadings(readingsData || []);
      setActiveAlerts(alertsData || []);
    } catch (err) {
      console.error('Failed to load initial mine safety data:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Initialize data and WebSocket subscriptions
  useEffect(() => {
    loadInitialData();

    // Connect to WebSocket stream
    wsService.connect();

    // 1. Connection status change
    const unbindStatus = wsService.on('STATUS_CHANGE', ({ connected }) => {
      setIsConnected(connected);
    });

    // 2. Real-time sensor reading arrived
    const unbindSensor = wsService.on('SENSOR_READING', (reading) => {
      setCurrentReadings((prev) => {
        const index = prev.findIndex((r) => r.sensor_code === reading.sensor_code);
        if (index >= 0) {
          const updated = [...prev];
          updated[index] = {
            ...updated[index],
            latest_value: reading.value,
            last_updated: reading.timestamp,
          };
          return updated;
        }
        return [
          ...prev,
          {
            sensor_code: reading.sensor_code,
            name: `${reading.sensor_type} (${reading.sensor_code})`,
            zone_id: reading.zone_id,
            zone_name: reading.zone_name,
            mine_type: reading.mine_type,
            sensor_type: reading.sensor_type,
            latest_value: reading.value,
            unit: reading.unit,
            status: 'active',
            last_updated: reading.timestamp,
          },
        ];
      });
    });

    // 3. Zone risk level updated
    const unbindRisk = wsService.on('RISK_UPDATE', (riskData) => {
      setZones((prev) =>
        prev.map((z) =>
          z.id === riskData.zone_id
            ? { ...z, current_risk_tier: riskData.current_risk_tier, updated_at: riskData.timestamp }
            : z
        )
      );
    });

    // 4. Worker location/geofence updated
    const unbindWorker = wsService.on('WORKER_LOCATION', (workerData) => {
      setWorkers((prev) =>
        prev.map((w) =>
          w.id === workerData.worker_id
            ? {
                ...w,
                current_lat: workerData.current_lat,
                current_lng: workerData.current_lng,
                elevation_or_level: workerData.elevation_or_level,
                zone_id: workerData.zone_id,
                zone_name: workerData.zone_name,
                status: workerData.status,
                last_ping: workerData.last_ping,
              }
            : w
        )
      );
    });

    // 5. Emergency Alert triggered
    const unbindAlert = wsService.on('EMERGENCY_ALERT', (alertData) => {
      setActiveAlerts((prev) => {
        const exists = prev.some((a) => a.id === alertData.alert_id);
        if (exists) return prev;
        return [
          {
            id: alertData.alert_id,
            alert_code: alertData.alert_code,
            zone_id: alertData.zone_id,
            zone_name: alertData.zone_name,
            risk_tier: alertData.risk_tier,
            hazard_type: alertData.hazard_type,
            message: alertData.message,
            affected_workers_count: alertData.affected_workers_count,
            acknowledged_count: 0,
            evacuated_safe_count: 0,
            trapped_count: 0,
            is_active: true,
            created_at: alertData.created_at,
          },
          ...prev,
        ];
      });
    });

    // 6. Evacuation status tally updated
    const unbindEvac = wsService.on('EVACUATION_STATUS', (statusData) => {
      setActiveAlerts((prev) =>
        prev.map((a) =>
          a.id === statusData.alert_id
            ? {
                ...a,
                acknowledged_count: statusData.acknowledged_count,
                evacuated_safe_count: statusData.evacuated_safe_count,
                trapped_count: statusData.trapped_count,
              }
            : a
        )
      );
      // Update worker status if matching
      setWorkers((prev) =>
        prev.map((w) =>
          w.id === statusData.worker_id ? { ...w, status: statusData.status } : w
        )
      );
    });

    // 7. Alert resolved
    const unbindResolve = wsService.on('EMERGENCY_ALERT_RESOLVED', (data) => {
      setActiveAlerts((prev) => prev.filter((a) => a.id !== data.alert_id));
      loadInitialData();
    });

    return () => {
      unbindStatus();
      unbindSensor();
      unbindRisk();
      unbindWorker();
      unbindAlert();
      unbindEvac();
      unbindResolve();
      wsService.disconnect();
    };
  }, [loadInitialData]);

  // Render current view component
  const renderView = () => {
    switch (currentView) {
      case 'overview':
        return (
          <OverviewView
            zones={zones}
            workers={workers}
            activeAlerts={activeAlerts}
            currentReadings={currentReadings}
            setCurrentView={setCurrentView}
          />
        );
      case 'open_pit':
        return (
          <OpenPitView
            zones={zones}
            workers={workers}
            activeAlerts={activeAlerts}
            currentReadings={currentReadings}
            onRefresh={loadInitialData}
          />
        );
      case 'underground':
        return (
          <UndergroundView
            zones={zones}
            workers={workers}
            activeAlerts={activeAlerts}
            currentReadings={currentReadings}
            onRefresh={loadInitialData}
          />
        );
      case 'sensors':
        return (
          <LiveSensorsView
            currentReadings={currentReadings}
            zones={zones}
            onRefresh={loadInitialData}
          />
        );
      case 'workers':
        return (
          <WorkerTrackingView
            workers={workers}
            zones={zones}
            onRefresh={loadInitialData}
          />
        );
      case 'alerts':
        return (
          <EmergencyAlertsView
            activeAlerts={activeAlerts}
            zones={zones}
            workers={workers}
            onRefresh={loadInitialData}
          />
        );
      case 'analytics':
        return (
          <AnalyticsView
            zones={zones}
            workers={workers}
          />
        );
      case 'settings':
        return (
          <SettingsView
            isConnected={isConnected}
          />
        );
      default:
        return (
          <OverviewView
            zones={zones}
            workers={workers}
            activeAlerts={activeAlerts}
            currentReadings={currentReadings}
            setCurrentView={setCurrentView}
          />
        );
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex font-sans antialiased overflow-x-hidden">
      {/* Sidebar Navigation */}
      <Sidebar
        currentView={currentView}
        setCurrentView={setCurrentView}
        activeAlertCount={activeAlerts.length}
        isCollapsed={isCollapsed}
        setIsCollapsed={setIsCollapsed}
        isMobileOpen={isMobileOpen}
        setIsMobileOpen={setIsMobileOpen}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-y-auto">
        {/* Top Header */}
        <Header
          currentView={currentView}
          setIsMobileOpen={setIsMobileOpen}
          isConnected={isConnected}
          onRefresh={loadInitialData}
        />

        {/* Dynamic View Body */}
        <main className="flex-1 p-4 md:p-6 max-w-[1920px] w-full mx-auto">
          {isLoading ? (
            <div className="h-64 flex flex-col items-center justify-center space-y-3">
              <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
              <p className="text-xs text-slate-400 font-medium">
                Loading Mine Safety Command Center...
              </p>
            </div>
          ) : (
            renderView()
          )}
        </main>

        {/* Footer */}
        <footer className="border-t border-slate-800/80 bg-slate-900/60 px-6 py-3 text-center text-[11px] text-slate-400">
          AI/ML-Powered Mining Safety and Worker Evacuation System • Academic Research & Demonstration Prototype • Live Telemetry Stream Connected
        </footer>
      </div>
    </div>
  );
}

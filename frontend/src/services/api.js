/**
 * Centralized REST API Service Client
 * AI/ML-Powered Mining Safety and Worker Evacuation System
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL !== undefined 
  ? import.meta.env.VITE_API_BASE_URL 
  : (import.meta.env.DEV ? 'http://localhost:8000' : '');

async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const res = await fetch(url, config);
    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP Error ${res.status}: ${res.statusText}`);
    }
    return await res.json();
  } catch (error) {
    console.error(`[API Error] ${options.method || 'GET'} ${endpoint}:`, error.message);
    throw error;
  }
}

// ---------------- SENSORS ----------------
export async function getSensors(params = {}) {
  const query = new URLSearchParams(params).toString();
  return request(`/api/sensors/${query ? `?${query}` : ''}`);
}

export async function getCurrentSensorReadings(zoneId = null) {
  const query = zoneId ? `?zone_id=${zoneId}` : '';
  return request(`/api/sensors/readings/current${query}`);
}

export async function getSensorHistory(params = {}) {
  const query = new URLSearchParams(params).toString();
  return request(`/api/sensors/readings/history${query ? `?${query}` : ''}`);
}

export async function submitSensorReading(readingData) {
  return request('/api/sensors/readings', {
    method: 'POST',
    body: JSON.stringify(readingData),
  });
}

export async function simulateTelemetryTick(anomaly = null) {
  const query = anomaly ? `?anomaly=${anomaly}` : '';
  return request(`/api/sensors/simulate-tick${query}`, {
    method: 'POST',
  });
}

// ---------------- WORKERS ----------------
export async function getWorkers(params = {}) {
  const query = new URLSearchParams(params).toString();
  return request(`/api/workers/${query ? `?${query}` : ''}`);
}

export async function getWorkerDetail(idOrCode) {
  return request(`/api/workers/${idOrCode}`);
}

export async function registerWorker(workerData) {
  return request('/api/workers/', {
    method: 'POST',
    body: JSON.stringify(workerData),
  });
}

export async function updateWorkerLocation(idOrCode, locationData) {
  return request(`/api/workers/${idOrCode}/location`, {
    method: 'POST',
    body: JSON.stringify(locationData),
  });
}

export async function getEvacuationSummary() {
  return request('/api/workers/evacuation/summary');
}

// ---------------- ZONES ----------------
export async function getZones(mineType = null) {
  const query = mineType ? `?mine_type=${mineType}` : '';
  return request(`/api/zones/${query}`);
}

export async function getZoneDetail(idOrCode) {
  return request(`/api/zones/${idOrCode}`);
}

export async function getZoneRiskDetail(idOrCode) {
  return request(`/api/zones/${idOrCode}/risk`);
}

export async function updateZoneRisk(idOrCode, riskData) {
  return request(`/api/zones/${idOrCode}/risk`, {
    method: 'PATCH',
    body: JSON.stringify(riskData),
  });
}

// ---------------- EMERGENCY ALERTS ----------------
export async function getActiveAlerts() {
  return request('/api/alerts/active');
}

export async function getAlertHistory(params = {}) {
  const query = new URLSearchParams(params).toString();
  return request(`/api/alerts/history${query ? `?${query}` : ''}`);
}

export async function triggerEmergencyAlert(alertData) {
  return request('/api/alerts/trigger', {
    method: 'POST',
    body: JSON.stringify(alertData),
  });
}

export async function acknowledgeAlert(alertId, ackData) {
  return request(`/api/alerts/${alertId}/acknowledge`, {
    method: 'POST',
    body: JSON.stringify(ackData),
  });
}

export async function getAlertEvacuationStatus(alertId) {
  return request(`/api/alerts/${alertId}/evacuation-status`);
}

export async function resolveAlert(alertId) {
  return request(`/api/alerts/${alertId}/resolve`, {
    method: 'POST',
  });
}

// ---------------- SIMULATION CONTROL ----------------
export async function getSimulationStatus() {
  return request('/api/simulation/status');
}

export async function startSimulation() {
  return request('/api/simulation/start', {
    method: 'POST',
  });
}

export async function stopSimulation() {
  return request('/api/simulation/stop', {
    method: 'POST',
  });
}

export async function resetSimulation() {
  return request('/api/simulation/reset', {
    method: 'POST',
  });
}

export async function setSimulationScenario(scenario) {
  return request('/api/simulation/scenario', {
    method: 'POST',
    body: JSON.stringify({ scenario }),
  });
}

export async function triggerSimulationTick() {
  return request('/api/simulation/tick', {
    method: 'POST',
  });
}

// ---------------- ADVANCED ANALYTICS & REPORTING ----------------
export async function getAnalyticsKPIs() {
  return request('/api/analytics/kpis');
}

export async function getHistoricalRisk(params = {}) {
  const query = new URLSearchParams(params).toString();
  return request(`/api/analytics/historical-risk${query ? `?${query}` : ''}`);
}

export async function getPredictiveTrends() {
  return request('/api/analytics/predictive-trends');
}

export async function getEvacuationPerformance() {
  return request('/api/analytics/evacuation-performance');
}

export async function getMLModelComparison() {
  return request('/api/analytics/ml-model-comparison');
}

export function getIncidentReportPDFUrl(alertId) {
  return `${API_BASE_URL}/api/reports/incident/${alertId}/pdf`;
}

export function getZoneSafetyPDFUrl(zoneId) {
  return `${API_BASE_URL}/api/reports/zone/${zoneId}/pdf`;
}

export function getSensorCSVUrl(params = {}) {
  const query = new URLSearchParams(params).toString();
  return `${API_BASE_URL}/api/reports/sensors/csv${query ? `?${query}` : ''}`;
}

export function getIncidentsCSVUrl() {
  return `${API_BASE_URL}/api/reports/incidents/csv`;
}

export async function triggerFileDownload(url, filename) {
  try {
    const res = await fetch(url);
    if (!res.ok) {
      throw new Error(`Download failed with HTTP ${res.status}`);
    }
    const blob = await res.blob();
    const blobUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = blobUrl;
    link.download = filename || 'download';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(blobUrl);
    return true;
  } catch (err) {
    console.error('File download error:', err);
    throw err;
  }
}

// ---------------- SYSTEM ----------------
export async function getHealth() {
  return request('/health');
}


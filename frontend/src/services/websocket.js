/**
 * Enhanced Real-Time WebSocket Client
 * AI/ML-Powered Mining Safety and Worker Evacuation System
 */

const getDefaultWsUrl = () => {
  if (typeof window !== 'undefined' && window.location) {
    if (window.location.port === '5173') {
      return `ws://${window.location.hostname}:8000`;
    }
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${protocol}//${window.location.host}`;
  }
  return 'ws://localhost:8000';
};

const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || getDefaultWsUrl();

class TelemetryWebSocketService {
  constructor() {
    this.socket = null;
    this.listeners = new Map();
    this.isConnected = false;
    this.reconnectTimeout = null;
    this.reconnectAttempts = 0;
    this.maxReconnectDelay = 10000;
  }

  connect() {
    if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
      return;
    }

    try {
      this.socket = new WebSocket(`${WS_BASE_URL}/ws/telemetry`);

      this.socket.onopen = () => {
        this.isConnected = true;
        this.reconnectAttempts = 0;
        console.log('[WebSocket] Connected to Mine Safety Telemetry Hub');
        this.emit('STATUS_CHANGE', { connected: true });
      };

      this.socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          const { event: eventType, data } = payload;
          if (eventType) {
            this.emit(eventType, data);
            // Also emit general 'ANY' event
            this.emit('*', { event: eventType, data });
          }
        } catch (err) {
          console.error('[WebSocket] Failed to parse incoming packet:', err);
        }
      };

      this.socket.onerror = (err) => {
        console.warn('[WebSocket] Error occurred:', err);
      };

      this.socket.onclose = () => {
        this.isConnected = false;
        this.emit('STATUS_CHANGE', { connected: false });
        this.scheduleReconnect();
      };
    } catch (err) {
      console.error('[WebSocket] Connection attempt failed:', err);
      this.scheduleReconnect();
    }
  }

  scheduleReconnect() {
    if (this.reconnectTimeout) return;
    const delay = Math.min(1000 * Math.pow(1.5, this.reconnectAttempts), this.maxReconnectDelay);
    this.reconnectAttempts++;
    this.reconnectTimeout = setTimeout(() => {
      this.reconnectTimeout = null;
      this.connect();
    }, delay);
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event).add(callback);

    // Return unbind function
    return () => this.off(event, callback);
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).delete(callback);
    }
  }

  emit(event, data) {
    if (this.listeners.has(event)) {
      for (const callback of this.listeners.get(event)) {
        try {
          callback(data);
        } catch (err) {
          console.error(`[WebSocket] Listener error for ${event}:`, err);
        }
      }
    }
  }

  send(action, payload = {}) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({ action, ...payload }));
    }
  }

  disconnect() {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    this.isConnected = false;
  }
}

export const wsService = new TelemetryWebSocketService();

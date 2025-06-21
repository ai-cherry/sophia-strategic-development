class WebSocketManager {
  constructor(url = (import.meta.env.VITE_WS_URL || 'ws://localhost:5001/ws')) {
    this.url = url;
    this.socket = null;
    this.listeners = new Set();
  }

  connect() {
    if (this.socket) {
      return this.socket;
    }
    this.socket = new WebSocket(this.url);
    this.socket.addEventListener('message', (e) => {
      let data;
      try { data = JSON.parse(e.data); } catch { data = e.data; }
      this.listeners.forEach((cb) => cb(data));
    });
    this.socket.addEventListener('close', () => {
      this.socket = null;
    });
    return this.socket;
  }

  subscribe(callback) {
    this.listeners.add(callback);
    this.connect();
  }

  unsubscribe(callback) {
    this.listeners.delete(callback);
    if (!this.listeners.size && this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}

export default new WebSocketManager();

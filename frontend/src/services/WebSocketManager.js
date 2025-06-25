// Environment-aware WebSocket URL configuration
const getWebSocketUrl = () => {
  // React environment variables (prefixed with REACT_APP_) for Vercel compatibility
  // Also support Vite environment variables (prefixed with VITE_) for local development
  const wsUrl = process.env.REACT_APP_WS_URL || import.meta.env.VITE_WS_URL;
  const apiUrl = process.env.REACT_APP_API_URL || import.meta.env.VITE_API_URL;
  const environment = process.env.REACT_APP_ENVIRONMENT || import.meta.env.VITE_ENVIRONMENT || import.meta.env.MODE || process.env.NODE_ENV;
  
  if (wsUrl) {
    return wsUrl;
  }
  
  if (apiUrl) {
    // Convert HTTP(S) URL to WebSocket URL
    return apiUrl.replace(/^https?:/, apiUrl.startsWith('https:') ? 'wss:' : 'ws:') + '/ws';
  }
  
  // Fallback URLs based on environment
  switch (environment) {
    case 'production':
      return 'wss://api.sophia.payready.com/ws';
    case 'staging':
      return 'wss://api.staging.sophia.payready.com/ws';
    case 'development':
    case 'dev':
      return 'wss://api.dev.sophia.payready.com/ws';
    default:
      // Local development fallback
      return 'ws://localhost:8000/ws';
  }
};

class WebSocketManager {
  constructor(url = getWebSocketUrl()) {
    this.url = url;
    this.socket = null;
    this.listeners = new Set();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000; // Start with 1 second
    this.isConnecting = false;
    
    console.log('WebSocketManager initialized with URL:', this.url);
  }

  connect() {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      return this.socket;
    }
    
    if (this.isConnecting) {
      return null;
    }
    
    this.isConnecting = true;
    
    try {
      this.socket = new WebSocket(this.url);
      
      this.socket.addEventListener('open', () => {
        console.log('WebSocket connected to:', this.url);
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        this.reconnectDelay = 1000;
      });
      
      this.socket.addEventListener('message', (e) => {
        let data;
        try { 
          data = JSON.parse(e.data); 
        } catch { 
          data = e.data; 
        }
        this.listeners.forEach((cb) => cb(data));
      });
      
      this.socket.addEventListener('close', (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        this.socket = null;
        this.isConnecting = false;
        
        // Attempt to reconnect if there are active listeners
        if (this.listeners.size > 0 && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.scheduleReconnect();
        }
      });
      
      this.socket.addEventListener('error', (error) => {
        console.error('WebSocket error:', error);
        this.isConnecting = false;
      });
      
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      this.isConnecting = false;
    }
    
    return this.socket;
  }

  scheduleReconnect() {
    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1); // Exponential backoff
    
    console.log(`Scheduling WebSocket reconnect attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${delay}ms`);
    
    setTimeout(() => {
      if (this.listeners.size > 0) {
        this.connect();
      }
    }, delay);
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

  send(data) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      const message = typeof data === 'string' ? data : JSON.stringify(data);
      this.socket.send(message);
      return true;
    } else {
      console.warn('WebSocket not connected, cannot send message:', data);
      return false;
    }
  }

  disconnect() {
    this.listeners.clear();
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}

export default WebSocketManager;

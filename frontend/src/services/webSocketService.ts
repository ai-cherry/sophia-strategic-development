/**
 * WebSocket Service for Real-time Updates
 * Replaces fixed polling with efficient real-time communication
 */

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: number;
}

export interface WebSocketConfig {
  url: string;
  reconnectInterval: number;
  maxRetries: number;
  heartbeatInterval: number;
}

class WebSocketService {
  private ws: WebSocket | null = null;
  private config: WebSocketConfig;
  private reconnectAttempts = 0;
  private heartbeatTimer: NodeJS.Timeout | null = null;
  private messageHandlers: Map<string, ((data: any) => void)[]> = new Map();
  private connectionState: 'connecting' | 'connected' | 'disconnected' | 'error' = 'disconnected';
  
  constructor(config: WebSocketConfig) {
    this.config = config;
  }
  
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.connectionState = 'connecting';
        this.ws = new WebSocket(this.config.url);
        
        this.ws.onopen = () => {
          console.log('🔗 WebSocket connected');
          this.connectionState = 'connected';
          this.reconnectAttempts = 0;
          this.startHeartbeat();
          resolve();
        };
        
        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('❌ WebSocket message parse error:', error);
          }
        };
        
        this.ws.onclose = () => {
          console.log('🔌 WebSocket disconnected');
          this.connectionState = 'disconnected';
          this.stopHeartbeat();
          this.handleReconnect();
        };
        
        this.ws.onerror = (error) => {
          console.error('❌ WebSocket error:', error);
          this.connectionState = 'error';
          reject(error);
        };
        
      } catch (error) {
        this.connectionState = 'error';
        reject(error);
      }
    });
  }
  
  private handleMessage(message: WebSocketMessage) {
    const handlers = this.messageHandlers.get(message.type) || [];
    handlers.forEach(handler => {
      try {
        handler(message.data);
      } catch (error) {
        console.error(`❌ Message handler error for type ${message.type}:`, error);
      }
    });
  }
  
  private handleReconnect() {
    if (this.reconnectAttempts < this.config.maxRetries) {
      this.reconnectAttempts++;
      const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
      
      console.log(`🔄 Reconnecting WebSocket in ${delay}ms (attempt ${this.reconnectAttempts})`);
      
      setTimeout(() => {
        this.connect().catch(error => {
          console.error('❌ WebSocket reconnection failed:', error);
        });
      }, delay);
    } else {
      console.error('❌ WebSocket max reconnection attempts reached');
    }
  }
  
  private startHeartbeat() {
    this.heartbeatTimer = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.send('ping', { timestamp: Date.now() });
      }
    }, this.config.heartbeatInterval);
  }
  
  private stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }
  
  send(type: string, data: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      const message: WebSocketMessage = {
        type,
        data,
        timestamp: Date.now()
      };
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('⚠️ WebSocket not connected, message not sent:', { type, data });
    }
  }
  
  subscribe(messageType: string, handler: (data: any) => void) {
    if (!this.messageHandlers.has(messageType)) {
      this.messageHandlers.set(messageType, []);
    }
    this.messageHandlers.get(messageType)!.push(handler);
    
    // Return unsubscribe function
    return () => {
      const handlers = this.messageHandlers.get(messageType);
      if (handlers) {
        const index = handlers.indexOf(handler);
        if (index > -1) {
          handlers.splice(index, 1);
        }
      }
    };
  }
  
  disconnect() {
    this.stopHeartbeat();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.connectionState = 'disconnected';
  }
  
  getConnectionState() {
    return this.connectionState;
  }
}

// Create singleton WebSocket service
const wsConfig: WebSocketConfig = {
  url: process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws',
  reconnectInterval: 5000,
  maxRetries: 10,
  heartbeatInterval: 30000
};

export const webSocketService = new WebSocketService(wsConfig);

// Auto-connect on module load
webSocketService.connect().catch(error => {
  console.error('❌ Initial WebSocket connection failed:', error);
});

export default webSocketService;

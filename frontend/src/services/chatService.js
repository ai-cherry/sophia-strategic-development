import apiClient from './apiClient';

/**
 * Enhanced Chat Service with robust WebSocket connectivity
 * Addresses all chat disconnection issues with auto-reconnection
 */
class ChatService {
  constructor() {
    this.ws = null;
    this.isConnected = false;
    this.isConnecting = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000; // Start with 1 second
    this.userId = null;
    this.sessionId = null;
    
    // Event handlers
    this.onMessage = null;
    this.onStatusChange = null;
    this.onError = null;
    
    // Connection status
    this.status = 'disconnected'; // disconnected, connecting, connected, error
    
    // Message queue for offline messages
    this.messageQueue = [];
    
    // Heartbeat
    this.heartbeatInterval = null;
    this.heartbeatTimeout = null;
  }

  /**
   * Initialize chat service
   */
  initialize(userId, sessionId = null) {
    this.userId = userId;
    this.sessionId = sessionId || this.generateSessionId();
    this.connect();
  }

  /**
   * Generate unique session ID
   */
  generateSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Get WebSocket URL
   */
  getWebSocketUrl() {
    const baseUrl = apiClient.getApiUrl();
    const wsUrl = baseUrl.replace('http://', 'ws://').replace('https://', 'wss://');
    return `${wsUrl}/ws/chat/${this.userId}`;
  }

  /**
   * Connect to WebSocket
   */
  connect() {
    if (this.isConnecting || this.isConnected) {
      return;
    }

    this.isConnecting = true;
    this.updateStatus('connecting');

    try {
      const wsUrl = this.getWebSocketUrl();
      console.log('[Chat] Connecting to:', wsUrl);
      
      this.ws = new WebSocket(wsUrl);
      
      this.ws.onopen = this.handleOpen.bind(this);
      this.ws.onmessage = this.handleMessage.bind(this);
      this.ws.onclose = this.handleClose.bind(this);
      this.ws.onerror = this.handleError.bind(this);
      
      // Connection timeout
      setTimeout(() => {
        if (this.isConnecting && !this.isConnected) {
          console.warn('[Chat] Connection timeout');
          this.ws?.close();
          this.handleConnectionFailure();
        }
      }, 10000);
      
    } catch (error) {
      console.error('[Chat] Connection error:', error);
      this.handleConnectionFailure();
    }
  }

  /**
   * Handle WebSocket open
   */
  handleOpen(event) {
    console.log('[Chat] Connected successfully');
    this.isConnected = true;
    this.isConnecting = false;
    this.reconnectAttempts = 0;
    this.updateStatus('connected');
    
    // Send authentication message
    this.sendAuthMessage();
    
    // Start heartbeat
    this.startHeartbeat();
    
    // Process queued messages
    this.processMessageQueue();
  }

  /**
   * Handle WebSocket message
   */
  handleMessage(event) {
    try {
      const data = JSON.parse(event.data);
      
      // Handle different message types
      switch (data.type) {
        case 'auth_success':
          console.log('[Chat] Authentication successful');
          break;
        case 'auth_error':
          console.error('[Chat] Authentication failed:', data.message);
          this.updateStatus('error');
          break;
        case 'message':
          this.handleChatMessage(data);
          break;
        case 'pong':
          this.handlePong();
          break;
        case 'error':
          console.error('[Chat] Server error:', data.message);
          if (this.onError) {
            this.onError(new Error(data.message));
          }
          break;
        default:
          console.warn('[Chat] Unknown message type:', data.type);
      }
    } catch (error) {
      console.error('[Chat] Failed to parse message:', error);
    }
  }

  /**
   * Handle chat message
   */
  handleChatMessage(data) {
    if (this.onMessage) {
      this.onMessage({
        id: data.id || Date.now(),
        message: data.message,
        sender: data.sender || 'sophia',
        timestamp: data.timestamp || new Date().toISOString(),
        type: data.messageType || 'text',
        metadata: data.metadata || {}
      });
    }
  }

  /**
   * Handle WebSocket close
   */
  handleClose(event) {
    console.log('[Chat] Connection closed:', event.code, event.reason);
    this.isConnected = false;
    this.isConnecting = false;
    this.stopHeartbeat();
    
    // Attempt reconnection if not intentional
    if (event.code !== 1000) {
      this.scheduleReconnect();
    } else {
      this.updateStatus('disconnected');
    }
  }

  /**
   * Handle WebSocket error
   */
  handleError(event) {
    console.error('[Chat] WebSocket error:', event);
    this.updateStatus('error');
    
    if (this.onError) {
      this.onError(new Error('WebSocket connection error'));
    }
  }

  /**
   * Handle connection failure
   */
  handleConnectionFailure() {
    this.isConnecting = false;
    this.isConnected = false;
    this.updateStatus('error');
    this.scheduleReconnect();
  }

  /**
   * Schedule reconnection with exponential backoff
   */
  scheduleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[Chat] Max reconnection attempts reached');
      this.updateStatus('error');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    
    console.log(`[Chat] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
    this.updateStatus('connecting');
    
    setTimeout(() => {
      this.connect();
    }, delay);
  }

  /**
   * Send authentication message
   */
  sendAuthMessage() {
    this.sendRawMessage({
      type: 'auth',
      userId: this.userId,
      sessionId: this.sessionId,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Start heartbeat to keep connection alive
   */
  startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      if (this.isConnected) {
        this.sendRawMessage({ type: 'ping' });
        
        // Set timeout for pong response
        this.heartbeatTimeout = setTimeout(() => {
          console.warn('[Chat] Heartbeat timeout, reconnecting...');
          this.ws?.close();
        }, 5000);
      }
    }, 30000); // Send ping every 30 seconds
  }

  /**
   * Stop heartbeat
   */
  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
    if (this.heartbeatTimeout) {
      clearTimeout(this.heartbeatTimeout);
      this.heartbeatTimeout = null;
    }
  }

  /**
   * Handle pong response
   */
  handlePong() {
    if (this.heartbeatTimeout) {
      clearTimeout(this.heartbeatTimeout);
      this.heartbeatTimeout = null;
    }
  }

  /**
   * Send raw message to WebSocket
   */
  sendRawMessage(data) {
    if (this.isConnected && this.ws?.readyState === WebSocket.OPEN) {
      try {
        this.ws.send(JSON.stringify(data));
        return true;
      } catch (error) {
        console.error('[Chat] Failed to send message:', error);
        return false;
      }
    }
    return false;
  }

  /**
   * Send chat message
   */
  async sendMessage(message, context = {}) {
    const messageData = {
      type: 'message',
      message,
      userId: this.userId,
      sessionId: this.sessionId,
      context,
      timestamp: new Date().toISOString()
    };

    // Try WebSocket first
    if (this.sendRawMessage(messageData)) {
      return { success: true, method: 'websocket' };
    }

    // Fallback to HTTP API
    try {
      const response = await apiClient.sendChatMessage(
        message,
        this.userId,
        this.sessionId,
        context
      );
      
      // Simulate message event for consistency
      if (this.onMessage && response.message) {
        this.handleChatMessage({
          id: response.id,
          message: response.message,
          sender: 'sophia',
          timestamp: response.timestamp,
          messageType: response.type,
          metadata: response.metadata
        });
      }
      
      return { success: true, method: 'http', data: response };
    } catch (error) {
      // Queue message for later if both methods fail
      this.messageQueue.push(messageData);
      throw error;
    }
  }

  /**
   * Process queued messages
   */
  processMessageQueue() {
    while (this.messageQueue.length > 0 && this.isConnected) {
      const message = this.messageQueue.shift();
      this.sendRawMessage(message);
    }
  }

  /**
   * Update connection status
   */
  updateStatus(status) {
    if (this.status !== status) {
      this.status = status;
      console.log(`[Chat] Status changed to: ${status}`);
      
      if (this.onStatusChange) {
        this.onStatusChange(status);
      }
    }
  }

  /**
   * Set event handlers
   */
  setEventHandlers({ onMessage, onStatusChange, onError }) {
    this.onMessage = onMessage;
    this.onStatusChange = onStatusChange;
    this.onError = onError;
  }

  /**
   * Get current status
   */
  getStatus() {
    return this.status;
  }

  /**
   * Disconnect
   */
  disconnect() {
    this.stopHeartbeat();
    if (this.ws) {
      this.ws.close(1000, 'User disconnected');
      this.ws = null;
    }
    this.isConnected = false;
    this.isConnecting = false;
    this.updateStatus('disconnected');
  }

  /**
   * Reconnect manually
   */
  reconnect() {
    this.disconnect();
    this.reconnectAttempts = 0;
    setTimeout(() => this.connect(), 1000);
  }
}

// Create singleton instance
const chatService = new ChatService();

export default chatService;


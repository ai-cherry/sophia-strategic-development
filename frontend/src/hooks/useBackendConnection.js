import { useState, useEffect, useCallback } from 'react';
import { checkConnection, createWebSocketConnection } from '../services/apiClient';

// Custom hook for managing backend connection status
export const useBackendConnection = () => {
  const [connectionStatus, setConnectionStatus] = useState({
    connected: false,
    status: 'checking',
    error: null,
    latency: null,
    lastChecked: null
  });
  
  const [websocket, setWebsocket] = useState(null);
  const [wsStatus, setWsStatus] = useState('disconnected');

  // Check backend connection
  const checkBackendConnection = useCallback(async () => {
    try {
      setConnectionStatus(prev => ({ ...prev, status: 'checking' }));
      
      const result = await checkConnection();
      
      setConnectionStatus({
        connected: result.connected,
        status: result.connected ? 'connected' : 'disconnected',
        error: result.error || null,
        latency: result.latency,
        lastChecked: new Date()
      });
      
      return result;
    } catch (error) {
      setConnectionStatus({
        connected: false,
        status: 'error',
        error: error.message,
        latency: null,
        lastChecked: new Date()
      });
      
      return { connected: false, error: error.message };
    }
  }, []);

  // Initialize WebSocket connection
  const connectWebSocket = useCallback(() => {
    if (websocket) {
      websocket.close();
    }

    const ws = createWebSocketConnection();
    
    if (ws) {
      ws.onopen = () => {
        setWsStatus('connected');
        console.log('✅ WebSocket connected');
      };
      
      ws.onclose = () => {
        setWsStatus('disconnected');
        console.log('❌ WebSocket disconnected');
        
        // Attempt to reconnect after 5 seconds
        setTimeout(() => {
          if (connectionStatus.connected) {
            connectWebSocket();
          }
        }, 5000);
      };
      
      ws.onerror = (error) => {
        setWsStatus('error');
        console.error('❌ WebSocket error:', error);
      };
      
      setWebsocket(ws);
    } else {
      setWsStatus('error');
    }
  }, [websocket, connectionStatus.connected]);

  // Send WebSocket message
  const sendWebSocketMessage = useCallback((message) => {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      websocket.send(JSON.stringify(message));
      return true;
    }
    return false;
  }, [websocket]);

  // Initial connection check
  useEffect(() => {
    checkBackendConnection();
    
    // Set up periodic connection checks every 30 seconds
    const interval = setInterval(checkBackendConnection, 30000);
    
    return () => clearInterval(interval);
  }, [checkBackendConnection]);

  // Initialize WebSocket when backend is connected
  useEffect(() => {
    if (connectionStatus.connected && wsStatus === 'disconnected') {
      connectWebSocket();
    }
  }, [connectionStatus.connected, wsStatus, connectWebSocket]);

  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      if (websocket) {
        websocket.close();
      }
    };
  }, [websocket]);

  return {
    // Connection status
    ...connectionStatus,
    
    // WebSocket status
    wsStatus,
    websocket,
    
    // Methods
    checkConnection: checkBackendConnection,
    connectWebSocket,
    sendWebSocketMessage,
    
    // Computed properties
    isHealthy: connectionStatus.connected && connectionStatus.status === 'connected',
    isWebSocketReady: wsStatus === 'connected'
  };
};

export default useBackendConnection;


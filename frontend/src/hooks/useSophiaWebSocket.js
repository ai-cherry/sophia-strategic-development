import { useState, useEffect, useRef, useCallback } from 'react';
import sophiaApiService from '../services/SophiaApiService';

/**
 * Enhanced WebSocket Hook for Sophia AI Chat
 * Integrates with the existing backend WebSocket infrastructure
 */
export const useSophiaWebSocket = (userId = 'ceo', dashboardType = 'executive') => {
  // State management
  const [messages, setMessages] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [error, setError] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [typingIndicator, setTypingIndicator] = useState(false);
  
  // Refs
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  // Initialize chat session
  const initializeChat = useCallback(async () => {
    try {
      setIsConnecting(true);
      
      // Create session - try multiple endpoints for compatibility
      let session;
      try {
        session = await sophiaApiService.createChatSession(userId, dashboardType);
      } catch (e) {
        // Fallback to direct session creation
        session = { session_id: `${userId}_${Date.now()}` };
      }
      
      setSessionId(session.session_id);
      
      // Add welcome message
      const welcomeMessage = {
        id: 'welcome-' + Date.now(),
        role: 'assistant',
        content: `Hello! I'm Sophia, your AI assistant ready to help with your ${dashboardType} dashboard. I have access to your company data and can provide real-time insights.`,
        timestamp: new Date().toISOString()
      };
      
      setMessages([welcomeMessage]);
      
    } catch (error) {
      console.error('Failed to initialize chat:', error);
      setError('Failed to initialize chat: ' + error.message);
    } finally {
      setIsConnecting(false);
    }
  }, [userId, dashboardType]);

  // WebSocket connection management
  const connectWebSocket = useCallback(() => {
    if (!sessionId || (wsRef.current?.readyState === WebSocket.OPEN)) {
      return;
    }

    setIsConnecting(true);
    setConnectionStatus('connecting');

    try {
      // Use the existing backend WebSocket endpoint
      const wsUrl = `${sophiaApiService.wsURL}/ws/chat/${userId}`;
      console.log('Connecting to WebSocket:', wsUrl);
      
      const ws = new WebSocket(wsUrl);
      
      ws.onopen = () => {
        console.log('WebSocket connected to Sophia AI');
        setIsConnected(true);
        setIsConnecting(false);
        setConnectionStatus('connected');
        setError(null);
        reconnectAttempts.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleWebSocketMessage(data);
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        setIsConnected(false);
        setIsConnecting(false);
        setConnectionStatus('disconnected');
        
        // Auto-reconnect with exponential backoff
        if (reconnectAttempts.current < maxReconnectAttempts) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
          reconnectAttempts.current++;
          
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log(`Reconnecting... Attempt ${reconnectAttempts.current}/${maxReconnectAttempts}`);
            connectWebSocket();
          }, delay);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('disconnected');
        setError('Connection error. Retrying...');
      };

      wsRef.current = ws;
    } catch (err) {
      console.error('Failed to create WebSocket connection:', err);
      setConnectionStatus('disconnected');
      setError('Failed to connect: ' + err.message);
      setIsConnecting(false);
    }
  }, [sessionId, userId]);

  // Handle incoming WebSocket messages
  const handleWebSocketMessage = useCallback((data) => {
    console.log('WebSocket message received:', data);
    
    // Handle the response format from the existing backend
    if (data.content) {
      const assistantMessage = {
        id: Date.now().toString(),
        role: 'assistant',
        content: data.content,
        timestamp: data.timestamp || new Date().toISOString(),
        sources: data.sources || []
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      setTypingIndicator(false);
    }
  }, []);

  // Send message function
  const sendMessage = useCallback((content, options = {}) => {
    if (!content.trim() || !isConnected) {
      console.warn('Cannot send message: not connected or empty content');
      return false;
    }

    // Add user message to UI immediately
    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setTypingIndicator(true);
    setError(null);

    // Send via WebSocket using the existing backend format
    try {
      const message = {
        content: content.trim(),
        session_id: sessionId,
        user_id: userId
      };

      wsRef.current.send(JSON.stringify(message));
      return true;
    } catch (err) {
      console.error('Failed to send message:', err);
      setError('Failed to send message: ' + err.message);
      setTypingIndicator(false);
      return false;
    }
  }, [isConnected, sessionId, userId]);

  // Clear chat
  const clearChat = useCallback(() => {
    setMessages([]);
    setError(null);
    setTypingIndicator(false);
  }, []);

  // Disconnect
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    if (wsRef.current) {
      wsRef.current.close(1000, 'User disconnect');
    }
    
    setIsConnected(false);
    setConnectionStatus('disconnected');
  }, []);

  // Initialize on mount
  useEffect(() => {
    initializeChat();
    
    return () => {
      disconnect();
    };
  }, [initializeChat, disconnect]);

  // Connect WebSocket when session is ready
  useEffect(() => {
    if (sessionId && !isConnected && !isConnecting) {
      connectWebSocket();
    }
  }, [sessionId, isConnected, isConnecting, connectWebSocket]);

  return {
    // Connection state
    isConnected,
    isConnecting,
    connectionStatus,
    error,
    sessionId,
    
    // Messages and indicators
    messages,
    typingIndicator,
    
    // Actions
    sendMessage,
    clearChat,
    disconnect,
    setError
  };
};

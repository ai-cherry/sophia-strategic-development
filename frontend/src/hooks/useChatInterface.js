import { useState, useEffect, useCallback } from 'react';
import { api } from '../services/apiClient';
import { useBackendConnection } from './useBackendConnection';

// Custom hook for chat interface functionality
export const useChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [inputValue, setInputValue] = useState('');
  
  const { isHealthy, isWebSocketReady, sendWebSocketMessage } = useBackendConnection();

  // Load chat history on mount
  useEffect(() => {
    if (isHealthy) {
      loadChatHistory();
    }
  }, [isHealthy]);

  // Load chat history from backend
  const loadChatHistory = useCallback(async () => {
    try {
      const response = await api.chat.getHistory();
      setMessages(response.data.messages || []);
    } catch (error) {
      console.error('Failed to load chat history:', error);
      // Don't show error for history loading failure
    }
  }, []);

  // Send message via API or WebSocket
  const sendMessage = useCallback(async (message) => {
    if (!message.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date()
    };

    // Add user message immediately
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setError(null);

    try {
      let response;
      
      // Try WebSocket first if available
      if (isWebSocketReady) {
        const wsMessage = {
          type: 'chat_message',
          content: message,
          timestamp: new Date().toISOString()
        };
        
        const sent = sendWebSocketMessage(wsMessage);
        if (!sent) {
          throw new Error('WebSocket not available');
        }
        
        // For WebSocket, we'll handle the response in the WebSocket message handler
        // For now, add a placeholder response
        response = {
          data: {
            message: 'Message sent via WebSocket. Response handling in progress...',
            id: Date.now() + 1
          }
        };
      } else {
        // Fallback to HTTP API
        response = await api.chat.sendMessage(message);
      }

      const aiMessage = {
        id: response.data.id || Date.now() + 1,
        type: 'assistant',
        content: response.data.message || 'I received your message but encountered an issue generating a response.',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: `Sorry, I couldn't process your message: ${error.message}`,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  }, [isWebSocketReady, sendWebSocketMessage]);

  // Clear chat history
  const clearChat = useCallback(async () => {
    try {
      await api.chat.clearHistory();
      setMessages([]);
      setError(null);
    } catch (error) {
      console.error('Failed to clear chat:', error);
      setError('Failed to clear chat history');
    }
  }, []);

  // Add system message
  const addSystemMessage = useCallback((content) => {
    const systemMessage = {
      id: Date.now(),
      type: 'system',
      content,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, systemMessage]);
  }, []);

  // Handle input change
  const handleInputChange = useCallback((value) => {
    setInputValue(value);
    setError(null);
  }, []);

  // Handle form submission
  const handleSubmit = useCallback((e) => {
    e.preventDefault();
    sendMessage(inputValue);
  }, [inputValue, sendMessage]);

  // Connection status message
  const getConnectionStatus = useCallback(() => {
    if (!isHealthy) {
      return 'Backend disconnected';
    }
    if (isWebSocketReady) {
      return 'Connected (Real-time)';
    }
    return 'Connected (HTTP)';
  }, [isHealthy, isWebSocketReady]);

  // Get connection status color
  const getConnectionStatusColor = useCallback(() => {
    if (!isHealthy) {
      return 'text-red-400';
    }
    if (isWebSocketReady) {
      return 'text-green-400';
    }
    return 'text-yellow-400';
  }, [isHealthy, isWebSocketReady]);

  return {
    // State
    messages,
    isLoading,
    error,
    inputValue,
    
    // Connection status
    connectionStatus: getConnectionStatus(),
    connectionStatusColor: getConnectionStatusColor(),
    isConnected: isHealthy,
    
    // Actions
    sendMessage,
    clearChat,
    addSystemMessage,
    handleInputChange,
    handleSubmit,
    
    // Computed properties
    canSendMessage: isHealthy && !isLoading && inputValue.trim().length > 0,
    hasMessages: messages.length > 0
  };
};

export default useChatInterface;


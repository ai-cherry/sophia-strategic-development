import React, { useState, useEffect, useRef, useCallback } from 'react';
import apiClient from '../../services/apiClient';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Card, CardContent } from '../ui/card';
import { Loader2, Send, AlertCircle, Wifi, WifiOff, FileText, Upload } from 'lucide-react';

/**
 * Sophia Live Chat Interface Component
 * Integrates with our enhanced dashboard UI and backend WebSocket infrastructure
 */
const SophiaLiveChatInterface = ({ 
  userId = 'ceo_user', 
  onUpload, 
  className = '',
  context = 'ceo_dashboard' 
}) => {
  // State management
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [connectionStatus, setConnectionStatus] = useState('connecting'); // connecting, connected, disconnected, error
  const [isTyping, setIsTyping] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [connectionError, setConnectionError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);

  // Refs
  const wsRef = useRef(null);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  // Connection management
  useEffect(() => {
    connectWebSocket();
    
    // Cleanup on unmount
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [userId]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const connectWebSocket = useCallback(() => {
    setConnectionStatus('connecting');
    setConnectionError(null);

    // Clear any existing connection
    if (wsRef.current) {
      wsRef.current.close();
    }

    // Create new WebSocket connection
    wsRef.current = apiClient.createWebSocketConnection(
      userId,
      handleMessage,
      handleError,
      handleClose,
      handleOpen
    );
  }, [userId]);

  const handleOpen = useCallback((event) => {
    console.log('Chat WebSocket connected');
    setConnectionStatus('connected');
    setConnectionError(null);
    setRetryCount(0);
    
    // Send initial welcome message
    const welcomeMessage = {
      id: Date.now(),
      text: "Hello! I'm Sophia, your AI assistant. How can I help you today?",
      sender: 'sophia',
      timestamp: new Date(),
      type: 'welcome'
    };
    setMessages(prev => [...prev, welcomeMessage]);
  }, []);

  const handleMessage = useCallback((data) => {
    setIsTyping(false);
    
    if (data.type === 'error') {
      // Handle error messages from the server
      const errorMessage = {
        id: Date.now(),
        text: data.content || 'An error occurred while processing your message.',
        sender: 'system',
        timestamp: new Date(),
        type: 'error'
      };
      setMessages(prev => [...prev, errorMessage]);
      return;
    }

    if (data.type === 'message' || data.content) {
      const message = {
        id: data.id || Date.now(),
        text: data.content || data.message || data.text,
        sender: 'sophia',
        timestamp: new Date(data.timestamp || Date.now()),
        sources: data.sources || [],
        metadata: data.metadata || {}
      };
      setMessages(prev => [...prev, message]);
    }
  }, []);

  const handleError = useCallback((error) => {
    console.error('Chat WebSocket error:', error);
    setConnectionStatus('error');
    setConnectionError(error.message || 'Connection error occurred');
    
    // Show error message to user
    const errorMessage = {
      id: Date.now(),
      text: 'Connection error. Attempting to reconnect...',
      sender: 'system',
      timestamp: new Date(),
      type: 'error'
    };
    setMessages(prev => [...prev, errorMessage]);
  }, []);

  const handleClose = useCallback((event) => {
    console.log('Chat WebSocket closed:', event);
    setConnectionStatus('disconnected');
    setIsTyping(false);
    
    // Only show reconnection message if it wasn't intentional
    if (event.code !== 1000) { // 1000 = normal closure
      setRetryCount(prev => prev + 1);
      
      const reconnectMessage = {
        id: Date.now(),
        text: 'Connection lost. Attempting to reconnect...',
        sender: 'system',
        timestamp: new Date(),
        type: 'reconnect'
      };
      setMessages(prev => [...prev, reconnectMessage]);
    }
  }, []);

  const sendMessage = async () => {
    if (!newMessage.trim() || isSending) return;

    const messageText = newMessage.trim();
    setNewMessage('');
    setIsSending(true);

    // Add user message immediately
    const userMessage = {
      id: Date.now(),
      text: messageText,
      sender: 'user',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);

    try {
      // Show typing indicator
      setIsTyping(true);

      // Try WebSocket first if connected
      if (wsRef.current && connectionStatus === 'connected') {
        const sent = wsRef.current.send({
          type: 'message',
          content: messageText,
          user_id: userId,
          context: context
        });

        if (!sent) {
          // Fallback to HTTP API
          throw new Error('WebSocket not available');
        }
      } else {
        // Fallback to HTTP API
        const result = await apiClient.sendChatMessage(messageText, userId);
        
        if (!result.success) {
          throw new Error(result.error);
        }

        // Handle HTTP response
        if (result.data && result.data.response) {
          const sophiaMessage = {
            id: Date.now() + 1,
            text: result.data.response,
            sender: 'sophia',
            timestamp: new Date(),
            sources: result.data.sources || []
          };
          setMessages(prev => [...prev, sophiaMessage]);
        }
        
        setIsTyping(false);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      setIsTyping(false);
      
      // Show error message
      const errorMessage = {
        id: Date.now() + 2,
        text: 'Failed to send message. Please try again.',
        sender: 'system',
        timestamp: new Date(),
        type: 'error'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsSending(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsUploading(true);
    
    try {
      // Add upload status message
      const uploadMessage = {
        id: Date.now(),
        text: `📎 Uploading ${file.name}...`,
        sender: 'system',
        timestamp: new Date(),
        type: 'upload'
      };
      setMessages(prev => [...prev, uploadMessage]);

      const result = await apiClient.uploadFile(file, 'document', context);
      
      if (!result.success) {
        throw new Error(result.error);
      }

      // Success message
      const successMessage = {
        id: Date.now() + 1,
        text: `✅ Successfully uploaded ${file.name}`,
        sender: 'system',
        timestamp: new Date(),
        type: 'upload_success'
      };
      setMessages(prev => [...prev, successMessage]);
      
      if (onUpload) {
        onUpload(result.data);
      }

    } catch (error) {
      console.error('Upload failed:', error);
      
      // Error message
      const errorMessage = {
        id: Date.now() + 2,
        text: `❌ Upload failed: ${error.message}`,
        sender: 'system',
        timestamp: new Date(),
        type: 'upload_error'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsUploading(false);
      // Clear the file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  const retryConnection = () => {
    connectWebSocket();
  };

  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return 'bg-green-500';
      case 'connecting': return 'bg-yellow-500';
      case 'disconnected': return 'bg-orange-500';
      case 'error': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getConnectionStatusText = () => {
    switch (connectionStatus) {
      case 'connected': return 'Connected';
      case 'connecting': return 'Connecting...';
      case 'disconnected': return 'Disconnected';
      case 'error': return 'Connection Error';
      default: return 'Unknown';
    }
  };

  const getMessageTypeClass = (message) => {
    switch (message.type) {
      case 'error':
      case 'upload_error':
        return 'bg-red-500/20 border-red-500/30 text-red-100';
      case 'upload':
        return 'bg-blue-500/20 border-blue-500/30 text-blue-100';
      case 'upload_success':
        return 'bg-green-500/20 border-green-500/30 text-green-100';
      case 'reconnect':
        return 'bg-yellow-500/20 border-yellow-500/30 text-yellow-100';
      case 'welcome':
        return 'bg-purple-500/20 border-purple-500/30 text-purple-100';
      default:
        return message.sender === 'user' 
          ? 'bg-blue-600 text-white' 
          : 'bg-white/20 text-white';
    }
  };

  // Loading state
  if (connectionStatus === 'connecting' && messages.length === 0) {
    return (
      <Card className={`${className} flex flex-col`}>
        <CardContent className="flex items-center justify-center h-full">
          <div className="text-center">
            <Loader2 className="w-8 h-8 animate-spin text-pr-primary-blue mx-auto mb-2" />
            <p className="text-text-secondary">Initializing Sophia AI...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={`${className} flex flex-col`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border-interactive">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-full bg-pr-primary-blue text-white flex items-center justify-center text-sm font-medium">
            S
          </div>
          <div>
            <h3 className="font-medium text-text-primary">Sophia AI</h3>
            <p className="text-xs text-text-secondary capitalize">Your Executive Assistant</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <div className={`w-2 h-2 rounded-full ${getConnectionStatusColor()}`}></div>
          <span className="text-xs text-text-tertiary">{getConnectionStatusText()}</span>
          {connectionStatus !== 'connected' && connectionStatus !== 'connecting' && (
            <button
              onClick={retryConnection}
              className="text-xs text-blue-400 hover:text-blue-300 underline ml-2"
            >
              Retry
            </button>
          )}
        </div>
      </div>

      {/* Messages Area */}
      <CardContent className="flex-1 overflow-y-auto p-4 space-y-0">
        {messages.length === 0 && connectionStatus !== 'connected' && connectionStatus !== 'connecting' && (
          <div className="text-center text-text-tertiary py-8">
            <div className="w-16 h-16 rounded-full bg-pr-primary-blue bg-opacity-10 flex items-center justify-center mx-auto mb-4">
              <div className="w-8 h-8 rounded-full bg-pr-primary-blue text-white flex items-center justify-center text-sm font-medium">
                S
              </div>
            </div>
            <p className="mb-2">Start a conversation with Sophia AI</p>
            <p className="text-sm">Ask about your business data, upload documents, or get insights</p>
          </div>
        )}
        
        {messages.map((message) => (
          <div 
            key={message.id} 
            className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg border ${getMessageTypeClass(message)}`}>
              <p className="text-sm whitespace-pre-wrap">{message.text}</p>
              
              {message.sources && message.sources.length > 0 && (
                <div className="mt-2 text-xs opacity-70 border-t border-current/20 pt-2">
                  <strong>Sources:</strong> {message.sources.join(', ')}
                </div>
              )}
              
              <div className="text-xs opacity-70 mt-1">
                {message.timestamp.toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
        
        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-surface-elevated text-text-secondary rounded-lg px-4 py-3 flex items-center space-x-2">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span className="text-sm">Sophia is typing...</span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </CardContent>

      {/* Error Display */}
      {connectionError && (
        <div className="px-4 py-2 bg-red-50 border-t border-red-200">
          <div className="flex items-center space-x-2 text-red-700">
            <AlertCircle className="w-4 h-4" />
            <span className="text-sm">{connectionError}</span>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setConnectionError(null)}
              className="ml-auto text-red-600 hover:text-red-800"
            >
              ×
            </Button>
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="border-t border-border-interactive p-4">
        <div className="flex space-x-2">
          <Input
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask Sophia anything..."
            disabled={isSending}
            className="flex-1"
          />
          
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            className="hidden"
            accept=".pdf,.doc,.docx,.txt,.md,.csv,.xlsx"
          />
          
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="bg-purple-600 hover:bg-purple-700 text-white px-3 py-2 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            title="Upload file"
          >
            {isUploading ? (
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
            ) : (
              '📎'
            )}
          </button>
          
          <button
            onClick={sendMessage}
            disabled={!newMessage.trim() || isSending}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSending ? (
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
            ) : (
              'Send'
            )}
          </button>
        </div>
        
        <div className="flex justify-between items-center mt-2 text-xs text-text-tertiary">
          <span>Press Enter to send, Shift+Enter for new line</span>
          {connectionStatus === 'connected' && <span>• Ready to assist</span>}
        </div>
      </div>
    </Card>
  );
};

export default SophiaLiveChatInterface;

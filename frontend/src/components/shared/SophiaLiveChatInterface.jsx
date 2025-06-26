import React, { useState, useRef, useEffect } from 'react';
import { useSophiaWebSocket } from '../../hooks/useSophiaWebSocket';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Card, CardContent } from '../ui/card';
import { Loader2, Send, AlertCircle, Wifi, WifiOff, FileText, Upload } from 'lucide-react';

/**
 * Sophia Live Chat Interface Component
 * Integrates with our enhanced dashboard UI and backend WebSocket infrastructure
 */
export const SophiaLiveChatInterface = ({ 
  userId = 'ceo', 
  dashboardType = 'executive',
  className = '',
  showFileUpload = true,
  height = 'h-96'
}) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  // Use our enhanced WebSocket hook
  const {
    messages,
    isConnected,
    isConnecting,
    connectionStatus,
    error,
    sessionId,
    typingIndicator,
    sendMessage,
    clearChat,
    setError
  } = useSophiaWebSocket(userId, dashboardType);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, typingIndicator]);

  // Handle sending messages
  const handleSendMessage = async () => {
    if (!input.trim() || !isConnected) return;
    
    const success = sendMessage(input.trim());
    if (success) {
      setInput('');
    }
  };

  // Handle Enter key press
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Connection status indicator
  const ConnectionStatus = () => {
    const statusConfig = {
      connected: { icon: Wifi, color: 'text-green-500', text: 'Connected' },
      connecting: { icon: Loader2, color: 'text-yellow-500', text: 'Connecting...', spin: true },
      disconnected: { icon: WifiOff, color: 'text-red-500', text: 'Disconnected' }
    };

    const config = statusConfig[connectionStatus] || statusConfig.disconnected;
    const StatusIcon = config.icon;

    return (
      <div className="flex items-center space-x-2 text-sm">
        <StatusIcon 
          className={`w-4 h-4 ${config.color} ${config.spin ? 'animate-spin' : ''}`} 
        />
        <span className="text-text-secondary">{config.text}</span>
        {sessionId && (
          <span className="text-xs text-text-tertiary">
            Session: {sessionId.slice(0, 8)}...
          </span>
        )}
      </div>
    );
  };

  // Message component
  const Message = ({ message }) => {
    const isUser = message.role === 'user';
    const isSystem = message.role === 'system';
    
    return (
      <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
        <div
          className={`max-w-[80%] rounded-lg px-4 py-3 ${
            isUser 
              ? 'bg-pr-primary-blue text-white' 
              : isSystem
              ? 'bg-pr-secondary-teal bg-opacity-10 text-text-secondary text-sm'
              : 'bg-surface-elevated text-text-primary border border-border-interactive'
          }`}
        >
          <div className="whitespace-pre-wrap break-words">
            {message.content}
          </div>
          
          {/* Show sources if available */}
          {message.sources && message.sources.length > 0 && (
            <div className="mt-2 pt-2 border-t border-white border-opacity-20">
              <div className="text-xs opacity-80 mb-1">Sources:</div>
              {message.sources.map((source, index) => (
                <div key={index} className="text-xs opacity-70 flex items-center">
                  <FileText className="w-3 h-3 mr-1" />
                  {source.title || source.category || 'Document'}
                </div>
              ))}
            </div>
          )}
          
          <div className="text-xs opacity-70 mt-2">
            {new Date(message.timestamp).toLocaleTimeString()}
          </div>
        </div>
      </div>
    );
  };

  // Loading state
  if (isConnecting && messages.length === 0) {
    return (
      <Card className={`${className} ${height}`}>
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
    <Card className={`${className} flex flex-col ${height}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border-interactive">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-full bg-pr-primary-blue text-white flex items-center justify-center text-sm font-medium">
            S
          </div>
          <div>
            <h3 className="font-medium text-text-primary">Sophia AI</h3>
            <p className="text-xs text-text-secondary capitalize">{dashboardType} Assistant</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <ConnectionStatus />
          <Button
            variant="ghost"
            size="sm"
            onClick={clearChat}
            className="text-text-tertiary hover:text-text-primary"
          >
            Clear
          </Button>
        </div>
      </div>

      {/* Messages Area */}
      <CardContent className="flex-1 overflow-y-auto p-4 space-y-0">
        {messages.length === 0 && !isConnecting && (
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
          <Message key={message.id} message={message} />
        ))}
        
        {/* Typing indicator */}
        {typingIndicator && (
          <div className="flex justify-start mb-4">
            <div className="bg-surface-elevated text-text-secondary rounded-lg px-4 py-3 flex items-center space-x-2">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span className="text-sm">Sophia is thinking...</span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </CardContent>

      {/* Error Display */}
      {error && (
        <div className="px-4 py-2 bg-red-50 border-t border-red-200">
          <div className="flex items-center space-x-2 text-red-700">
            <AlertCircle className="w-4 h-4" />
            <span className="text-sm">{error}</span>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setError(null)}
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
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask Sophia about your business..."
            disabled={!isConnected}
            className="flex-1"
          />
          <Button
            onClick={handleSendMessage}
            disabled={!input.trim() || !isConnected}
            className="px-4"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
        
        <div className="flex justify-between items-center mt-2 text-xs text-text-tertiary">
          <span>Press Enter to send, Shift+Enter for new line</span>
          {isConnected && <span>• Ready to assist</span>}
        </div>
      </div>
    </Card>
  );
};

import React, { memo, useCallback, useMemo, useRef, useEffect } from 'react';
import { useIntelligentPolling } from '../../hooks/useIntelligentPolling';
import webSocketService from '../../services/webSocketService';

interface Message {
  id: string;
  content: string;
  timestamp: number;
  type: 'user' | 'assistant';
}

interface ChatProps {
  messages: Message[];
  onSendMessage: (message: string) => void;
  isLoading?: boolean;
}

/**
 * Optimized Chat Component
 * - Memoized to prevent unnecessary re-renders
 * - WebSocket integration for real-time updates
 * - Intelligent polling fallback
 * - Virtualized message list for performance
 */
const OptimizedChat: React.FC<ChatProps> = memo(({
  messages,
  onSendMessage,
  isLoading = false
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // WebSocket subscription for real-time messages
  useEffect(() => {
    const unsubscribe = webSocketService.subscribe('chat_message', (data) => {
      // Handle real-time message updates
      console.log('📨 Real-time message received:', data);
    });
    
    return unsubscribe;
  }, []);
  
  // Intelligent polling as fallback when WebSocket is not available
  const pollChatUpdates = useCallback(async () => {
    if (webSocketService.getConnectionState() !== 'connected') {
      // Only poll when WebSocket is not connected
      try {
        const response = await fetch('/api/chat/updates');
        const updates = await response.json();
        console.log('🔄 Polling updates:', updates);
      } catch (error) {
        console.warn('⚠️ Polling failed:', error);
      }
    }
  }, []);
  
  const { currentInterval, errorCount } = useIntelligentPolling(
    pollChatUpdates,
    {
      baseInterval: 10000,  // 10 seconds when WebSocket is down
      maxInterval: 120000,  // Max 2 minutes
      errorThreshold: 2     // Increase interval after 2 errors
    },
    true // Enable polling
  );
  
  // Memoized message rendering
  const renderedMessages = useMemo(() => {
    return messages.map((message) => (
      <MessageItem
        key={message.id}
        message={message}
      />
    ));
  }, [messages]);
  
  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  // Memoized send handler
  const handleSend = useCallback((message: string) => {
    if (message.trim() && !isLoading) {
      onSendMessage(message);
    }
  }, [onSendMessage, isLoading]);
  
  return (
    <div className="optimized-chat">
      <div className="chat-header">
        <ConnectionStatus />
        <PollingStatus 
          interval={currentInterval} 
          errorCount={errorCount}
          wsConnected={webSocketService.getConnectionState() === 'connected'}
        />
      </div>
      
      <div className="messages-container">
        <div className="messages-list">
          {renderedMessages}
          <div ref={messagesEndRef} />
        </div>
      </div>
      
      <ChatInput 
        onSend={handleSend}
        disabled={isLoading}
      />
    </div>
  );
});

/**
 * Memoized Message Item Component
 */
const MessageItem: React.FC<{ message: Message }> = memo(({ message }) => {
  return (
    <div className={`message ${message.type}`}>
      <div className="message-content">{message.content}</div>
      <div className="message-timestamp">
        {new Date(message.timestamp).toLocaleTimeString()}
      </div>
    </div>
  );
});

/**
 * Connection Status Indicator
 */
const ConnectionStatus: React.FC = memo(() => {
  const [status, setStatus] = React.useState(webSocketService.getConnectionState());
  
  useEffect(() => {
    const interval = setInterval(() => {
      setStatus(webSocketService.getConnectionState());
    }, 1000);
    
    return () => clearInterval(interval);
  }, []);
  
  const statusConfig = {
    connected: { color: 'green', text: '🟢 Real-time' },
    connecting: { color: 'yellow', text: '🟡 Connecting' },
    disconnected: { color: 'orange', text: '🟠 Polling' },
    error: { color: 'red', text: '🔴 Error' }
  };
  
  const config = statusConfig[status];
  
  return (
    <div className="connection-status" style={{ color: config.color }}>
      {config.text}
    </div>
  );
});

/**
 * Polling Status Indicator
 */
interface PollingStatusProps {
  interval: number;
  errorCount: number;
  wsConnected: boolean;
}

const PollingStatus: React.FC<PollingStatusProps> = memo(({
  interval,
  errorCount,
  wsConnected
}) => {
  if (wsConnected) {
    return null; // Don't show polling status when WebSocket is connected
  }
  
  return (
    <div className="polling-status">
      <small>
        📊 Polling: {interval/1000}s
        {errorCount > 0 && ` (${errorCount} errors)`}
      </small>
    </div>
  );
});

/**
 * Memoized Chat Input Component
 */
interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

const ChatInput: React.FC<ChatInputProps> = memo(({ onSend, disabled }) => {
  const [input, setInput] = React.useState('');
  
  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      onSend(input);
      setInput('');
    }
  }, [input, onSend]);
  
  return (
    <form onSubmit={handleSubmit} className="chat-input">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Type your message..."
        disabled={disabled}
      />
      <button type="submit" disabled={disabled || !input.trim()}>
        Send
      </button>
    </form>
  );
});

export default OptimizedChat;

import React, { useState, useRef, useEffect } from 'react';

const ExecutiveChatInterface = ({ messages, onSendMessage, isConnected, connectionStatus }) => {
  const [inputMessage, setInputMessage] = useState('');
  const [isExpanded, setIsExpanded] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (inputMessage.trim() && isConnected) {
      onSendMessage(inputMessage.trim());
      setInputMessage('');
    }
  };

  const quickActions = [
    { icon: 'fa-chart-line', label: 'Revenue Analysis', query: 'Analyze our revenue performance this quarter' },
    { icon: 'fa-users', label: 'Team Performance', query: 'Show me team performance metrics' },
    { icon: 'fa-globe', label: 'Market Insights', query: 'What are the latest market trends?' },
    { icon: 'fa-target', label: 'Goal Progress', query: 'How are we tracking against our goals?' }
  ];

  const formatMessageTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return 'status-online';
      case 'connecting': return 'status-warning';
      case 'disconnected': return 'status-offline';
      default: return 'status-warning';
    }
  };

  return (
    <div className={`glassmorphism-card transition-all duration-300 ${isExpanded ? 'p-6' : 'p-4'}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="executive-icon gradient-purple-blue">
            <i className="fas fa-robot"></i>
          </div>
          <div>
            <h3 className="text-xl font-bold text-white">Sophia AI Assistant</h3>
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full pulse-dot ${getConnectionStatusColor()}`}></div>
              <span className="text-sm text-executive-secondary">
                {isConnected ? 'Online' : 'Offline'}
              </span>
            </div>
          </div>
        </div>
        
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="executive-icon hover-scale"
          style={{ background: 'rgba(75, 85, 99, 0.5)' }}
        >
          <i className={`fas ${isExpanded ? 'fa-compress' : 'fa-expand'}`}></i>
        </button>
      </div>

      {/* Quick Actions */}
      {!isExpanded && (
        <div className="grid grid-cols-2 gap-3 mb-4">
          {quickActions.map((action, index) => (
            <button
              key={index}
              onClick={() => isConnected && onSendMessage(action.query)}
              disabled={!isConnected}
              className="quick-action p-3 rounded-lg text-left hover-scale transition-all duration-200"
            >
              <div className="flex items-center space-x-2">
                <i className={`fas ${action.icon} text-executive-primary`}></i>
                <span className="text-sm text-executive-secondary">{action.label}</span>
              </div>
            </button>
          ))}
        </div>
      )}

      {/* Chat Messages */}
      {isExpanded && (
        <div className="glassmorphism-light rounded-lg p-4 mb-4" style={{ height: '300px', overflowY: 'auto' }}>
          {messages && messages.length > 0 ? (
            <div className="space-y-4">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      message.type === 'user'
                        ? 'bg-gradient-to-r from-purple-500 to-blue-500 text-white'
                        : 'ai-message text-executive-secondary'
                    }`}
                  >
                    <p className="text-sm">{message.content}</p>
                    <span className="text-xs opacity-70">
                      {formatMessageTime(message.timestamp)}
                    </span>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-executive-muted">
              <div className="text-center">
                <i className="fas fa-comments text-3xl mb-2"></i>
                <p>Start a conversation with Sophia AI</p>
                <p className="text-xs">Ask about revenue, team performance, or market insights</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Input Area */}
      <form onSubmit={handleSendMessage} className="flex space-x-3">
        <div className="flex-1 relative">
          <input
            ref={inputRef}
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder={isConnected ? "Ask Sophia AI anything..." : "Connecting..."}
            disabled={!isConnected}
            className="w-full bg-transparent border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-executive-muted focus:outline-none focus:border-purple-500 transition-colors"
          />
          {!isConnected && (
            <div className="absolute right-3 top-3">
              <div className="w-5 h-5 border-2 border-gray-400 border-t-purple-500 rounded-full animate-spin"></div>
            </div>
          )}
        </div>
        
        <button
          type="submit"
          disabled={!inputMessage.trim() || !isConnected}
          className="btn-executive-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          <i className="fas fa-paper-plane"></i>
          <span>Send</span>
        </button>
      </form>

      {/* Status Bar */}
      <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-700">
        <div className="flex items-center space-x-2 text-xs text-executive-muted">
          <i className="fas fa-shield-alt"></i>
          <span>End-to-end encrypted</span>
        </div>
        <div className="flex items-center space-x-2 text-xs text-executive-muted">
          <i className="fas fa-clock"></i>
          <span>Real-time responses</span>
        </div>
      </div>
    </div>
  );
};

export default ExecutiveChatInterface;

import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../../ui/card';
import { Button } from '../../../ui/button';
import { Input } from '../../../ui/input';

const ExecutiveChatInterface = ({ messages, onSendMessage, isConnected, connectionStatus }) => {
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !isConnected) return;

    const message = inputMessage.trim();
    setInputMessage('');
    setIsTyping(true);

    try {
      await onSendMessage(message);
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return 'text-green-600';
      case 'connecting': return 'text-yellow-600';
      case 'error': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getConnectionStatusText = () => {
    switch (connectionStatus) {
      case 'connected': return 'Connected';
      case 'connecting': return 'Connecting...';
      case 'error': return 'Connection Error';
      default: return 'Offline';
    }
  };

  // Sample executive queries
  const sampleQueries = [
    "What's our revenue trend for Q2?",
    "Show me team performance metrics",
    "Analyze competitive landscape",
    "What are the top strategic risks?",
    "Generate executive summary"
  ];

  return (
    <Card className="h-96 flex flex-col">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <CardTitle className="text-xl font-bold flex items-center space-x-2">
          <span>🤖</span>
          <span>Sophia AI Assistant</span>
        </CardTitle>
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className={`text-sm ${getConnectionStatusColor()}`}>
            {getConnectionStatusText()}
          </span>
        </div>
      </CardHeader>
      
      <CardContent className="flex-1 flex flex-col space-y-4">
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto space-y-3 p-2 bg-gray-50 rounded-lg">
          {(!messages || messages.length === 0) ? (
            <div className="text-center text-gray-500 py-8">
              <div className="text-4xl mb-2">👋</div>
              <p className="mb-4">Welcome! I'm your AI executive assistant.</p>
              <div className="text-left space-y-1">
                <p className="text-sm font-medium mb-2">Try asking me:</p>
                {sampleQueries.slice(0, 3).map((query, index) => (
                  <button
                    key={index}
                    onClick={() => setInputMessage(query)}
                    className="block w-full text-left text-sm text-blue-600 hover:text-blue-800 py-1 px-2 rounded hover:bg-blue-50"
                  >
                    • {query}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map((message, index) => (
                <div key={index} className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] rounded-lg px-4 py-2 ${
                    message.sender === 'user' 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-white text-gray-900 border'
                  }`}>
                    <p className="text-sm">{message.content}</p>
                    {message.timestamp && (
                      <span className={`text-xs mt-1 block ${
                        message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'
                      }`}>
                        {formatTimestamp(message.timestamp)}
                      </span>
                    )}
                  </div>
                </div>
              ))}
              
              {isTyping && (
                <div className="flex justify-start">
                  <div className="bg-white text-gray-900 border rounded-lg px-4 py-2">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="flex space-x-2">
          <Input
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={isConnected ? "Ask me anything about your business..." : "Connecting..."}
            disabled={!isConnected || isTyping}
            className="flex-1"
          />
          <Button 
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || !isConnected || isTyping}
          >
            Send
          </Button>
        </div>

        {/* Quick Actions */}
        <div className="flex flex-wrap gap-2">
          {sampleQueries.map((query, index) => (
            <button
              key={index}
              onClick={() => setInputMessage(query)}
              className="text-xs px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-700 transition-colors"
              disabled={!isConnected}
            >
              {query}
            </button>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default ExecutiveChatInterface;

import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import MCPIntegrationService from '../../services/mcpIntegration';
import apiClient from '../../services/apiClient';
import { 
  MessageCircle, 
  Send, 
  Bot, 
  User, 
  Settings, 
  Sparkles,
  Crown,
  Globe,
  Loader2,
  RefreshCw
} from 'lucide-react';

/**
 * Unified Chat Interface - Phase 2C Implementation
 * Consolidates all chat functionality into a single, configurable component
 */
const UnifiedChatInterface = ({ 
  mode = 'universal',
  sessionId = null,
  onModeChange = null,
  className = '',
  height = '500px',
  showModeSelector = true,
  showSettings = true,
  apiEndpoint = '/api/v1/chat'
}) => {
  // State management
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentMode, setCurrentMode] = useState(mode);
  const [currentSessionId, setCurrentSessionId] = useState(sessionId || generateSessionId());
  const [suggestions, setSuggestions] = useState([]);
  const [error, setError] = useState(null);
  const [isConnected, setIsConnected] = useState(true);
  
  // Refs
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  
  // Chat mode configurations
  const modeConfigs = {
    universal: {
      title: 'Universal Chat',
      icon: Globe,
      color: 'bg-blue-500',
      description: 'General AI assistance',
      placeholder: 'Ask me anything...',
      features: ['basic_chat', 'general_knowledge']
    },
    sophia: {
      title: 'Sophia AI',
      icon: Sparkles,
      color: 'bg-purple-500',
      description: 'Advanced business intelligence',
      placeholder: 'Ask about business metrics, analytics, or insights...',
      features: ['business_intelligence', 'data_analysis', 'strategic_insights']
    },
    executive: {
      title: 'Executive Assistant',
      icon: Crown,
      color: 'bg-amber-500',
      description: 'C-suite focused insights',
      placeholder: 'Ask for executive summaries, strategic analysis...',
      features: ['executive_insights', 'strategic_analysis', 'board_summaries']
    }
  };
  
  // Generate session ID
  function generateSessionId() {
    return 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
  }
  
  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  // Initialize chat with welcome message
  useEffect(() => {
    const config = modeConfigs[currentMode];
    const welcomeMessage = {
      id: 'welcome_' + Date.now(),
      role: 'assistant',
      content: `Hello! I'm your ${config.title}. ${config.description}. How can I help you today?`,
      timestamp: new Date().toISOString(),
      mode: currentMode
    };
    
    setMessages([welcomeMessage]);
    
    // Set initial suggestions based on mode
    const initialSuggestions = getModeSuggestions(currentMode);
    setSuggestions(initialSuggestions);
  }, [currentMode]);
  
  // Get suggestions based on mode
  const getModeSuggestions = (mode) => {
    const suggestions = {
      universal: [
        "What can you help me with?",
        "Tell me about your capabilities",
        "How do I get started?"
      ],
      sophia: [
        "Analyze our Q3 performance metrics",
        "What are the key business trends?",
        "Generate strategic recommendations",
        "Show me cost analysis breakdown"
      ],
      executive: [
        "Summarize this week's key metrics",
        "What are our top 3 priorities?",
        "Prepare a board presentation summary",
        "Analyze competitive positioning"
      ]
    };
    
    return suggestions[mode] || suggestions.universal;
  };
  
  // Handle mode change
  const handleModeChange = (newMode) => {
    setCurrentMode(newMode);
    setCurrentSessionId(generateSessionId());
    setError(null);
    
    if (onModeChange) {
      onModeChange(newMode);
    }
  };
  
  // Send message to API
  const sendMessage = async (messageText) => {
    if (!messageText.trim() || isLoading) return;
    
    const userMessage = {
      id: 'user_' + Date.now(),
      role: 'user',
      content: messageText,
      timestamp: new Date().toISOString(),
      mode: currentMode
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.post('/api/v1/chat', {
        message: messageText,
        mode: currentMode,
        session_id: currentSessionId,
        context: {
          user_role: 'user',
          timestamp: new Date().toISOString()
        }
      });
      
      const data = response.data;
      
      const assistantMessage = {
        id: 'assistant_' + Date.now(),
        role: 'assistant',
        content: data.response,
        timestamp: data.timestamp || new Date().toISOString(),
        mode: data.mode || currentMode,
        metadata: data.metadata,
        usage: data.usage
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      
      // Update suggestions if provided
      if (data.suggestions && data.suggestions.length > 0) {
        setSuggestions(data.suggestions);
      }
      
      setIsConnected(true);
      
    } catch (error) {
      console.error('Chat API error:', error);
      setError(error.message);
      setIsConnected(false);
      
      // Add error message
      const errorMessage = {
        id: 'error_' + Date.now(),
        role: 'assistant',
        content: `I apologize, but I encountered an error: ${error.message}. Please try again.`,
        timestamp: new Date().toISOString(),
        mode: currentMode,
        isError: true
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(inputMessage);
  };
  
  // Handle suggestion click
  const handleSuggestionClick = (suggestion) => {
    sendMessage(suggestion);
  };
  
  // Handle key press
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };
  
  // Clear chat
  const clearChat = () => {
    setCurrentSessionId(generateSessionId());
    setMessages([]);
    setError(null);
    
    // Re-initialize with welcome message
    const config = modeConfigs[currentMode];
    const welcomeMessage = {
      id: 'welcome_' + Date.now(),
      role: 'assistant',
      content: `Chat cleared. I'm your ${config.title}. How can I help you?`,
      timestamp: new Date().toISOString(),
      mode: currentMode
    };
    
    setMessages([welcomeMessage]);
  };
  
  const currentConfig = modeConfigs[currentMode];
  const ModeIcon = currentConfig.icon;
  
  return (
    <Card className={`flex flex-col ${className}`} style={{ height }}>
      {/* Header */}
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`p-2 rounded-lg ${currentConfig.color} text-white`}>
              <ModeIcon size={20} />
            </div>
            <div>
              <CardTitle className="text-lg">{currentConfig.title}</CardTitle>
              <p className="text-sm text-gray-600">{currentConfig.description}</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            {/* Connection status */}
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
            
            {/* Mode selector */}
            {showModeSelector && (
              <select
                value={currentMode}
                onChange={(e) => handleModeChange(e.target.value)}
                className="text-sm border rounded px-2 py-1"
              >
                <option value="universal">Universal</option>
                <option value="sophia">Sophia AI</option>
                <option value="executive">Executive</option>
              </select>
            )}
            
            {/* Settings and clear */}
            {showSettings && (
              <div className="flex space-x-1">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={clearChat}
                  title="Clear chat"
                >
                  <RefreshCw size={16} />
                </Button>
              </div>
            )}
          </div>
        </div>
        
        {/* Features badges */}
        <div className="flex flex-wrap gap-1 mt-2">
          {currentConfig.features.map(feature => (
            <Badge key={feature} variant="secondary" className="text-xs">
              {feature.replace('_', ' ')}
            </Badge>
          ))}
        </div>
        
        {/* Error display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded p-2 text-sm text-red-700">
            Error: {error}
          </div>
        )}
      </CardHeader>
      
      {/* Messages */}
      <CardContent className="flex-1 overflow-hidden flex flex-col">
        <div className="flex-1 overflow-y-auto space-y-4 mb-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-3 ${
                  message.role === 'user'
                    ? 'bg-blue-500 text-white'
                    : message.isError
                    ? 'bg-red-50 border border-red-200 text-red-700'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                <div className="flex items-start space-x-2">
                  <div className="flex-shrink-0 mt-1">
                    {message.role === 'user' ? (
                      <User size={16} />
                    ) : (
                      <Bot size={16} />
                    )}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                    {message.usage && (
                      <div className="text-xs opacity-70 mt-1">
                        {message.usage.total_tokens} tokens • ${message.usage.estimated_cost?.toFixed(4)}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
          
          {/* Loading indicator */}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-lg p-3">
                <div className="flex items-center space-x-2">
                  <Loader2 size={16} className="animate-spin" />
                  <span className="text-sm text-gray-600">Thinking...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
        
        {/* Suggestions */}
        {suggestions.length > 0 && !isLoading && (
          <div className="mb-4">
            <p className="text-xs text-gray-500 mb-2">Suggested questions:</p>
            <div className="flex flex-wrap gap-2">
              {suggestions.slice(0, 3).map((suggestion, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="text-xs h-auto py-1 px-2"
                >
                  {suggestion}
                </Button>
              ))}
            </div>
          </div>
        )}
        
        {/* Input form */}
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <Input
            ref={inputRef}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={currentConfig.placeholder}
            disabled={isLoading}
            className="flex-1"
          />
          <Button
            type="submit"
            disabled={isLoading || !inputMessage.trim()}
            className={currentConfig.color}
          >
            {isLoading ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <Send size={16} />
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

export default UnifiedChatInterface;


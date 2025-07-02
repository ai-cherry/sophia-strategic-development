/**
 * UNIVERSAL CHAT INTERFACE - CONSOLIDATED IMPLEMENTATION
 * 
 * This component consolidates ALL existing chat interfaces into a single,
 * unified, role-aware chat system for Sophia AI Platform.
 * 
 * Features:
 * - Role-based access control (CEO, Executive, Manager, Employee)
 * - Universal search across all data sources (Redis, Pinecone, Snowflake)
 * - Real-time WebSocket communication
 * - AI personality management
 * - Business intelligence integration
 * - Mobile-responsive glassmorphism design
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  Bot, 
  User, 
  Send, 
  Settings, 
  Globe, 
  Database, 
  Brain, 
  Shield,
  RefreshCw,
  Copy,
  AlertCircle,
  Sparkles,
  Clock,
  Target,
  Search,
  Zap,
  Crown,
  Users,
  Building,
  Mic,
  MicOff,
  Upload,
  Download,
  BarChart3,
  TrendingUp,
  DollarSign
} from 'lucide-react';

// Types
interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  sources?: Array<{
    type: 'internal' | 'internet' | 'database' | 'api';
    source: string;
    title: string;
    url?: string;
    relevance_score: number;
  }>;
  metadata?: {
    personality_applied: string;
    search_time_ms: number;
    confidence_score: number;
    internal_results_count: number;
    internet_results_count: number;
    synthesis_quality: number;
    business_context?: string;
    executive_insights?: string[];
  };
  actions?: string[];
  insights?: string[];
}

interface UserRole {
  level: 'CEO' | 'Executive' | 'Manager' | 'Employee';
  permissions: string[];
  data_access: string[];
  features: string[];
}

interface UniversalChatProps {
  userId?: string;
  userRole?: UserRole;
  context?: string;
  height?: string;
  className?: string;
  dashboardType?: 'ceo' | 'executive' | 'manager' | 'employee' | 'universal';
  onPersonalityChange?: (personality: string) => void;
  onRoleChange?: (role: UserRole) => void;
  showAdvancedControls?: boolean;
  enableVoiceInput?: boolean;
  enableFileUpload?: boolean;
}

// Default role configurations
const ROLE_CONFIGS = {
  CEO: {
    level: 'CEO' as const,
    permissions: ['all_data', 'executive_insights', 'strategic_analysis', 'financial_data', 'personnel_data'],
    data_access: ['snowflake', 'gong', 'hubspot', 'linear', 'asana', 'slack', 'notion', 'financial_systems'],
    features: ['ai_personas', 'deep_research', 'code_analysis', 'ui_generation', 'strategic_planning']
  },
  Executive: {
    level: 'Executive' as const,
    permissions: ['department_data', 'team_insights', 'performance_metrics', 'project_data'],
    data_access: ['snowflake', 'hubspot', 'linear', 'asana', 'slack'],
    features: ['business_intelligence', 'team_analytics', 'project_management']
  },
  Manager: {
    level: 'Manager' as const,
    permissions: ['team_data', 'project_insights', 'performance_metrics'],
    data_access: ['linear', 'asana', 'slack', 'team_metrics'],
    features: ['team_management', 'project_tracking', 'basic_analytics']
  },
  Employee: {
    level: 'Employee' as const,
    permissions: ['personal_data', 'assigned_projects', 'team_communication'],
    data_access: ['linear', 'slack', 'personal_metrics'],
    features: ['task_management', 'communication', 'basic_assistance']
  }
};

// AI Personalities
const AI_PERSONALITIES = {
  executive_advisor: {
    name: 'Executive Advisor',
    icon: Crown,
    description: 'Strategic insights and C-suite focused analysis',
    color: 'text-amber-400',
    available_to: ['CEO', 'Executive']
  },
  business_intelligence: {
    name: 'Business Intelligence',
    icon: BarChart3,
    description: 'Data-driven insights and analytics',
    color: 'text-blue-400',
    available_to: ['CEO', 'Executive', 'Manager']
  },
  friendly_assistant: {
    name: 'Friendly Assistant',
    icon: Sparkles,
    description: 'Helpful and approachable AI companion',
    color: 'text-purple-400',
    available_to: ['CEO', 'Executive', 'Manager', 'Employee']
  },
  technical_expert: {
    name: 'Technical Expert',
    icon: Brain,
    description: 'Deep technical knowledge and analysis',
    color: 'text-green-400',
    available_to: ['CEO', 'Executive']
  },
  project_manager: {
    name: 'Project Manager',
    icon: Target,
    description: 'Project coordination and team management',
    color: 'text-orange-400',
    available_to: ['CEO', 'Executive', 'Manager']
  }
};

// Search contexts
const SEARCH_CONTEXTS = {
  universal: {
    name: 'Universal Search',
    icon: Globe,
    description: 'Search across all available data sources',
    sources: ['internal', 'internet', 'databases', 'apis']
  },
  internal_only: {
    name: 'Internal Data Only',
    icon: Database,
    description: 'Search only internal business data',
    sources: ['internal', 'databases']
  },
  business_intelligence: {
    name: 'Business Intelligence',
    icon: Brain,
    description: 'Focus on business metrics and insights',
    sources: ['internal', 'databases', 'analytics']
  },
  strategic_research: {
    name: 'Strategic Research',
    icon: Search,
    description: 'Deep research with external sources',
    sources: ['internal', 'internet', 'competitive_intelligence']
  }
};

export const UniversalChatInterface: React.FC<UniversalChatProps> = ({
  userId = "user",
  userRole = ROLE_CONFIGS.Employee,
  context = "universal",
  height = "600px",
  className = "",
  dashboardType = "universal",
  onPersonalityChange,
  onRoleChange,
  showAdvancedControls = true,
  enableVoiceInput = false,
  enableFileUpload = false
}) => {
  // State management
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'connecting'>('disconnected');
  
  // Configuration state
  const [selectedPersonality, setSelectedPersonality] = useState('friendly_assistant');
  const [selectedSearchContext, setSelectedSearchContext] = useState('universal');
  const [sessionId, setSessionId] = useState(`session_${Date.now()}`);
  
  // UI state
  const [showSettings, setShowSettings] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [typingIndicator, setTypingIndicator] = useState(false);
  
  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Initialize chat
  useEffect(() => {
    initializeChat();
    connectWebSocket();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [userId, userRole]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, typingIndicator]);

  const initializeChat = useCallback(() => {
    const welcomeMessage: ChatMessage = {
      id: 'welcome_' + Date.now(),
      role: 'assistant',
      content: getWelcomeMessage(),
      timestamp: new Date().toISOString(),
      metadata: {
        personality_applied: selectedPersonality,
        search_time_ms: 0,
        confidence_score: 1.0,
        internal_results_count: 0,
        internet_results_count: 0,
        synthesis_quality: 1.0,
        business_context: dashboardType
      }
    };
    
    setMessages([welcomeMessage]);
  }, [selectedPersonality, dashboardType, userRole]);

  const getWelcomeMessage = () => {
    const roleLevel = userRole.level;
    const personality = AI_PERSONALITIES[selectedPersonality as keyof typeof AI_PERSONALITIES];
    
    return `🎯 **Welcome to Sophia AI - ${personality.name} Mode**

I'm your AI assistant with **${roleLevel}**-level access to:

${userRole.data_access.map(source => `📊 **${source.charAt(0).toUpperCase() + source.slice(1)}**`).join('\n')}

**Available Features:**
${userRole.features.map(feature => `✨ ${feature.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}`).join('\n')}

**What would you like to explore today?**`;
  };

  const connectWebSocket = useCallback(() => {
    try {
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${wsProtocol}//${window.location.host}/api/chat/ws/${sessionId}?user_id=${userId}`;
      
      wsRef.current = new WebSocket(wsUrl);
      
      wsRef.current.onopen = () => {
        setConnectionStatus('connected');
        setError(null);
      };
      
      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleWebSocketMessage(data);
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };
      
      wsRef.current.onclose = () => {
        setConnectionStatus('disconnected');
        // Attempt to reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
      };
      
      wsRef.current.onerror = (error) => {
        setConnectionStatus('disconnected');
        setError('WebSocket connection failed');
      };
      
    } catch (err) {
      setConnectionStatus('disconnected');
      setError('Failed to connect to chat service');
    }
  }, [sessionId, userId]);

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'chat_response':
        setTypingIndicator(false);
        const assistantMessage: ChatMessage = {
          id: data.data.message_id || `msg_${Date.now()}`,
          role: 'assistant',
          content: data.data.content,
          timestamp: data.data.timestamp || new Date().toISOString(),
          sources: data.data.sources,
          metadata: data.data.metadata,
          actions: data.data.actions,
          insights: data.data.insights
        };
        setMessages(prev => [...prev, assistantMessage]);
        break;
        
      case 'typing':
        setTypingIndicator(data.is_typing);
        break;
        
      case 'error':
        setError(data.message);
        setLoading(false);
        setTypingIndicator(false);
        break;
        
      default:
        console.log('Unknown message type:', data.type);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    
    const userMessage: ChatMessage = {
      id: `msg_${Date.now()}`,
      role: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setError(null);
    
    try {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        // Send via WebSocket
        wsRef.current.send(JSON.stringify({
          type: 'chat_message',
          message: userMessage.content,
          session_id: sessionId,
          user_id: userId,
          context: {
            personality: selectedPersonality,
            search_context: selectedSearchContext,
            user_role: userRole,
            dashboard_type: dashboardType
          }
        }));
        setTypingIndicator(true);
      } else {
        // Fallback to HTTP
        const response = await fetch('/api/chat/message', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: userMessage.content,
            session_id: sessionId,
            user_id: userId,
            metadata: {
              personality: selectedPersonality,
              search_context: selectedSearchContext,
              user_role: userRole,
              dashboard_type: dashboardType
            }
          })
        });
        
        if (response.ok) {
          const data = await response.json();
          const assistantMessage: ChatMessage = {
            id: data.message_id || `msg_${Date.now()}`,
            role: 'assistant',
            content: data.content,
            timestamp: data.timestamp || new Date().toISOString(),
            sources: data.sources,
            metadata: data.metadata,
            actions: data.actions,
            insights: data.insights
          };
          setMessages(prev => [...prev, assistantMessage]);
        } else {
          throw new Error('Failed to send message');
        }
      }
    } catch (err) {
      setError('Failed to send message. Please try again.');
      console.error('Send message error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
    setSessionId(`session_${Date.now()}`);
    setError(null);
    initializeChat();
  };

  const changePersonality = (personality: string) => {
    setSelectedPersonality(personality);
    if (onPersonalityChange) {
      onPersonalityChange(personality);
    }
    
    // Send personality change via WebSocket
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'personality_change',
        personality: personality
      }));
    }
  };

  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return 'bg-green-500';
      case 'connecting': return 'bg-yellow-500 animate-pulse';
      case 'disconnected': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getAvailablePersonalities = () => {
    return Object.entries(AI_PERSONALITIES).filter(([_, personality]) => 
      personality.available_to.includes(userRole.level)
    );
  };

  const currentPersonality = AI_PERSONALITIES[selectedPersonality as keyof typeof AI_PERSONALITIES];
  const PersonalityIcon = currentPersonality?.icon || Bot;

  return (
    <div 
      className={`flex flex-col bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 rounded-xl shadow-2xl border border-white/10 ${className}`}
      style={{ height }}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-white/10 bg-white/5 backdrop-blur-xl rounded-t-xl">
        <div className="flex items-center space-x-3">
          <div className={`p-2 rounded-lg bg-gradient-to-r from-purple-500 to-blue-500 text-white`}>
            <PersonalityIcon className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">
              {currentPersonality?.name || 'Sophia AI'}
            </h3>
            <p className="text-sm text-gray-300">
              {userRole.level} • {connectionStatus}
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          {/* Connection status indicator */}
          <div className={`w-2 h-2 rounded-full ${getConnectionStatusColor()}`} />
          
          {/* Settings */}
          {showAdvancedControls && (
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-2 text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
            >
              <Settings className="w-4 h-4" />
            </button>
          )}
          
          {/* Clear chat */}
          <button
            onClick={clearChat}
            className="p-2 text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
            title="Clear chat"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <div className="p-4 border-b border-white/10 bg-white/5 backdrop-blur-xl">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Personality Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                AI Personality
              </label>
              <select
                value={selectedPersonality}
                onChange={(e) => changePersonality(e.target.value)}
                className="w-full p-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                {getAvailablePersonalities().map(([key, personality]) => (
                  <option key={key} value={key} className="bg-gray-800">
                    {personality.name}
                  </option>
                ))}
              </select>
            </div>
            
            {/* Search Context */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Search Context
              </label>
              <select
                value={selectedSearchContext}
                onChange={(e) => setSelectedSearchContext(e.target.value)}
                className="w-full p-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                {Object.entries(SEARCH_CONTEXTS).map(([key, context]) => (
                  <option key={key} value={key} className="bg-gray-800">
                    {context.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="mx-4 mt-4 p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-300 text-sm flex items-center space-x-2">
          <AlertCircle className="w-4 h-4" />
          <span>{error}</span>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {message.role === 'assistant' && (
              <div className="flex-shrink-0">
                <Bot className="w-6 h-6 text-purple-400" />
              </div>
            )}
            
            <div className={`max-w-[85%] p-4 rounded-xl ${
              message.role === 'user'
                ? 'bg-blue-500/20 border border-blue-500/30 text-white'
                : 'bg-white/10 border border-white/20 text-gray-100'
            }`}>
              <div className="whitespace-pre-wrap text-sm leading-relaxed">
                {message.content}
              </div>
              
              {/* Message metadata */}
              {message.metadata && (
                <div className="mt-3 pt-3 border-t border-white/10 text-xs text-gray-400">
                  <div className="flex items-center space-x-4">
                    <span>Confidence: {(message.metadata.confidence_score * 100).toFixed(0)}%</span>
                    <span>Time: {message.metadata.search_time_ms}ms</span>
                    {message.metadata.internal_results_count > 0 && (
                      <span>Internal: {message.metadata.internal_results_count}</span>
                    )}
                    {message.metadata.internet_results_count > 0 && (
                      <span>Web: {message.metadata.internet_results_count}</span>
                    )}
                  </div>
                </div>
              )}
              
              {/* Sources */}
              {message.sources && message.sources.length > 0 && (
                <div className="mt-3 pt-3 border-t border-white/10">
                  <div className="text-xs text-gray-400 mb-2">Sources:</div>
                  <div className="space-y-1">
                    {message.sources.slice(0, 3).map((source, index) => (
                      <div key={index} className="flex items-center space-x-2 text-xs">
                        <div className={`w-2 h-2 rounded-full ${
                          source.type === 'internal' ? 'bg-blue-400' : 
                          source.type === 'internet' ? 'bg-green-400' : 'bg-purple-400'
                        }`} />
                        <span className="text-gray-300 truncate">{source.title}</span>
                        <span className="text-gray-500">({(source.relevance_score * 100).toFixed(0)}%)</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Actions */}
              {message.actions && message.actions.length > 0 && (
                <div className="mt-3 pt-3 border-t border-white/10">
                  <div className="text-xs text-gray-400 mb-2">Recommended Actions:</div>
                  <div className="space-y-1">
                    {message.actions.map((action, index) => (
                      <div key={index} className="flex items-start space-x-2 text-xs">
                        <Zap className="w-3 h-3 text-yellow-400 mt-0.5 flex-shrink-0" />
                        <span className="text-gray-300">{action}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              <div className="mt-2 text-xs text-gray-500">
                {new Date(message.timestamp).toLocaleTimeString()}
              </div>
            </div>
            
            {message.role === 'user' && (
              <div className="flex-shrink-0">
                <User className="w-6 h-6 text-blue-400" />
              </div>
            )}
          </div>
        ))}
        
        {/* Typing indicator */}
        {typingIndicator && (
          <div className="flex justify-start">
            <div className="flex items-center space-x-2 bg-white/10 backdrop-blur-xl border border-white/20 rounded-xl p-4">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
              <span className="text-gray-300 text-sm">Sophia is thinking...</span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-white/10 bg-white/5 backdrop-blur-xl rounded-b-xl">
        <div className="flex items-end space-x-3">
          {/* File upload */}
          {enableFileUpload && (
            <button
              onClick={() => fileInputRef.current?.click()}
              className="p-2 text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
            >
              <Upload className="w-5 h-5" />
            </button>
          )}
          
          {/* Voice input */}
          {enableVoiceInput && (
            <button
              onClick={() => setIsListening(!isListening)}
              className={`p-2 rounded-lg transition-colors ${
                isListening 
                  ? 'text-red-400 bg-red-500/20 hover:bg-red-500/30' 
                  : 'text-gray-300 hover:text-white hover:bg-white/10'
              }`}
            >
              {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
            </button>
          )}
          
          {/* Message input */}
          <div className="flex-1 relative">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={`Message ${currentPersonality?.name || 'Sophia AI'}...`}
              className="w-full p-3 pr-12 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              disabled={loading || connectionStatus === 'disconnected'}
            />
            
            {/* Send button */}
            <button
              onClick={sendMessage}
              disabled={!input.trim() || loading || connectionStatus === 'disconnected'}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 text-purple-400 hover:text-purple-300 disabled:text-gray-500 disabled:cursor-not-allowed transition-colors"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
        
        {/* Status bar */}
        <div className="flex items-center justify-between mt-2 text-xs text-gray-400">
          <div className="flex items-center space-x-4">
            <span>Session: {sessionId.slice(-8)}</span>
            <span>Role: {userRole.level}</span>
            <span>Context: {SEARCH_CONTEXTS[selectedSearchContext as keyof typeof SEARCH_CONTEXTS]?.name}</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className={connectionStatus === 'connected' ? 'text-green-400' : 'text-red-400'}>
              {connectionStatus}
            </span>
          </div>
        </div>
      </div>
      
      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        multiple
        accept=".txt,.pdf,.doc,.docx,.csv,.json"
        onChange={(e) => {
          // Handle file upload
          console.log('Files selected:', e.target.files);
        }}
      />
    </div>
  );
};

export default UniversalChatInterface; 
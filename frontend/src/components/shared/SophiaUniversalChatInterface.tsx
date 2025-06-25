import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
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
  Zap
} from 'lucide-react';
import { Alert, AlertDescription } from '../ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '../ui/tooltip';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  sources?: Array<{
    type: 'internal' | 'internet';
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
  };
}

interface SophiaPersonality {
  value: string;
  name: string;
  tone: string;
  style: string;
  focus: string;
  greeting: string;
}

interface SearchContext {
  value: string;
  name: string;
  description: string;
  requires_permission: boolean;
}

interface UserProfile {
  user_id: string;
  name: string;
  access_level: string;
  search_permissions: string[];
  preferred_personality: string;
  api_usage_today: number;
  api_quota_daily: number;
}

interface SophiaUniversalChatInterfaceProps {
  userId?: string;
  height?: string;
  className?: string;
  onPersonalityChange?: (personality: string) => void;
  onSearchContextChange?: (context: string) => void;
  showAdvancedControls?: boolean;
}

export const SophiaUniversalChatInterface: React.FC<SophiaUniversalChatInterfaceProps> = ({
  userId = "ceo",
  height = "600px",
  className = "",
  onPersonalityChange,
  onSearchContextChange,
  showAdvancedControls = true
}) => {
  // State management
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'connecting'>('disconnected');
  
  // Sophia configuration
  const [personalities, setPersonalities] = useState<Record<string, SophiaPersonality>>({});
  const [searchContexts, setSearchContexts] = useState<Record<string, SearchContext>>({});
  const [selectedPersonality, setSelectedPersonality] = useState('executive_advisor');
  const [selectedSearchContext, setSelectedSearchContext] = useState('blended_intelligence');
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  
  // UI state
  const [showSettings, setShowSettings] = useState(false);
  const [typingIndicator, setTypingIndicator] = useState(false);
  
  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // Initialize chat interface
  useEffect(() => {
    initializeSophia();
    connectWebSocket();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [userId]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, typingIndicator]);

  const initializeSophia = async () => {
    try {
      // Load personalities
      const personalitiesResponse = await fetch('/api/v1/sophia/chat/personalities');
      if (personalitiesResponse.ok) {
        const personalitiesData = await personalitiesResponse.json();
        setPersonalities(personalitiesData.personalities);
      }

      // Load search contexts
      const contextsResponse = await fetch('/api/v1/sophia/search/contexts');
      if (contextsResponse.ok) {
        const contextsData = await contextsResponse.json();
        setSearchContexts(contextsData.search_contexts);
      }

      // Load user profile
      const userResponse = await fetch(`/api/v1/sophia/users/${userId}`);
      if (userResponse.ok) {
        const userData = await userResponse.json();
        setUserProfile(userData);
        setSelectedPersonality(userData.preferred_personality);
        
        // Set default search context based on permissions
        if (userData.search_permissions.includes('ceo_deep_research')) {
          setSelectedSearchContext('ceo_deep_research');
        } else if (userData.search_permissions.includes('blended_intelligence')) {
          setSelectedSearchContext('blended_intelligence');
        } else {
          setSelectedSearchContext('internal_only');
        }
      }

      // Add welcome message
      const welcomeMessage: ChatMessage = {
        id: '1',
        role: 'assistant',
        content: `Hello! I'm Sophia, your AI assistant with personality and internet intelligence. I'm currently in ${selectedPersonality.replace('_', ' ')} mode and ready to help with anything you need. I have access to both internal company data and real-time internet intelligence to provide you with comprehensive insights.`,
        timestamp: new Date().toISOString()
      };
      
      setMessages([welcomeMessage]);

    } catch (error) {
      console.error('Failed to initialize Sophia:', error);
      setError('Failed to initialize Sophia AI');
    }
  };

  const connectWebSocket = () => {
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/api/v1/sophia/chat/ws/${userId}_${Date.now()}?user_id=${userId}`;
      
      const ws = new WebSocket(wsUrl);
      
      ws.onopen = () => {
        setConnectionStatus('connected');
        setError(null);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleWebSocketMessage(data);
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      ws.onclose = () => {
        setConnectionStatus('disconnected');
        // Auto-reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('disconnected');
      };

      wsRef.current = ws;
    } catch (err) {
      console.error('Failed to create WebSocket:', err);
      setConnectionStatus('disconnected');
    }
  };

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'connected':
        console.log('Connected to Sophia AI');
        break;
        
      case 'chat_response':
        const assistantMessage: ChatMessage = {
          id: Date.now().toString(),
          role: 'assistant',
          content: data.content,
          timestamp: data.timestamp,
          sources: data.sources || [],
          metadata: {
            personality_applied: data.personality_applied,
            search_time_ms: data.search_time_ms,
            confidence_score: data.confidence_score,
            internal_results_count: data.internal_results_count,
            internet_results_count: data.internet_results_count,
            synthesis_quality: data.synthesis_quality
          }
        };
        
        setMessages(prev => [...prev, assistantMessage]);
        setLoading(false);
        setTypingIndicator(false);
        break;
        
      case 'typing':
        setTypingIndicator(data.is_typing);
        break;
        
      case 'error':
        setError(data.message);
        setLoading(false);
        setTypingIndicator(false);
        break;
        
      case 'personality_changed':
        setSelectedPersonality(data.personality);
        if (onPersonalityChange) {
          onPersonalityChange(data.personality);
        }
        break;
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
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
          message: input.trim(),
          context: {
            personality: selectedPersonality,
            search_context: selectedSearchContext
          }
        }));
      } else {
        // Fallback to HTTP
        const response = await fetch('/api/v1/sophia/chat/message', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: input.trim(),
            user_id: userId,
            personality_override: selectedPersonality,
            context: {
              search_context: selectedSearchContext
            }
          })
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        const assistantMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.content,
          timestamp: new Date().toISOString(),
          sources: data.sources || [],
          metadata: {
            personality_applied: data.personality_applied,
            search_time_ms: data.search_time_ms,
            confidence_score: data.confidence_score,
            internal_results_count: data.internal_results_count,
            internet_results_count: data.internet_results_count,
            synthesis_quality: data.synthesis_quality
          }
        };

        setMessages(prev => [...prev, assistantMessage]);
      }
    } catch (err) {
      console.error('Failed to send message:', err);
      setError('Failed to send message. Please try again.');
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

  const changePersonality = async (personality: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'personality_change',
        personality: personality
      }));
    }
    setSelectedPersonality(personality);
    if (onPersonalityChange) {
      onPersonalityChange(personality);
    }
  };

  const getPersonalityIcon = (personality: string) => {
    switch (personality) {
      case 'executive_advisor': return <Target className="h-4 w-4" />;
      case 'friendly_assistant': return <Sparkles className="h-4 w-4" />;
      case 'technical_expert': return <Brain className="h-4 w-4" />;
      case 'creative_collaborator': return <Zap className="h-4 w-4" />;
      case 'professional_consultant': return <Shield className="h-4 w-4" />;
      default: return <Bot className="h-4 w-4" />;
    }
  };

  const getSearchContextIcon = (context: string) => {
    switch (context) {
      case 'internal_only': return <Database className="h-4 w-4" />;
      case 'internet_only': return <Globe className="h-4 w-4" />;
      case 'blended_intelligence': return <Brain className="h-4 w-4" />;
      case 'ceo_deep_research': return <Search className="h-4 w-4" />;
      default: return <Database className="h-4 w-4" />;
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

  const copyMessage = async (content: string) => {
    try {
      await navigator.clipboard.writeText(content);
    } catch (err) {
      console.error('Failed to copy message:', err);
    }
  };

  const clearChat = () => {
    setMessages([{
      id: '1',
      role: 'assistant',
      content: `Chat cleared! I'm still here as Sophia in ${selectedPersonality.replace('_', ' ')} mode. How can I help you?`,
      timestamp: new Date().toISOString()
    }]);
  };

  return (
    <TooltipProvider>
      <Card className={`flex flex-col ${className}`} style={{ height }}>
        <CardHeader className="pb-3 border-b">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Bot className="h-5 w-5 text-purple-500" />
              Sophia AI
              <Badge variant="outline" className="ml-2">
                {personalities[selectedPersonality]?.name || 'Executive Advisor'}
              </Badge>
            </CardTitle>
            
            <div className="flex items-center gap-2">
              {/* Connection Status */}
              <Tooltip>
                <TooltipTrigger>
                  <div className={`h-2 w-2 rounded-full ${getConnectionStatusColor()}`} />
                </TooltipTrigger>
                <TooltipContent>
                  {connectionStatus.charAt(0).toUpperCase() + connectionStatus.slice(1)}
                </TooltipContent>
              </Tooltip>

              {/* Usage Indicator */}
              {userProfile && (
                <Tooltip>
                  <TooltipTrigger>
                    <Badge variant="secondary" className="text-xs">
                      {userProfile.api_usage_today}/{userProfile.api_quota_daily}
                    </Badge>
                  </TooltipTrigger>
                  <TooltipContent>
                    API Usage Today: {Math.round((userProfile.api_usage_today / userProfile.api_quota_daily) * 100)}%
                  </TooltipContent>
                </Tooltip>
              )}

              {/* Settings Toggle */}
              {showAdvancedControls && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowSettings(!showSettings)}
                  className="h-8 w-8 p-0"
                >
                  <Settings className="h-4 w-4" />
                </Button>
              )}

              {/* Clear Chat */}
              <Button
                variant="ghost"
                size="sm"
                onClick={clearChat}
                className="h-8 w-8 p-0"
              >
                <RefreshCw className="h-3 w-3" />
              </Button>
            </div>
          </div>

          {/* Advanced Controls */}
          {showSettings && showAdvancedControls && (
            <div className="mt-3 p-3 bg-gray-50 rounded-lg space-y-3">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {/* Personality Selector */}
                <div>
                  <label className="text-sm font-medium mb-1 block">Sophia's Personality</label>
                  <Select value={selectedPersonality} onValueChange={changePersonality}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {Object.entries(personalities).map(([value, personality]) => (
                        <SelectItem key={value} value={value}>
                          <div className="flex items-center gap-2">
                            {getPersonalityIcon(value)}
                            {personality.name}
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Search Context Selector */}
                <div>
                  <label className="text-sm font-medium mb-1 block">Search Context</label>
                  <Select value={selectedSearchContext} onValueChange={setSelectedSearchContext}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {Object.entries(searchContexts).map(([value, context]) => (
                        <SelectItem 
                          key={value} 
                          value={value}
                          disabled={context.requires_permission && !userProfile?.search_permissions.includes(value)}
                        >
                          <div className="flex items-center gap-2">
                            {getSearchContextIcon(value)}
                            {context.name}
                            {context.requires_permission && (
                              <Shield className="h-3 w-3 text-yellow-500" />
                            )}
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Current personality description */}
              {personalities[selectedPersonality] && (
                <div className="text-xs text-gray-600">
                  <strong>Current mode:</strong> {personalities[selectedPersonality].tone} • {personalities[selectedPersonality].focus}
                </div>
              )}
            </div>
          )}
        </CardHeader>

        <CardContent className="flex-1 overflow-hidden p-0">
          {/* Error Alert */}
          {error && (
            <Alert variant="destructive" className="m-4 mb-0">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Messages */}
          <div className="h-full overflow-y-auto p-4 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`group flex gap-3 p-4 rounded-lg transition-all duration-200 ${
                  message.role === 'user'
                    ? 'bg-blue-50 ml-8 border-l-4 border-blue-500'
                    : 'bg-gray-50 mr-8 border-l-4 border-purple-500'
                }`}
              >
                <div className="flex-shrink-0">
                  {message.role === 'user' ? (
                    <User className="h-6 w-6 text-blue-500" />
                  ) : (
                    <Bot className="h-6 w-6 text-purple-500" />
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-medium">
                      {message.role === 'user' ? 'You' : 'Sophia'}
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </span>
                    {message.metadata && (
                      <div className="flex items-center gap-1 text-xs text-gray-500">
                        <Clock className="h-3 w-3" />
                        {message.metadata.search_time_ms}ms
                        <Badge variant="outline" className="text-xs">
                          {Math.round(message.metadata.confidence_score * 100)}% confidence
                        </Badge>
                      </div>
                    )}
                  </div>

                  <div className="prose prose-sm max-w-none">
                    {message.content}
                  </div>

                  {/* Sources */}
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-3 space-y-2">
                      <div className="text-xs font-medium text-gray-600">Sources:</div>
                      <div className="space-y-1">
                        {message.sources.slice(0, 3).map((source, index) => (
                          <div key={index} className="flex items-center gap-2 text-xs bg-white p-2 rounded border">
                            {source.type === 'internal' ? (
                              <Database className="h-3 w-3 text-blue-500" />
                            ) : (
                              <Globe className="h-3 w-3 text-green-500" />
                            )}
                            <span className="font-medium">{source.source}</span>
                            <span className="text-gray-500">•</span>
                            <span>{Math.round(source.relevance_score * 100)}% relevant</span>
                            {source.url && (
                              <a 
                                href={source.url} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="text-blue-500 hover:underline ml-auto"
                              >
                                View
                              </a>
                            )}
                          </div>
                        ))}
                        {message.sources.length > 3 && (
                          <div className="text-xs text-gray-500">
                            +{message.sources.length - 3} more sources
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Metadata */}
                  {message.metadata && (
                    <div className="mt-2 flex items-center gap-4 text-xs text-gray-500">
                      {message.metadata.internal_results_count > 0 && (
                        <span className="flex items-center gap-1">
                          <Database className="h-3 w-3" />
                          {message.metadata.internal_results_count} internal
                        </span>
                      )}
                      {message.metadata.internet_results_count > 0 && (
                        <span className="flex items-center gap-1">
                          <Globe className="h-3 w-3" />
                          {message.metadata.internet_results_count} web
                        </span>
                      )}
                      <span>
                        {Math.round(message.metadata.synthesis_quality * 100)}% synthesis quality
                      </span>
                    </div>
                  )}

                  {/* Copy Button */}
                  <div className="flex items-center gap-2 mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => copyMessage(message.content)}
                      className="h-6 w-6 p-0"
                    >
                      <Copy className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}

            {/* Typing Indicator */}
            {typingIndicator && (
              <div className="flex gap-3 p-4 rounded-lg bg-gray-50 mr-8">
                <Bot className="h-6 w-6 text-purple-500" />
                <div className="flex items-center gap-1">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                    <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                  </div>
                  <span className="text-sm text-gray-500 ml-2">Sophia is thinking...</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t p-4">
            <div className="flex gap-2">
              <Input
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask Sophia anything... I have access to internal data and internet intelligence!"
                disabled={loading || connectionStatus === 'disconnected'}
                className="flex-1"
              />
              <Button
                onClick={sendMessage}
                disabled={loading || !input.trim() || connectionStatus === 'disconnected'}
                size="sm"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
            
            {/* Quick Actions */}
            <div className="flex flex-wrap gap-2 mt-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setInput("What are the latest trends in our industry?")}
                className="text-xs"
              >
                Industry Trends
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setInput("How are we performing compared to competitors?")}
                className="text-xs"
              >
                Competitive Analysis
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setInput("Show me our key metrics dashboard")}
                className="text-xs"
              >
                Key Metrics
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </TooltipProvider>
  );
}; 
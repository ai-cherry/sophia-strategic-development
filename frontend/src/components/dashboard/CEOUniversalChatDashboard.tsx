import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { 
  Bot, 
  User, 
  Send, 
  Search,
  BarChart3,
  TrendingUp,
  Users,
  DollarSign,
  Target,
  Zap,
  Globe,
  Settings,
  Mic,
  MicOff,
  Loader2,
  ExternalLink,
  Copy,
  Download,
  RefreshCw,
  Clock,
  Shield
} from 'lucide-react';

// Environment-aware configuration
const getBackendUrl = () => {
  return import.meta.env.VITE_BACKEND_URL || 'http://localhost:8001';
};

// Types
interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources?: Array<{
    type: string;
    title: string;
    relevance: number;
    timestamp: string;
  }>;
  suggestions?: string[];
  query_type?: string;
  processing_time_ms?: number;
}

interface DashboardMetrics {
  total_revenue: string;
  active_deals: number;
  team_performance: number;
  customer_satisfaction: number;
  recent_insights: Array<{
    title: string;
    description: string;
    priority: string;
    timestamp: string;
  }>;
  last_updated: string;
}

interface SearchContext {
  type: 'universal' | 'internal_only' | 'web_research' | 'deep_research' | 'blended' | 'business_intelligence';
  label: string;
  description: string;
  ceoOnly: boolean;
}

const CEOUniversalChatDashboard: React.FC = () => {
  // State management
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: `🎯 **Welcome to Sophia AI CEO Dashboard**

I'm your advanced AI assistant with enterprise-grade capabilities:

🧠 **Business Intelligence**: Real-time analysis of revenue, performance, and operational metrics
🌐 **Market Research**: Industry trends and competitive analysis  
👥 **Team Analytics**: Performance, productivity, and engagement insights
🎯 **Strategic Planning**: Growth opportunities and risk assessment

**Quick Actions:**
- "What's our revenue performance this quarter?"
- "How is our team performing compared to last quarter?"
- "What are the top opportunities in our pipeline?"
- "Show me the latest business insights"

**What would you like to explore today?**`,
      timestamp: new Date().toISOString(),
      suggestions: [
        "Analyze our revenue performance this quarter",
        "Review team performance metrics",
        "Check sales pipeline status",
        "Get market intelligence update"
      ]
    }
  ]);

  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [searchContext, setSearchContext] = useState<SearchContext['type']>('business_intelligence');
  const [isListening, setIsListening] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'connecting' | 'disconnected'>('connected');
  const [dashboardMetrics, setDashboardMetrics] = useState<DashboardMetrics | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Search context options
  const searchContexts: SearchContext[] = [
    {
      type: 'business_intelligence',
      label: 'Business Intelligence',
      description: 'Internal business data and analytics',
      ceoOnly: false
    },
    {
      type: 'universal',
      label: 'Universal Search',
      description: 'Search across all data sources',
      ceoOnly: false
    },
    {
      type: 'internal_only',
      label: 'Internal Only',
      description: 'Search only internal business data',
      ceoOnly: false
    },
    {
      type: 'web_research',
      label: 'Web Research',
      description: 'External market research and analysis',
      ceoOnly: false
    },
    {
      type: 'deep_research',
      label: 'Deep Research',
      description: 'Advanced intelligence gathering',
      ceoOnly: true
    },
    {
      type: 'blended',
      label: 'Blended Intelligence',
      description: 'Combine internal data with external research',
      ceoOnly: false
    }
  ];

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Load dashboard metrics on mount
  useEffect(() => {
    loadDashboardMetrics();
    
    // Refresh metrics every 5 minutes
    const interval = setInterval(loadDashboardMetrics, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  // API Functions
  const loadDashboardMetrics = async () => {
    try {
      const backendUrl = getBackendUrl();
      const response = await fetch(`${backendUrl}/api/v1/ceo/dashboard/summary`);
      if (response.ok) {
        const data = await response.json();
        setDashboardMetrics(data);
        setLastRefresh(new Date());
        setConnectionStatus('connected');
      } else {
        setConnectionStatus('disconnected');
      }
    } catch (error) {
      console.error('Failed to load dashboard metrics:', error);
      setConnectionStatus('disconnected');
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setLoading(true);
    setInput('');

    try {
      const backendUrl = getBackendUrl();
      const response = await fetch(`${backendUrl}/api/v1/ceo/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          search_context: searchContext,
          user_id: 'ceo_user',
          include_sources: true
        })
      });

      if (response.ok) {
        const data = await response.json();
        
        const assistantMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.response,
          timestamp: data.timestamp,
          sources: data.sources,
          suggestions: data.suggestions,
          query_type: data.query_type,
          processing_time_ms: data.processing_time_ms
        };

        setMessages(prev => [...prev, assistantMessage]);
        setConnectionStatus('connected');
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      console.error('Chat error:', error);
      setConnectionStatus('disconnected');
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'I apologize, but I encountered an error processing your request. Please try again.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
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

  const handleSuggestionClick = (suggestion: string) => {
    setInput(suggestion);
    inputRef.current?.focus();
  };

  const getSearchContextBadgeColor = (context: SearchContext['type']) => {
    switch (context) {
      case 'business_intelligence': return 'bg-blue-600';
      case 'universal': return 'bg-purple-600';
      case 'internal_only': return 'bg-green-600';
      case 'web_research': return 'bg-orange-600';
      case 'deep_research': return 'bg-red-600';
      case 'blended': return 'bg-indigo-600';
      default: return 'bg-gray-600';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return 'text-green-400';
      case 'connecting': return 'text-yellow-400';
      case 'disconnected': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getConnectionStatusIcon = () => {
    switch (connectionStatus) {
      case 'connected': return <Shield className="w-3 h-3" />;
      case 'connecting': return <Loader2 className="w-3 h-3 animate-spin" />;
      case 'disconnected': return <ExternalLink className="w-3 h-3" />;
      default: return <Shield className="w-3 h-3" />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-4">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">
              CEO Dashboard - Universal Intelligence
            </h1>
            <p className="text-gray-300">
              Advanced AI-powered business intelligence and chat interface
            </p>
          </div>
          
          <div className="flex items-center gap-4">
            <div className={`flex items-center gap-2 text-sm ${getConnectionStatusColor()}`}>
              {getConnectionStatusIcon()}
              {connectionStatus}
            </div>
            <Badge className={`${getSearchContextBadgeColor(searchContext)} text-white`}>
              {searchContexts.find(c => c.type === searchContext)?.label}
            </Badge>
            <Button
              onClick={loadDashboardMetrics}
              variant="outline"
              size="sm"
              className="text-white border-white/20 hover:bg-white/10"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
          </div>
        </div>

        {/* Dashboard Metrics */}
        {dashboardMetrics && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="bg-white/10 border-white/20 text-white">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-300">Total Revenue</p>
                    <p className="text-2xl font-bold">{dashboardMetrics.total_revenue}</p>
                  </div>
                  <DollarSign className="w-8 h-8 text-green-400" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white/10 border-white/20 text-white">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-300">Active Deals</p>
                    <p className="text-2xl font-bold">{dashboardMetrics.active_deals}</p>
                  </div>
                  <Target className="w-8 h-8 text-blue-400" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white/10 border-white/20 text-white">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-300">Team Performance</p>
                    <p className="text-2xl font-bold">{dashboardMetrics.team_performance}%</p>
                  </div>
                  <Users className="w-8 h-8 text-purple-400" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white/10 border-white/20 text-white">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-300">Customer Satisfaction</p>
                    <p className="text-2xl font-bold">{dashboardMetrics.customer_satisfaction}/5</p>
                  </div>
                  <TrendingUp className="w-8 h-8 text-orange-400" />
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Main Chat Interface */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          
          {/* Chat Area */}
          <div className="lg:col-span-3">
            <Card className="bg-white/10 border-white/20 h-[600px] flex flex-col">
              <CardHeader className="pb-3 border-b border-white/10">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg flex items-center gap-2 text-white">
                    <Bot className="h-5 w-5 text-purple-400" />
                    Sophia AI Universal Chat
                  </CardTitle>
                  
                  {/* Search Context Selector */}
                  <div className="flex flex-wrap gap-2">
                    {searchContexts.map((context) => (
                      <button
                        key={context.type}
                        onClick={() => setSearchContext(context.type)}
                        className={`px-2 py-1 rounded text-xs transition-all ${
                          searchContext === context.type
                            ? `${getSearchContextBadgeColor(context.type)} text-white`
                            : 'bg-white/10 text-gray-300 hover:bg-white/20'
                        }`}
                        title={context.description}
                      >
                        {context.label} {context.ceoOnly && '👑'}
                      </button>
                    ))}
                  </div>
                </div>
              </CardHeader>
              
              <CardContent className="flex-1 flex flex-col p-0">
                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`max-w-[80%] ${message.role === 'user' ? 'order-2' : 'order-1'}`}>
                        <div
                          className={`rounded-lg p-3 ${
                            message.role === 'user'
                              ? 'bg-purple-600 text-white'
                              : 'bg-white/10 text-white border border-white/20'
                          }`}
                        >
                          <div className="whitespace-pre-wrap">{message.content}</div>
                          
                          {/* Sources */}
                          {message.sources && message.sources.length > 0 && (
                            <div className="mt-3 space-y-1">
                              <p className="text-xs text-gray-300">Sources:</p>
                              {message.sources.map((source, idx) => (
                                <div key={idx} className="text-xs bg-white/5 rounded p-2">
                                  <div className="flex items-center justify-between">
                                    <span className="font-medium">{source.title}</span>
                                    <Badge variant="outline" className="text-xs">
                                      {Math.round(source.relevance * 100)}%
                                    </Badge>
                                  </div>
                                  <p className="text-gray-400 mt-1">{source.type}</p>
                                </div>
                              ))}
                            </div>
                          )}
                          
                          {/* Suggestions */}
                          {message.suggestions && message.suggestions.length > 0 && (
                            <div className="mt-3 space-y-2">
                              <p className="text-xs text-gray-300">Suggested follow-ups:</p>
                              <div className="flex flex-wrap gap-2">
                                {message.suggestions.map((suggestion, idx) => (
                                  <button
                                    key={idx}
                                    onClick={() => handleSuggestionClick(suggestion)}
                                    className="text-xs bg-white/10 hover:bg-white/20 rounded px-2 py-1 transition-colors"
                                  >
                                    {suggestion}
                                  </button>
                                ))}
                              </div>
                            </div>
                          )}
                          
                          <div className="flex items-center justify-between mt-2 text-xs text-gray-400">
                            <span>{formatTimestamp(message.timestamp)}</span>
                            {message.processing_time_ms && (
                              <span>{message.processing_time_ms}ms</span>
                            )}
                          </div>
                        </div>
                      </div>
                      
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        message.role === 'user' ? 'bg-purple-600 order-1' : 'bg-white/10 order-2'
                      }`}>
                        {message.role === 'user' ? (
                          <User className="w-4 h-4 text-white" />
                        ) : (
                          <Bot className="w-4 h-4 text-purple-400" />
                        )}
                      </div>
                    </div>
                  ))}
                  
                  {loading && (
                    <div className="flex justify-start">
                      <div className="bg-white/10 rounded-lg p-3 border border-white/20">
                        <div className="flex items-center gap-2">
                          <Loader2 className="w-4 h-4 animate-spin text-purple-400" />
                          <span className="text-white">Thinking...</span>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  <div ref={messagesEndRef} />
                </div>
                
                {/* Input */}
                <div className="border-t border-white/10 p-4">
                  <div className="flex gap-2">
                    <div className="flex-1 relative">
                      <Input
                        ref={inputRef}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Ask about your business, analyze data, or explore opportunities..."
                        className="bg-white/10 border-white/20 text-white placeholder-gray-400 pr-10"
                        disabled={loading}
                      />
                      <button
                        onClick={() => setIsListening(!isListening)}
                        className={`absolute right-2 top-1/2 transform -translate-y-1/2 p-1 rounded ${
                          isListening ? 'text-red-400' : 'text-gray-400 hover:text-white'
                        }`}
                      >
                        {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                      </button>
                    </div>
                    <Button
                      onClick={sendMessage}
                      disabled={loading || !input.trim()}
                      className="bg-purple-600 hover:bg-purple-700 text-white"
                    >
                      <Send className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
          
          {/* Sidebar - Recent Insights */}
          <div className="lg:col-span-1">
            <Card className="bg-white/10 border-white/20 h-[600px]">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-purple-400" />
                  Recent Insights
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {dashboardMetrics?.recent_insights.map((insight, idx) => (
                  <div key={idx} className="bg-white/5 rounded-lg p-3">
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="text-sm font-medium text-white">{insight.title}</h4>
                      <Badge 
                        variant={insight.priority === 'high' ? 'destructive' : 
                                insight.priority === 'medium' ? 'default' : 'secondary'}
                        className="text-xs"
                      >
                        {insight.priority}
                      </Badge>
                    </div>
                    <p className="text-xs text-gray-300">{insight.description}</p>
                    <div className="flex items-center gap-1 mt-2 text-xs text-gray-400">
                      <Clock className="w-3 h-3" />
                      {formatTimestamp(insight.timestamp)}
                    </div>
                  </div>
                ))}
                
                {dashboardMetrics && (
                  <div className="text-xs text-gray-400 mt-4">
                    Last updated: {formatTimestamp(dashboardMetrics.last_updated)}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CEOUniversalChatDashboard; 
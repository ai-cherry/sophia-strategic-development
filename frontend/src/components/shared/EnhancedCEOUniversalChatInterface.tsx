import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { 
  Bot, 
  User, 
  Code, 
  Globe, 
  Zap, 
  Settings, 
  Search,
  Palette,
  Database,
  Send,
  Mic,
  MicOff,
  Loader2,
  ExternalLink,
  Copy,
  Download,
  Eye,
  Layers
} from 'lucide-react';

// Types
interface EnhancedCEOChatProps {
  userId?: string;
  height?: string;
  className?: string;
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  sources?: Array<{
    type: string;
    name: string;
    description: string;
    url?: string;
  }>;
  actions?: Array<{
    type: string;
    description: string;
    onclick?: () => void;
  }>;
  suggestions?: string[];
  timestamp: string;
  queryType?: string;
  processingTime?: number;
}

interface SearchContext {
  type: 'internal_only' | 'web_research' | 'deep_research' | 'blended' | 'mcp_tools' | 'coding_agents';
  label: string;
  description: string;
  ceoOnly: boolean;
}

interface DesignOption {
  id: string;
  name: string;
  description: string;
  components: string[];
  features: string[];
  assets?: Array<{
    type: string;
    url: string;
    metadata: any;
  }>;
}

const EnhancedCEOUniversalChatInterface: React.FC<EnhancedCEOChatProps> = ({
  userId = "ceo_user",
  height = "600px",
  className = ""
}) => {
  // State management
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content: `🎯 **Welcome to Sophia AI Enhanced CEO Platform**

I'm your advanced AI assistant with enterprise-grade capabilities:

�� **Business Intelligence**: Deep analysis of internal data with Snowflake Cortex AI
🌐 **Web Research**: Real-time market intelligence and competitive analysis  
🕵️ **Deep Research**: Advanced web scraping and strategic intelligence (CEO-only)
💻 **Coding Agents**: AI-powered code analysis and architecture review (CEO-only)
🎨 **UI/UX Design**: Advanced design generation with Portkey multi-model routing (CEO-only)
⚙️ **MCP Integration**: Direct access to all MCP servers and tools (CEO-only)

**What would you like to explore today?**`,
      timestamp: new Date().toISOString(),
      suggestions: [
        "Analyze our Q4 revenue performance",
        "Research competitor pricing strategies",
        "Review our codebase architecture",
        "Generate a new dashboard design",
        "Deep dive into market opportunities"
      ]
    }
  ]);

  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('chat');
  const [searchContext, setSearchContext] = useState<SearchContext['type']>('blended');
  const [isListening, setIsListening] = useState(false);
  const [designMode, setDesignMode] = useState(false);
  const [codingMode, setCodingMode] = useState(false);
  const [websocket, setWebsocket] = useState<WebSocket | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'disconnected' | 'connecting' | 'connected'>('disconnected');

  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Search context options
  const searchContexts: SearchContext[] = [
    {
      type: 'internal_only',
      label: 'Internal Only',
      description: 'Search only internal business data',
      ceoOnly: false
    },
    {
      type: 'web_research',
      label: 'Web Research',
      description: 'Standard web research and analysis',
      ceoOnly: false
    },
    {
      type: 'deep_research',
      label: 'Deep Research',
      description: 'Advanced scraping and intelligence gathering',
      ceoOnly: true
    },
    {
      type: 'blended',
      label: 'Blended Intelligence',
      description: 'Combine internal data with external research',
      ceoOnly: false
    },
    {
      type: 'mcp_tools',
      label: 'MCP Tools',
      description: 'Direct access to MCP servers and tools',
      ceoOnly: true
    },
    {
      type: 'coding_agents',
      label: 'Coding Agents',
      description: 'AI-powered code analysis and development',
      ceoOnly: true
    }
  ];

  // WebSocket connection
  useEffect(() => {
    connectWebSocket();
    return () => {
      if (websocket) {
        websocket.close();
      }
    };
  }, []);

  const connectWebSocket = useCallback(() => {
    setConnectionStatus('connecting');
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.host}/api/v1/ceo-chat/ws/${userId}`;
    
    try {
      const ws = new WebSocket(wsUrl);
      
      ws.onopen = () => {
        setConnectionStatus('connected');
        setWebsocket(ws);
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
      };
      
      ws.onclose = () => {
        setConnectionStatus('disconnected');
        setWebsocket(null);
        // Attempt to reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('disconnected');
      };
      
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      setConnectionStatus('disconnected');
    }
  }, [userId]);

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'welcome':
        console.log('Connected to enhanced CEO chat');
        break;
      case 'response':
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: data.content,
          sources: data.sources,
          actions: data.actions,
          suggestions: data.suggestions,
          timestamp: data.metadata?.timestamp || new Date().toISOString(),
          queryType: data.metadata?.query_type,
          processingTime: data.metadata?.processing_time
        }]);
        setLoading(false);
        break;
      case 'design_response':
        handleDesignResponse(data);
        break;
      case 'typing':
        // Handle typing indicator
        break;
      case 'error':
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: `❌ Error: ${data.message}`,
          timestamp: new Date().toISOString()
        }]);
        setLoading(false);
        break;
    }
  };

  const handleDesignResponse = (data: any) => {
    const designContent = `🎨 **Design Generation Complete**

Generated ${data.options?.length || 0} design options:

${data.options?.map((option: DesignOption, index: number) => `
**Option ${index + 1}: ${option.name}**
${option.description}
Components: ${option.components?.join(', ')}
Features: ${option.features?.join(', ')}
`).join('\n') || ''}

**Recommendations:**
${data.recommendations?.map((rec: string) => `• ${rec}`).join('\n') || ''}`;

    setMessages(prev => [...prev, {
      role: 'assistant',
      content: designContent,
      timestamp: new Date().toISOString()
    }]);
    setLoading(false);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setLoading(true);
    setInput('');

    if (websocket && connectionStatus === 'connected') {
      // Send via WebSocket
      websocket.send(JSON.stringify({
        type: designMode ? 'design' : 'chat',
        data: designMode ? {
          description: input,
          project_name: "CEO Dashboard Enhancement",
          framework: "react_typescript",
          style: "glassmorphism"
        } : {
          message: input,
          user_id: userId,
          access_level: "ceo",
          search_context: searchContext,
          coding_mode: codingMode,
          design_mode: designMode
        }
      }));
    } else {
      // Fallback to REST API
      try {
        const endpoint = designMode ? '/api/v1/ceo-chat/design' : '/api/v1/ceo-chat/chat';
        const payload = designMode ? {
          description: input,
          project_name: "CEO Dashboard Enhancement",
          framework: "react_typescript",
          style: "glassmorphism"
        } : {
          message: input,
          user_id: userId,
          access_level: "ceo",
          search_context: searchContext,
          coding_mode: codingMode,
          design_mode: designMode
        };

        const response = await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        const data = await response.json();
        
        if (designMode) {
          handleDesignResponse(data);
        } else {
          setMessages(prev => [...prev, {
            role: 'assistant',
            content: data.response,
            sources: data.sources,
            actions: data.actions,
            suggestions: data.suggestions,
            timestamp: data.metadata?.timestamp || new Date().toISOString(),
            queryType: data.metadata?.query_type,
            processingTime: data.metadata?.processing_time
          }]);
        }
        
      } catch (error) {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: `Error: ${error instanceof Error ? error.message : 'Unknown error occurred'}`,
          timestamp: new Date().toISOString()
        }]);
      } finally {
        setLoading(false);
      }
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const getSearchContextBadgeColor = (contextType: SearchContext['type']) => {
    const colors = {
      'internal_only': 'bg-blue-500',
      'web_research': 'bg-green-500',
      'deep_research': 'bg-red-500',
      'blended': 'bg-purple-500',
      'mcp_tools': 'bg-orange-500',
      'coding_agents': 'bg-cyan-500'
    };
    return colors[contextType] || 'bg-gray-500';
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
      case 'connected': return '🟢';
      case 'connecting': return '🟡';
      case 'disconnected': return '🔴';
      default: return '⚪';
    }
  };

  return (
    <Card className={`flex flex-col glassmorphism-card ${className}`} style={{ height }}>
      <CardHeader className="pb-3 border-b border-white/10">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2 text-white">
            <Bot className="h-5 w-5 text-purple-400" />
            Sophia AI Enhanced CEO Platform
          </CardTitle>
          <div className="flex items-center gap-4 text-xs text-gray-300">
            <span className={getConnectionStatusColor()}>
              {getConnectionStatusIcon()} {connectionStatus}
            </span>
            <Badge 
              className={`text-xs text-white ${getSearchContextBadgeColor(searchContext)}`}
            >
              {searchContexts.find(c => c.type === searchContext)?.label}
            </Badge>
          </div>
        </div>
        
        {/* Search Context Selector */}
        <div className="flex flex-wrap gap-2 mt-3">
          {searchContexts.map((context) => (
            <button
              key={context.type}
              onClick={() => setSearchContext(context.type)}
              disabled={context.ceoOnly && userId !== "ceo_user"}
              className={`px-3 py-1 rounded-lg text-xs transition-all ${
                searchContext === context.type
                  ? `${getSearchContextBadgeColor(context.type)} text-white`
                  : context.ceoOnly && userId !== "ceo_user"
                  ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                  : 'bg-white/10 text-gray-300 hover:bg-white/20'
              }`}
              title={context.description}
            >
              {context.label} {context.ceoOnly && '👑'}
            </button>
          ))}
        </div>

        {/* Mode Toggles */}
        <div className="flex gap-2 mt-2">
          <button
            onClick={() => setCodingMode(!codingMode)}
            className={`px-3 py-1 rounded-lg text-xs flex items-center gap-1 transition-all ${
              codingMode ? 'bg-cyan-500 text-white' : 'bg-white/10 text-gray-300 hover:bg-white/20'
            }`}
          >
            <Code className="w-3 h-3" />
            Coding Mode
          </button>
          <button
            onClick={() => setDesignMode(!designMode)}
            className={`px-3 py-1 rounded-lg text-xs flex items-center gap-1 transition-all ${
              designMode ? 'bg-pink-500 text-white' : 'bg-white/10 text-gray-300 hover:bg-white/20'
            }`}
          >
            <Palette className="w-3 h-3" />
            Design Mode
          </button>
        </div>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col p-4">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
          <TabsList className="grid w-full grid-cols-4 bg-white/5">
            <TabsTrigger value="chat" className="flex items-center gap-1 text-xs">
              <Bot className="w-3 h-3" />
              Chat
            </TabsTrigger>
            <TabsTrigger value="research" className="flex items-center gap-1 text-xs">
              <Globe className="w-3 h-3" />
              Research
            </TabsTrigger>
            <TabsTrigger value="design" className="flex items-center gap-1 text-xs">
              <Palette className="w-3 h-3" />
              Design
            </TabsTrigger>
            <TabsTrigger value="analytics" className="flex items-center gap-1 text-xs">
              <Database className="w-3 h-3" />
              Analytics
            </TabsTrigger>
          </TabsList>

          <TabsContent value="chat" className="flex-1 flex flex-col mt-4">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto space-y-4 pr-2">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg p-3 ${
                      message.role === 'user'
                        ? 'bg-purple-600 text-white'
                        : 'bg-white/10 text-gray-100 border border-white/20'
                    }`}
                  >
                    <div className="flex items-start gap-2">
                      {message.role === 'assistant' && (
                        <Bot className="w-4 h-4 text-purple-400 mt-0.5 flex-shrink-0" />
                      )}
                      {message.role === 'user' && (
                        <User className="w-4 h-4 text-white mt-0.5 flex-shrink-0" />
                      )}
                      <div className="flex-1">
                        <div className="prose prose-invert prose-sm max-w-none">
                          {message.content.split('\n').map((line, i) => (
                            <p key={i} className="mb-2 last:mb-0">
                              {line}
                            </p>
                          ))}
                        </div>
                        
                        {/* Processing time and query type */}
                        {message.processingTime && (
                          <div className="text-xs text-gray-400 mt-2 flex items-center gap-2">
                            <Zap className="w-3 h-3" />
                            {message.processingTime.toFixed(2)}s
                            {message.queryType && (
                              <Badge variant="outline" className="text-xs">
                                {message.queryType}
                              </Badge>
                            )}
                          </div>
                        )}
                        
                        {/* Sources */}
                        {message.sources && message.sources.length > 0 && (
                          <div className="mt-3 space-y-2">
                            <p className="text-xs font-medium text-gray-300">Sources:</p>
                            {message.sources.map((source, i) => (
                              <div key={i} className="bg-white/5 rounded p-2 text-xs">
                                <div className="flex items-center gap-2">
                                  <ExternalLink className="w-3 h-3 text-blue-400" />
                                  <span className="font-medium">{source.name}</span>
                                  <Badge variant="outline" className="text-xs">
                                    {source.type}
                                  </Badge>
                                </div>
                                <p className="text-gray-400 mt-1">{source.description}</p>
                              </div>
                            ))}
                          </div>
                        )}
                        
                        {/* Actions */}
                        {message.actions && message.actions.length > 0 && (
                          <div className="mt-3 space-y-2">
                            <p className="text-xs font-medium text-gray-300">Actions:</p>
                            <div className="flex flex-wrap gap-2">
                              {message.actions.map((action, i) => (
                                <Button
                                  key={i}
                                  size="sm"
                                  variant="outline"
                                  className="text-xs bg-white/5 border-white/20 hover:bg-white/10"
                                  onClick={action.onclick}
                                >
                                  {action.description}
                                </Button>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        {/* Suggestions */}
                        {message.suggestions && message.suggestions.length > 0 && (
                          <div className="mt-3 space-y-2">
                            <p className="text-xs font-medium text-gray-300">Suggestions:</p>
                            <div className="flex flex-wrap gap-2">
                              {message.suggestions.map((suggestion, i) => (
                                <button
                                  key={i}
                                  onClick={() => setInput(suggestion)}
                                  className="text-xs bg-white/5 hover:bg-white/10 rounded px-2 py-1 text-left border border-white/10"
                                >
                                  {suggestion}
                                </button>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                    
                    <div className="text-xs text-gray-400 mt-2">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              ))}
              
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-white/10 rounded-lg p-3 border border-white/20">
                    <div className="flex items-center gap-2">
                      <Bot className="w-4 h-4 text-purple-400" />
                      <Loader2 className="w-4 h-4 animate-spin text-purple-400" />
                      <span className="text-sm text-gray-300">Thinking...</span>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
            
            {/* Input */}
            <div className="mt-4 flex gap-2">
              <div className="flex-1 relative">
                <Input
                  ref={inputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={
                    designMode 
                      ? "Describe the UI/UX component you want to create..."
                      : codingMode
                      ? "Ask about code analysis, architecture, or development..."
                      : "Ask about your business, research markets, or explore opportunities..."
                  }
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
          </TabsContent>
          
          <TabsContent value="research" className="flex-1 mt-4">
            <div className="text-center text-gray-400 py-8">
              <Globe className="w-12 h-12 mx-auto mb-4" />
              <p>Advanced web research capabilities</p>
              <p className="text-sm mt-2">Switch to Research mode in chat to access deep web intelligence</p>
            </div>
          </TabsContent>
          
          <TabsContent value="design" className="flex-1 mt-4">
            <div className="text-center text-gray-400 py-8">
              <Palette className="w-12 h-12 mx-auto mb-4" />
              <p>AI-powered UI/UX design generation</p>
              <p className="text-sm mt-2">Switch to Design mode in chat to create components and dashboards</p>
            </div>
          </TabsContent>
          
          <TabsContent value="analytics" className="flex-1 mt-4">
            <div className="text-center text-gray-400 py-8">
              <Database className="w-12 h-12 mx-auto mb-4" />
              <p>Business intelligence and analytics</p>
              <p className="text-sm mt-2">Real-time insights from your Snowflake data</p>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};

export default EnhancedCEOUniversalChatInterface;

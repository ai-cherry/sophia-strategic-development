import React, { useState, useEffect, useRef } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
// Removed ScrollArea import - using regular div with overflow
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Send,
  Loader2,
  MessageSquare,
  FolderOpen,
  CheckSquare,
  Activity,
  Target,
  Search,
  Bot,
  Brain,
  Database,
  Server,
  AlertCircle,
  CheckCircle,
  Wifi,
  WifiOff
} from 'lucide-react';
import apiClient from '../services/apiClient';
import { useNavigate } from 'react-router-dom';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: string;
  citations?: Array<{
    source: string;
    confidence: number;
    url?: string;
  }>;
  suggestions?: string[];
  metadata?: {
    confidence?: number;
    model_used?: string;
    processing_time?: string;
    data_sources_used?: string[];
  };
}

const UnifiedChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('chat');
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const ws = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const reconnectTimeout = useRef<NodeJS.Timeout | null>(null);

  // Get or generate user ID
  const userId = localStorage.getItem('userId') || 'user_' + Math.random().toString(36).substr(2, 9);
  if (!localStorage.getItem('userId')) {
    localStorage.setItem('userId', userId);
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // WebSocket connection
  const connectWebSocket = () => {
    const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';

    try {
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setError(null);

        // Send initial connection message
        ws.current?.send(JSON.stringify({
          type: 'connection',
          userId: userId,
          context: activeTab
        }));
      };

      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('Received message:', data);

          if (data.type === 'chat_response' || data.type === 'integrated_response') {
            const responseData = data.data || data;
            const assistantMessage: Message = {
              id: (Date.now() + 1).toString(),
              type: 'assistant',
              content: responseData.content || responseData.response,
              timestamp: new Date().toISOString(),
              citations: responseData.citations || responseData.sources,
              suggestions: responseData.suggestions,
              metadata: responseData.metadata
            };

            setMessages(prev => [...prev, assistantMessage]);
            setIsLoading(false);
          } else if (data.type === 'error') {
            setError(data.message);
            setIsLoading(false);
          } else if (data.type === 'pong') {
            // Heartbeat response
          }
        } catch (e) {
          console.error('Error parsing message:', e);
        }
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setError('Connection error. Using fallback API.');
        setIsConnected(false);
      };

      ws.current.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);

        // Attempt to reconnect after 5 seconds
        if (reconnectTimeout.current) {
          clearTimeout(reconnectTimeout.current);
        }
        reconnectTimeout.current = setTimeout(connectWebSocket, 5000);
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      setIsConnected(false);
    }
  };

  useEffect(() => {
    connectWebSocket();

    // Heartbeat to keep connection alive
    const heartbeatInterval = setInterval(() => {
      if (ws.current && ws.current.readyState === WebSocket.OPEN) {
        ws.current.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000);

    // Cleanup
    return () => {
      clearInterval(heartbeatInterval);
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
      if (ws.current) {
        ws.current.close();
      }
    };
  }, []);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setError(null);

    try {
      // Try WebSocket first
      if (ws.current && ws.current.readyState === WebSocket.OPEN) {
        ws.current.send(JSON.stringify({
          type: 'chat_message',
          message: input,
          context: activeTab,
          metadata: {
            search_context: activeTab,
            user_id: userId,
            session_id: Date.now().toString()
          }
        }));
      } else {
        // Fallback to HTTP API
        const response = await apiClient.post('/api/v3/chat/unified', {
          message: input,
          context: activeTab,
          sessionId: Date.now().toString(),
        });

        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: response.data.response,
          timestamp: new Date().toISOString(),
          citations: response.data.citations,
          suggestions: response.data.suggestions,
          metadata: response.data.metadata,
        };

        setMessages(prev => [...prev, assistantMessage]);
        setIsLoading(false);
      }
    } catch (error) {
      console.error('Chat error:', error);
      setError('Failed to send message. Please try again.');
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInput(suggestion);
  };

  return (
    <div className="flex h-screen bg-gray-950">
      {/* Left Sidebar with Tabs */}
      <div className="w-64 bg-gray-900 border-r border-gray-800">
        <div className="p-4">
          <h1 className="text-xl font-bold text-gray-50 flex items-center gap-2">
            <Bot className="h-5 w-5 text-purple-500" />
            Sophia AI
          </h1>
          <div className="flex items-center gap-2 mt-2">
            {isConnected ? (
              <Badge className="bg-emerald-500/20 text-emerald-500 border-emerald-500/30 text-xs">
                <Wifi className="h-3 w-3 mr-1" />
                Connected
              </Badge>
            ) : (
              <Badge className="bg-amber-500/20 text-amber-500 border-amber-500/30 text-xs">
                <WifiOff className="h-3 w-3 mr-1" />
                Offline Mode
              </Badge>
            )}
          </div>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} orientation="vertical" className="h-full">
          <TabsList className="flex flex-col h-auto bg-transparent p-2 gap-1">
            <TabsTrigger
              value="chat"
              className="w-full justify-start gap-2 data-[state=active]:bg-gray-800 data-[state=active]:text-purple-500"
            >
              <MessageSquare className="h-4 w-4" />
              Unified Chat
            </TabsTrigger>

            <TabsTrigger
              value="knowledge"
              className="w-full justify-start gap-2 data-[state=active]:bg-gray-800 data-[state=active]:text-purple-500"
            >
              <FolderOpen className="h-4 w-4" />
              Knowledge Management
            </TabsTrigger>

            <TabsTrigger
              value="projects"
              className="w-full justify-start gap-2 data-[state=active]:bg-gray-800 data-[state=active]:text-purple-500"
            >
              <CheckSquare className="h-4 w-4" />
              Project Management
            </TabsTrigger>

            <TabsTrigger
              value="system"
              className="w-full justify-start gap-2 data-[state=active]:bg-gray-800 data-[state=active]:text-purple-500"
            >
              <Activity className="h-4 w-4" />
              System Status
            </TabsTrigger>

            <TabsTrigger
              value="okrs"
              className="w-full justify-start gap-2 data-[state=active]:bg-gray-800 data-[state=active]:text-purple-500"
            >
              <Target className="h-4 w-4" />
              Company OKRs
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col">
        <Tabs value={activeTab} className="flex-1 flex flex-col">
          {/* Chat Tab */}
          <TabsContent value="chat" className="flex-1 flex flex-col m-0">
            <ChatPanel
              messages={messages}
              input={input}
              setInput={setInput}
              sendMessage={sendMessage}
              isLoading={isLoading}
              error={error}
              isConnected={isConnected}
              onSuggestionClick={handleSuggestionClick}
            />
          </TabsContent>

          {/* Knowledge Management Tab */}
          <TabsContent value="knowledge" className="flex-1 p-6">
            <KnowledgeManagementPanel />
          </TabsContent>

          {/* Project Management Tab */}
          <TabsContent value="projects" className="flex-1 p-6">
            <ProjectManagementPanel />
          </TabsContent>

          {/* System Status Tab */}
          <TabsContent value="system" className="flex-1 p-6">
            <SystemStatusPanel />
          </TabsContent>

          {/* Company OKRs Tab */}
          <TabsContent value="okrs" className="flex-1 p-6">
            <CompanyOKRsPanel />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

// Chat Panel Component with enhanced features
const ChatPanel: React.FC<{
  messages: Message[];
  input: string;
  setInput: (value: string) => void;
  sendMessage: () => void;
  isLoading: boolean;
  error: string | null;
  isConnected: boolean;
  onSuggestionClick: (suggestion: string) => void;
}> = ({ messages, input, setInput, sendMessage, isLoading, error, isConnected, onSuggestionClick }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const suggestions = [
    "What's our sales performance this quarter?",
    "Show me at-risk projects",
    "How is our infrastructure performing?",
    "What are competitors doing in AI?"
  ];

  return (
    <>
      {/* Chat Header */}
      <div className="p-4 border-b border-gray-800 bg-gray-900">
        <h2 className="text-lg font-semibold text-gray-50">Unified Intelligence Chat</h2>
        <p className="text-sm text-gray-400">
          Dynamic access to your entire ecosystem - databases, integrations, and the web
        </p>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert className="m-4 bg-red-900/20 border-red-800">
          <AlertCircle className="h-4 w-4 text-red-500" />
          <AlertDescription className="text-red-200">{error}</AlertDescription>
        </Alert>
      )}

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto space-y-6">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <Brain className="h-16 w-16 text-gray-300 mx-auto mb-4" />
              <h2 className="text-2xl font-semibold text-gray-700 mb-2">
                Welcome to Sophia AI
              </h2>
              <p className="text-gray-500 mb-8">
                Ask me anything about your business data, projects, or insights
              </p>
              
              {/* Suggestions */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
                {suggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => onSuggestionClick(suggestion)}
                    className="text-left p-4 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-all duration-200"
                  >
                    <p className="text-sm text-gray-700">{suggestion}</p>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-3xl rounded-lg p-4 ${
                      message.type === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{message.content}</p>
                    
                    {/* Sources */}
                    {message.citations && message.citations.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-gray-200">
                        <p className="text-xs font-semibold mb-2">Sources:</p>
                        <div className="flex flex-wrap gap-2">
                          {message.citations.map((citation, idx) => (
                            <span
                              key={idx}
                              className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs bg-white/20"
                            >
                              {citation.source}
                              {citation.confidence && (
                                <span className="ml-1 text-gray-400">
                                  ({Math.round(citation.confidence * 100)}%)
                                </span>
                              )}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {/* Metadata */}
                    {message.metadata && (
                      <div className="mt-2 text-xs opacity-70">
                        {message.metadata.confidence && (
                          <span>Confidence: {Math.round(message.metadata.confidence * 100)}%</span>
                        )}
                        {message.metadata.data_sources_used && (
                          <span className="ml-3">
                            Sources: {message.metadata.data_sources_used.join(', ')}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 rounded-lg p-4">
                    <Loader2 className="h-5 w-5 animate-spin text-gray-600" />
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </>
          )}
        </div>
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-gray-800 bg-gray-900">
        <div className="flex gap-2 max-w-4xl mx-auto">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
            placeholder="Ask anything about your business, projects, systems, or the market..."
            className="flex-1 bg-gray-800 border-gray-700 text-gray-50 placeholder-gray-400"
            disabled={isLoading}
          />
          <Button
            onClick={sendMessage}
            disabled={!input.trim() || isLoading}
            className="bg-purple-600 hover:bg-purple-700 text-white"
          >
            {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          </Button>
        </div>
      </div>
    </>
  );
};

// Knowledge Management Panel
const KnowledgeManagementPanel: React.FC = () => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-50 mb-2">Knowledge Management</h2>
        <p className="text-gray-400">Search and manage your organization's knowledge base</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-gray-900 border-gray-800">
          <div className="p-6">
            <Database className="h-8 w-8 text-purple-500 mb-3" />
            <h3 className="text-lg font-semibold text-gray-50 mb-1">Documents</h3>
            <p className="text-2xl font-bold text-gray-50">1,247</p>
            <p className="text-sm text-gray-400">Total indexed</p>
          </div>
        </Card>

        <Card className="bg-gray-900 border-gray-800">
          <div className="p-6">
            <Search className="h-8 w-8 text-emerald-500 mb-3" />
            <h3 className="text-lg font-semibold text-gray-50 mb-1">Searches</h3>
            <p className="text-2xl font-bold text-gray-50">3,892</p>
            <p className="text-sm text-gray-400">This month</p>
          </div>
        </Card>

        <Card className="bg-gray-900 border-gray-800">
          <div className="p-6">
            <Bot className="h-8 w-8 text-blue-500 mb-3" />
            <h3 className="text-lg font-semibold text-gray-50 mb-1">AI Insights</h3>
            <p className="text-2xl font-bold text-gray-50">156</p>
            <p className="text-sm text-gray-400">Generated today</p>
          </div>
        </Card>
      </div>

      <Card className="bg-gray-900 border-gray-800">
        <div className="p-6">
          <h3 className="text-lg font-semibold text-gray-50 mb-4">Recent Documents</h3>
          <div className="space-y-3">
            {['Q1 2025 Strategy', 'Product Roadmap', 'Sales Playbook', 'Engineering Guidelines'].map((doc) => (
              <div key={doc} className="flex items-center justify-between p-3 bg-gray-800 rounded-lg">
                <span className="text-gray-50">{doc}</span>
                <Badge className="bg-emerald-500/20 text-emerald-500 border-emerald-500/30">Active</Badge>
              </div>
            ))}
          </div>
        </div>
      </Card>
    </div>
  );
};

// Project Management Panel
const ProjectManagementPanel: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-50 mb-2">Project Management Hub</h2>
        <p className="text-gray-400">Unified view of Linear, Asana, Notion, and Slack projects</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-gray-900 border-gray-800">
          <div className="p-6">
            <h3 className="text-sm font-medium text-gray-400 mb-1">Linear</h3>
            <p className="text-2xl font-bold text-gray-50">23</p>
            <p className="text-sm text-emerald-500">Active tasks</p>
          </div>
        </Card>

        <Card className="bg-gray-900 border-gray-800">
          <div className="p-6">
            <h3 className="text-sm font-medium text-gray-400 mb-1">Asana</h3>
            <p className="text-2xl font-bold text-gray-50">17</p>
            <p className="text-sm text-blue-500">In progress</p>
          </div>
        </Card>

        <Card className="bg-gray-900 border-gray-800">
          <div className="p-6">
            <h3 className="text-sm font-medium text-gray-400 mb-1">Notion</h3>
            <p className="text-2xl font-bold text-gray-50">8</p>
            <p className="text-sm text-purple-500">CEO tasks</p>
          </div>
        </Card>

        <Card className="bg-gray-900 border-gray-800">
          <div className="p-6">
            <h3 className="text-sm font-medium text-gray-400 mb-1">Slack</h3>
            <p className="text-2xl font-bold text-gray-50">142</p>
            <p className="text-sm text-amber-500">Threads tracked</p>
          </div>
        </Card>
      </div>

      <Card className="bg-gray-900 border-gray-800">
        <div className="p-6">
          <h3 className="text-lg font-semibold text-gray-50 mb-4">Active Projects</h3>
          <div className="space-y-3">
            {[
              { name: 'AI Platform Enhancement', source: 'Linear', status: 'On Track', progress: 65 },
              { name: 'Q1 Sales Campaign', source: 'Asana', status: 'At Risk', progress: 35 },
              { name: 'Infrastructure Migration', source: 'Notion', status: 'On Track', progress: 80 },
              { name: 'Customer Onboarding', source: 'Asana', status: 'Completed', progress: 100 },
            ].map((project) => (
              <div key={project.name} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div>
                    <span className="text-gray-50 font-medium">{project.name}</span>
                    <Badge variant="outline" className="ml-2 text-xs">{project.source}</Badge>
                  </div>
                  <Badge
                    className={`text-xs ${
                      project.status === 'On Track' ? 'bg-emerald-500/20 text-emerald-500' :
                      project.status === 'At Risk' ? 'bg-amber-500/20 text-amber-500' :
                      'bg-blue-500/20 text-blue-500'
                    }`}
                  >
                    {project.status}
                  </Badge>
                </div>
                <div className="w-full bg-gray-800 rounded-full h-2">
                  <div
                    className="bg-purple-600 h-2 rounded-full transition-all"
                    style={{ width: `${project.progress}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>
    </div>
  );
};

// System Status Panel
const SystemStatusPanel: React.FC = () => {
  const mcpServers = [
    { name: 'AI Memory', port: 9001, status: 'healthy', uptime: '99.9%' },
    { name: 'Gong Integration', port: 9002, status: 'healthy', uptime: '99.8%' },
    { name: 'Snowflake', port: 9003, status: 'healthy', uptime: '99.9%' },
    { name: 'Linear', port: 9004, status: 'healthy', uptime: '100%' },
    { name: 'Notion', port: 9005, status: 'healthy', uptime: '99.7%' },
    { name: 'Asana', port: 3006, status: 'degraded', uptime: '95.2%' },
    { name: 'Slack', port: 9007, status: 'healthy', uptime: '99.9%' },
    { name: 'GitHub', port: 3007, status: 'healthy', uptime: '100%' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-50 mb-2">System Status</h2>
        <p className="text-gray-400">Real-time monitoring of all services and integrations</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-gray-900 border-gray-800">
          <div className="p-6">
            <Server className="h-8 w-8 text-emerald-500 mb-3" />
            <h3 className="text-lg font-semibold text-gray-50 mb-1">Overall Health</h3>
            <p className="text-2xl font-bold text-gray-50">98.7%</p>
            <p className="text-sm text-gray-400">System uptime</p>
          </div>
        </Card>

        <Card className="bg-gray-900 border-gray-800">
          <div className="p-6">
            <Database className="h-8 w-8 text-blue-500 mb-3" />
            <h3 className="text-lg font-semibold text-gray-50 mb-1">Memory Usage</h3>
            <p className="text-2xl font-bold text-gray-50">42.3 GB</p>
            <p className="text-sm text-gray-400">of 128 GB</p>
          </div>
        </Card>

        <Card className="bg-gray-900 border-gray-800">
          <div className="p-6">
            <Activity className="h-8 w-8 text-purple-500 mb-3" />
            <h3 className="text-lg font-semibold text-gray-50 mb-1">API Calls</h3>
            <p className="text-2xl font-bold text-gray-50">127K</p>
            <p className="text-sm text-gray-400">Last 24 hours</p>
          </div>
        </Card>
      </div>

      <Card className="bg-gray-900 border-gray-800">
        <div className="p-6">
          <h3 className="text-lg font-semibold text-gray-50 mb-4">MCP Server Status</h3>
          <div className="space-y-2">
            {mcpServers.map((server) => (
              <div key={server.name} className="flex items-center justify-between p-3 bg-gray-800 rounded-lg">
                <div className="flex items-center gap-3">
                  {server.status === 'healthy' ? (
                    <CheckCircle className="h-5 w-5 text-emerald-500" />
                  ) : (
                    <AlertCircle className="h-5 w-5 text-amber-500" />
                  )}
                  <div>
                    <span className="text-gray-50 font-medium">{server.name}</span>
                    <span className="text-gray-400 text-sm ml-2">Port {server.port}</span>
                  </div>
                </div>
                <div className="text-right">
                  <Badge
                    className={`text-xs ${
                      server.status === 'healthy'
                        ? 'bg-emerald-500/20 text-emerald-500 border-emerald-500/30'
                        : 'bg-amber-500/20 text-amber-500 border-amber-500/30'
                    }`}
                  >
                    {server.status}
                  </Badge>
                  <p className="text-xs text-gray-400 mt-1">{server.uptime} uptime</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>
    </div>
  );
};

// Company OKRs Panel
const CompanyOKRsPanel: React.FC = () => {
  const okrs = [
    {
      objective: 'Achieve Product-Market Fit for AI Platform',
      keyResults: [
        { name: 'Reach 100 active users', current: 87, target: 100 },
        { name: 'Achieve 95% user satisfaction', current: 92, target: 95 },
        { name: 'Generate $1M ARR', current: 750000, target: 1000000 },
      ]
    },
    {
      objective: 'Build World-Class Engineering Team',
      keyResults: [
        { name: 'Hire 5 senior engineers', current: 3, target: 5 },
        { name: 'Implement CI/CD pipeline', current: 100, target: 100 },
        { name: 'Achieve 90% code coverage', current: 82, target: 90 },
      ]
    },
    {
      objective: 'Establish Market Leadership',
      keyResults: [
        { name: 'Launch in 3 new markets', current: 2, target: 3 },
        { name: 'Secure 10 enterprise clients', current: 7, target: 10 },
        { name: 'Achieve 50% market share', current: 35, target: 50 },
      ]
    }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-50 mb-2">Company OKRs</h2>
        <p className="text-gray-400">Q1 2025 Objectives and Key Results</p>
      </div>

      <div className="space-y-6">
        {okrs.map((okr, idx) => (
          <Card key={idx} className="bg-gray-900 border-gray-800">
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-50 mb-4">{okr.objective}</h3>
              <div className="space-y-4">
                {okr.keyResults.map((kr, krIdx) => {
                  const progress = (kr.current / kr.target) * 100;
                  return (
                    <div key={krIdx} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-300">{kr.name}</span>
                        <span className="text-sm text-gray-400">
                          {typeof kr.current === 'number' && kr.current > 1000
                            ? `$${(kr.current / 1000000).toFixed(2)}M / $${(kr.target / 1000000).toFixed(0)}M`
                            : `${kr.current} / ${kr.target}`
                          }
                        </span>
                      </div>
                      <div className="w-full bg-gray-800 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full transition-all ${
                            progress >= 100 ? 'bg-emerald-500' :
                            progress >= 70 ? 'bg-blue-500' :
                            progress >= 40 ? 'bg-amber-500' :
                            'bg-red-500'
                          }`}
                          style={{ width: `${Math.min(progress, 100)}%` }}
                        />
                      </div>
                      <div className="text-right">
                        <span className={`text-xs ${
                          progress >= 100 ? 'text-emerald-500' :
                          progress >= 70 ? 'text-blue-500' :
                          progress >= 40 ? 'text-amber-500' :
                          'text-red-500'
                        }`}>
                          {progress.toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default UnifiedChatInterface;

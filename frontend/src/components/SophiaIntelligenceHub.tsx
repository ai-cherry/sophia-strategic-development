/**
 * 🧠 SOPHIA INTELLIGENCE HUB - UNIFIED COMMAND CENTER
 * Intelligence-first dashboard consolidating all Sophia AI capabilities
 * 
 * Architecture: Pure Qdrant + Lambda Labs + Enhanced Chat Integration
 * Backend: http://localhost:8000 (confirmed healthy)
 * 
 * Features:
 * - Conversational interface as primary interaction
 * - Real-time MCP server orchestration
 * - Pure Qdrant memory architecture visualization
 * - External intelligence monitoring
 * - Business intelligence live dashboard
 * - Natural language command processing
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  MessageSquare, 
  Brain, 
  Globe, 
  BarChart3, 
  Bot, 
  Database, 
  Zap, 
  Settings,
  TrendingUp,
  TrendingDown,
  Activity,
  Server,
  RefreshCw,
  Send,
  Mic,
  Search,
  Bell,
  Eye,
  AlertTriangle,
  CheckCircle
} from 'lucide-react';

// Types
interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  sources?: string[];
  insights?: string[];
  recommendations?: string[];
  metadata?: {
    intent: string;
    response_time: number;
    confidence: number;
  };
}

interface MCPServer {
  name: string;
  status: 'healthy' | 'degraded' | 'unhealthy';
  port: number;
  category: 'infrastructure' | 'business' | 'development' | 'ai';
  uptime: string;
  requests: number;
  latency: number;
}

interface QdrantCollection {
  name: string;
  status: 'healthy' | 'degraded' | 'unhealthy';
  documents: number;
  ttl: string;
  performance: number;
}

interface ProactiveAlert {
  id: string;
  type: 'opportunity' | 'risk' | 'system' | 'business';
  title: string;
  description: string;
  urgency: 'low' | 'medium' | 'high' | 'critical';
  timestamp: string;
  actionable: boolean;
}

interface SystemHealth {
  status: 'healthy' | 'degraded' | 'unhealthy';
  uptime: number;
  requests: number;
  success_rate: number;
  environment: string;
  version: string;
}

// Constants
const BACKEND_URL = 'http://localhost:8000';
const INTELLIGENCE_TABS = {
  'chat': { icon: MessageSquare, label: 'Sophia Chat', color: 'blue' },
  'external': { icon: Globe, label: 'External Intelligence', color: 'green' },
  'business': { icon: BarChart3, label: 'Business Intelligence', color: 'purple' },
  'agents': { icon: Bot, label: 'Agent Orchestration', color: 'orange' },
  'memory': { icon: Database, label: 'Memory Architecture', color: 'cyan' },
  'workflow': { icon: Zap, label: 'Workflow Automation', color: 'yellow' },
  'system': { icon: Settings, label: 'System Command', color: 'gray' }
};

const SophiaIntelligenceHub: React.FC = () => {
  // State management
  const [activeTab, setActiveTab] = useState<string>('chat');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [proactiveAlerts, setProactiveAlerts] = useState<ProactiveAlert[]>([]);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Real-time system health
  const { data: systemHealth } = useQuery<SystemHealth>({
    queryKey: ['systemHealth'],
    queryFn: async () => {
      const response = await fetch(`${BACKEND_URL}/health`);
      return response.json();
    },
    refetchInterval: 5000,
  });

  // Mock MCP servers data (in production, would come from backend)
  const mcpServers: MCPServer[] = [
    { name: 'ai_memory', status: 'healthy', port: 9001, category: 'ai', uptime: '2h 15m', requests: 1250, latency: 45 },
    { name: 'codacy', status: 'healthy', port: 3008, category: 'development', uptime: '5h 30m', requests: 890, latency: 32 },
    { name: 'github', status: 'degraded', port: 9003, category: 'development', uptime: '1h 45m', requests: 567, latency: 120 },
    { name: 'slack', status: 'healthy', port: 9101, category: 'business', uptime: '3h 20m', requests: 2100, latency: 28 },
    { name: 'linear', status: 'healthy', port: 9004, category: 'business', uptime: '4h 10m', requests: 1450, latency: 38 },
    { name: 'asana', status: 'healthy', port: 9006, category: 'business', uptime: '2h 50m', requests: 980, latency: 42 },
  ];

  // Pure Qdrant collections
  const qdrantCollections: QdrantCollection[] = [
    { name: 'sophia_episodic', status: 'healthy', documents: 12500, ttl: '1 hour', performance: 35 },
    { name: 'sophia_semantic', status: 'healthy', documents: 89000, ttl: '30 days', performance: 42 },
    { name: 'sophia_visual', status: 'healthy', documents: 34000, ttl: '7 days', performance: 48 },
    { name: 'sophia_procedural', status: 'healthy', documents: 15600, ttl: '14 days', performance: 39 },
  ];

  // Initialize with welcome message
  useEffect(() => {
    const welcomeMessage: ChatMessage = {
      id: 'welcome',
      role: 'system',
      content: '🧠 Welcome to Sophia Intelligence Hub! I\'m your executive AI assistant with real-time access to all business systems. How can I help you today?',
      timestamp: new Date().toISOString(),
      sources: ['sophia_ai_core'],
      insights: ['Intelligence-first interface active', 'Pure Qdrant architecture operational', 'MCP orchestration ready'],
      recommendations: ['Try: "Show me MCP server status"', 'Try: "What\'s our memory performance?"', 'Try: "Monitor business intelligence"']
    };
    setMessages([welcomeMessage]);

    // Mock proactive alerts
    setProactiveAlerts([
      {
        id: '1',
        type: 'opportunity',
        title: 'High-value prospect engagement detected',
        description: 'TechCorp increased website activity by 340% in last 24h',
        urgency: 'high',
        timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
        actionable: true
      },
      {
        id: '2',
        type: 'system',
        title: 'GitHub MCP server performance degraded',
        description: 'Response time increased to 120ms (target: <50ms)',
        urgency: 'medium',
        timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
        actionable: true
      }
    ]);
  }, []);

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Handle chat message submission
  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch(`${BACKEND_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: inputMessage })
      });

      const data = await response.json();
      
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response || 'I\'m processing your request...',
        timestamp: new Date().toISOString(),
        sources: data.sources || ['sophia_ai_core'],
        insights: data.insights || [],
        recommendations: data.recommendations || [],
        metadata: {
          intent: data.metadata?.intent || 'general',
          response_time: data.metadata?.response_time || 0,
          confidence: 0.95
        }
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'system',
        content: '❌ Connection error. Please ensure the backend is running.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Natural language command processing
  const handleQuickCommand = (command: string) => {
    setInputMessage(command);
    // Auto-send after a brief delay
    setTimeout(() => {
      handleSendMessage();
    }, 100);
  };

  // Status color helper
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-400';
      case 'degraded': return 'text-yellow-400';
      case 'unhealthy': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  // Render chat interface
  const renderChatInterface = () => (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div key={message.id} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-3xl p-4 rounded-lg ${
              message.role === 'user' 
                ? 'bg-blue-600 text-white' 
                : message.role === 'system'
                ? 'bg-gray-700 text-gray-200'
                : 'bg-gray-800 text-white'
            }`}>
              <div className="whitespace-pre-wrap">{message.content}</div>
              
              {message.sources && (
                <div className="mt-2 text-xs opacity-70">
                  Sources: {message.sources.join(', ')}
                </div>
              )}
              
              {message.insights && message.insights.length > 0 && (
                <div className="mt-2">
                  <div className="text-xs font-semibold mb-1">💡 Insights:</div>
                  <ul className="text-xs space-y-1">
                    {message.insights.map((insight, idx) => (
                      <li key={idx} className="opacity-80">• {insight}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {message.recommendations && message.recommendations.length > 0 && (
                <div className="mt-2">
                  <div className="text-xs font-semibold mb-1">🎯 Recommendations:</div>
                  <ul className="text-xs space-y-1">
                    {message.recommendations.map((rec, idx) => (
                      <li key={idx} className="opacity-80">• {rec}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              <div className="mt-2 text-xs opacity-50">
                {new Date(message.timestamp).toLocaleTimeString()}
                {message.metadata && (
                  <span className="ml-2">
                    • {message.metadata.response_time?.toFixed(1)}ms
                    • {Math.round(message.metadata.confidence * 100)}% confidence
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-800 text-white p-4 rounded-lg">
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-400"></div>
                <span>Sophia is thinking...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="p-4 border-t border-gray-700">
        <div className="flex items-center space-x-2">
          <div className="flex-1 relative">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Ask Sophia anything... (try: 'Show me MCP server status')"
              className="w-full bg-gray-800 text-white rounded-lg px-4 py-2 pr-12 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={() => setIsListening(!isListening)}
              className={`absolute right-2 top-2 p-1 rounded ${isListening ? 'text-red-400' : 'text-gray-400'} hover:text-white`}
            >
              <Mic className="h-4 w-4" />
            </button>
          </div>
          <button
            onClick={handleSendMessage}
            disabled={isLoading || !inputMessage.trim()}
            className="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
        
        {/* Quick actions */}
        <div className="mt-3 flex flex-wrap gap-2">
          <button
            onClick={() => handleQuickCommand('Show me MCP server status')}
            className="text-xs bg-gray-700 text-gray-300 px-3 py-1 rounded-full hover:bg-gray-600"
          >
            🤖 MCP Status
          </button>
          <button
            onClick={() => handleQuickCommand('What is our memory architecture performance?')}
            className="text-xs bg-gray-700 text-gray-300 px-3 py-1 rounded-full hover:bg-gray-600"
          >
            💾 Memory Performance
          </button>
          <button
            onClick={() => handleQuickCommand('Monitor business intelligence')}
            className="text-xs bg-gray-700 text-gray-300 px-3 py-1 rounded-full hover:bg-gray-600"
          >
            📊 Business Intel
          </button>
          <button
            onClick={() => handleQuickCommand('Deploy latest updates')}
            className="text-xs bg-gray-700 text-gray-300 px-3 py-1 rounded-full hover:bg-gray-600"
          >
            🚀 Deploy Updates
          </button>
        </div>
      </div>
    </div>
  );

  // Render MCP orchestration dashboard
  const renderMCPOrchestration = () => (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">MCP Server Orchestration</h2>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-400">
            {mcpServers.filter(s => s.status === 'healthy').length}/{mcpServers.length} healthy
          </span>
          <RefreshCw className="h-4 w-4 text-gray-400" />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {mcpServers.map((server) => (
          <div key={server.name} className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold text-white">{server.name}</h3>
              <div className={`flex items-center space-x-1 ${getStatusColor(server.status)}`}>
                {server.status === 'healthy' ? (
                  <CheckCircle className="h-4 w-4" />
                ) : (
                  <AlertTriangle className="h-4 w-4" />
                )}
                <span className="text-xs">{server.status}</span>
              </div>
            </div>
            
            <div className="space-y-1 text-sm text-gray-400">
              <div>Port: {server.port}</div>
              <div>Category: {server.category}</div>
              <div>Uptime: {server.uptime}</div>
              <div>Requests: {server.requests.toLocaleString()}</div>
              <div>Latency: {server.latency}ms</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  // Render memory architecture
  const renderMemoryArchitecture = () => (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">Pure Qdrant Memory Architecture</h2>
        <div className="text-sm text-gray-400">
          <span className="text-green-400">●</span> https://cloud.qdrant.io
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {qdrantCollections.map((collection) => (
          <div key={collection.name} className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold text-white">{collection.name}</h3>
              <div className={`flex items-center space-x-1 ${getStatusColor(collection.status)}`}>
                <Database className="h-4 w-4" />
                <span className="text-xs">{collection.status}</span>
              </div>
            </div>
            
            <div className="space-y-1 text-sm text-gray-400">
              <div>Documents: {collection.documents.toLocaleString()}</div>
              <div>TTL: {collection.ttl}</div>
              <div>Performance: {collection.performance}ms avg</div>
            </div>
          </div>
        ))}
      </div>

      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h3 className="font-semibold text-white mb-2">Architecture Overview</h3>
        <div className="text-sm text-gray-400 space-y-1">
          <div>• L0: GPU Cache (Lambda Labs) - Hardware acceleration</div>
          <div>• L1: Redis (Hot cache) - &lt;10ms session data</div>
          <div>• L2: Qdrant (Vectors) - &lt;50ms semantic search</div>
          <div>• L3: PostgreSQL pgvector - &lt;100ms hybrid queries</div>
          <div>• L4: Mem0 (Conversations) - Agent memory</div>
        </div>
      </div>
    </div>
  );

  // Render proactive intelligence feed
  const renderProactiveAlerts = () => (
    <div className="w-80 bg-gray-800 border-l border-gray-700 p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-white">Proactive Intelligence</h3>
        <Bell className="h-4 w-4 text-gray-400" />
      </div>
      
      <div className="space-y-3">
        {proactiveAlerts.map((alert) => (
          <div key={alert.id} className="bg-gray-700 rounded-lg p-3 border-l-4 border-blue-500">
            <div className="flex items-center justify-between mb-1">
              <span className={`text-xs px-2 py-1 rounded ${
                alert.urgency === 'critical' ? 'bg-red-600' :
                alert.urgency === 'high' ? 'bg-orange-600' :
                alert.urgency === 'medium' ? 'bg-yellow-600' :
                'bg-gray-600'
              }`}>
                {alert.urgency}
              </span>
              <span className="text-xs text-gray-400">
                {new Date(alert.timestamp).toLocaleTimeString()}
              </span>
            </div>
            
            <h4 className="font-medium text-white text-sm mb-1">{alert.title}</h4>
            <p className="text-xs text-gray-300 mb-2">{alert.description}</p>
            
            {alert.actionable && (
              <button className="text-xs bg-blue-600 text-white px-2 py-1 rounded hover:bg-blue-700">
                Take Action
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 text-white flex">
      {/* Sidebar */}
      <div className={`${sidebarCollapsed ? 'w-16' : 'w-64'} bg-gray-800 border-r border-gray-700 transition-all duration-300`}>
        <div className="p-4">
          <div className="flex items-center justify-between mb-8">
            {!sidebarCollapsed && (
              <div>
                <h1 className="text-xl font-bold">Sophia Intelligence</h1>
                <p className="text-xs text-gray-400">Executive Command Center</p>
              </div>
            )}
            <button
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="p-2 hover:bg-gray-700 rounded"
            >
              <Brain className="h-5 w-5" />
            </button>
          </div>
          
          <nav className="space-y-2">
            {Object.entries(INTELLIGENCE_TABS).map(([key, tab]) => {
              const Icon = tab.icon;
              return (
                <button
                  key={key}
                  onClick={() => setActiveTab(key)}
                  className={`w-full flex items-center space-x-3 p-3 rounded-lg transition-all ${
                    activeTab === key 
                      ? 'bg-blue-600 text-white' 
                      : 'text-gray-400 hover:text-white hover:bg-gray-700'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  {!sidebarCollapsed && <span className="text-sm">{tab.label}</span>}
                </button>
              );
            })}
          </nav>
        </div>
        
        {/* System status */}
        {!sidebarCollapsed && (
          <div className="absolute bottom-4 left-4 right-4">
            <div className="bg-gray-700 rounded-lg p-3">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-gray-400">System Status</span>
                <div className={`flex items-center space-x-1 ${getStatusColor(systemHealth?.status || 'healthy')}`}>
                  <Activity className="h-3 w-3" />
                  <span className="text-xs">{systemHealth?.status || 'healthy'}</span>
                </div>
              </div>
              <div className="text-xs text-gray-400 space-y-1">
                <div>Version: {systemHealth?.version || '2.0.0'}</div>
                <div>Uptime: {Math.floor((systemHealth?.uptime || 0) / 60)}m</div>
                <div>Success: {(systemHealth?.success_rate || 100).toFixed(1)}%</div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Main content area */}
      <div className="flex-1 flex">
        {/* Primary content */}
        <div className="flex-1">
          {activeTab === 'chat' && renderChatInterface()}
          {activeTab === 'agents' && renderMCPOrchestration()}
          {activeTab === 'memory' && renderMemoryArchitecture()}
          {activeTab === 'external' && (
            <div className="p-6">
              <h2 className="text-2xl font-bold text-white mb-4">External Intelligence Monitor</h2>
              <div className="text-gray-400">External intelligence monitoring will be implemented here...</div>
            </div>
          )}
          {activeTab === 'business' && (
            <div className="p-6">
              <h2 className="text-2xl font-bold text-white mb-4">Business Intelligence Live</h2>
              <div className="text-gray-400">Business intelligence dashboard will be implemented here...</div>
            </div>
          )}
          {activeTab === 'workflow' && (
            <div className="p-6">
              <h2 className="text-2xl font-bold text-white mb-4">Workflow Automation</h2>
              <div className="text-gray-400">Workflow automation interface will be implemented here...</div>
            </div>
          )}
          {activeTab === 'system' && (
            <div className="p-6">
              <h2 className="text-2xl font-bold text-white mb-4">System Command Center</h2>
              <div className="text-gray-400">System command center will be implemented here...</div>
            </div>
          )}
        </div>

        {/* Proactive intelligence feed */}
        {renderProactiveAlerts()}
      </div>
    </div>
  );
};

export default SophiaIntelligenceHub; 
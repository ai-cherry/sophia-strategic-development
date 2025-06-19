"""
Frontend React Component for AG-UI Real-time Interface
Provides real-time streaming, multi-modal interaction, and workflow visualization
"""

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  MessageCircle, 
  Zap, 
  Brain, 
  Database, 
  FileText, 
  Activity,
  Send,
  Mic,
  MicOff,
  Image,
  Video,
  Settings,
  BarChart3
} from 'lucide-react';

// Types
interface AGUIEvent {
  type: string;
  payload: any;
  session_id: string;
  timestamp: number;
  event_id: string;
}

interface WorkflowStep {
  step: string;
  description: string;
  progress: number;
  timestamp: number;
}

interface Message {
  id: string;
  type: 'user' | 'agent' | 'system';
  content: string;
  timestamp: number;
  confidence?: number;
  routing_info?: any;
  workflow_id?: string;
}

interface SystemStats {
  performance_summary: {
    total_queries: number;
    success_rate: number;
    avg_routing_time_ms: number;
    avg_agno_instantiation_us: number;
    active_agui_sessions: number;
    mcp_federation_health: number;
  };
  system_overview: {
    status: string;
    components: Record<string, string>;
  };
}

// Custom hooks
const useWebSocket = (sessionId: string | null) => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected');
  const [events, setEvents] = useState<AGUIEvent[]>([]);

  useEffect(() => {
    if (!sessionId) return;

    const wsUrl = `ws://localhost:8000/api/v1/hybrid-rag/sessions/${sessionId}/ws`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      setConnectionStatus('connected');
      setSocket(ws);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setEvents(prev => [...prev, data]);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onclose = () => {
      setConnectionStatus('disconnected');
      setSocket(null);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnectionStatus('disconnected');
    };

    setConnectionStatus('connecting');

    return () => {
      ws.close();
    };
  }, [sessionId]);

  const sendEvent = useCallback((eventType: string, payload: any) => {
    if (socket && connectionStatus === 'connected') {
      const event = {
        type: eventType,
        payload,
        session_id: sessionId,
        timestamp: Date.now(),
        event_id: Math.random().toString(36).substr(2, 9)
      };
      socket.send(JSON.stringify(event));
    }
  }, [socket, connectionStatus, sessionId]);

  return { connectionStatus, events, sendEvent };
};

const useSystemStats = () => {
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchStats = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/hybrid-rag/stats');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch system stats:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 10000); // Update every 10 seconds
    return () => clearInterval(interval);
  }, [fetchStats]);

  return { stats, loading, refetch: fetchStats };
};

// Components
const ConnectionStatus: React.FC<{ status: string }> = ({ status }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected': return 'bg-green-500';
      case 'connecting': return 'bg-yellow-500';
      case 'disconnected': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="flex items-center gap-2">
      <div className={`w-2 h-2 rounded-full ${getStatusColor(status)}`} />
      <span className="text-sm capitalize">{status}</span>
    </div>
  );
};

const WorkflowProgress: React.FC<{ workflow: any }> = ({ workflow }) => {
  if (!workflow) return null;

  return (
    <Card className="mb-4">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm flex items-center gap-2">
          <Activity className="w-4 h-4" />
          Workflow: {workflow.type}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Progress value={workflow.progress * 100} className="mb-2" />
        <div className="text-xs text-gray-600">
          {workflow.current_step?.description || 'Processing...'}
        </div>
      </CardContent>
    </Card>
  );
};

const MessageBubble: React.FC<{ message: Message }> = ({ message }) => {
  const isUser = message.type === 'user';
  const isSystem = message.type === 'system';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[80%] rounded-lg p-3 ${
        isUser 
          ? 'bg-blue-500 text-white' 
          : isSystem 
            ? 'bg-gray-100 text-gray-800 border'
            : 'bg-white border shadow-sm'
      }`}>
        <div className="text-sm">{message.content}</div>
        {message.confidence && (
          <div className="text-xs mt-1 opacity-70">
            Confidence: {(message.confidence * 100).toFixed(1)}%
          </div>
        )}
        {message.routing_info && (
          <div className="text-xs mt-1 opacity-70">
            Engine: {message.routing_info.decision?.primary_engine}
          </div>
        )}
        <div className="text-xs mt-1 opacity-50">
          {new Date(message.timestamp).toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
};

const SystemStatsPanel: React.FC<{ stats: SystemStats | null; loading: boolean }> = ({ stats, loading }) => {
  if (loading) {
    return <div className="text-center py-4">Loading stats...</div>;
  }

  if (!stats) {
    return <div className="text-center py-4 text-gray-500">No stats available</div>;
  }

  const { performance_summary, system_overview } = stats;

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-sm flex items-center gap-2">
            <BarChart3 className="w-4 h-4" />
            System Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-xs text-gray-500">Status</div>
              <Badge variant={system_overview.status === 'operational' ? 'default' : 'destructive'}>
                {system_overview.status}
              </Badge>
            </div>
            <div>
              <div className="text-xs text-gray-500">Active Sessions</div>
              <div className="font-semibold">{performance_summary.active_agui_sessions}</div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Performance Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-xs text-gray-500">Total Queries</span>
              <span className="font-semibold">{performance_summary.total_queries.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-xs text-gray-500">Success Rate</span>
              <span className="font-semibold">{(performance_summary.success_rate * 100).toFixed(1)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-xs text-gray-500">Avg Routing Time</span>
              <span className="font-semibold">{performance_summary.avg_routing_time_ms.toFixed(1)}ms</span>
            </div>
            <div className="flex justify-between">
              <span className="text-xs text-gray-500">Agno Instantiation</span>
              <span className="font-semibold">{performance_summary.avg_agno_instantiation_us.toFixed(1)}μs</span>
            </div>
            <div className="flex justify-between">
              <span className="text-xs text-gray-500">MCP Health</span>
              <span className="font-semibold">{(performance_summary.mcp_federation_health * 100).toFixed(1)}%</span>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Components</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {Object.entries(system_overview.components).map(([component, status]) => (
              <div key={component} className="flex justify-between items-center">
                <span className="text-xs text-gray-500">{component.replace(/_/g, ' ')}</span>
                <Badge variant={status === 'initialized' || status === 'operational' ? 'default' : 'destructive'} className="text-xs">
                  {status}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Main component
const HybridRAGInterface: React.FC = () => {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [activeWorkflow, setActiveWorkflow] = useState<any>(null);
  const [activeTab, setActiveTab] = useState('chat');
  
  const { connectionStatus, events, sendEvent } = useWebSocket(sessionId);
  const { stats, loading: statsLoading, refetch: refetchStats } = useSystemStats();
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize session
  useEffect(() => {
    const initSession = async () => {
      try {
        const response = await fetch('/api/v1/hybrid-rag/sessions', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: 'demo_user', context: {} })
        });
        const data = await response.json();
        setSessionId(data.session_id);
      } catch (error) {
        console.error('Failed to create session:', error);
      }
    };

    initSession();
  }, []);

  // Process incoming events
  useEffect(() => {
    events.forEach(event => {
      switch (event.type) {
        case 'agent_message':
          setMessages(prev => [...prev, {
            id: event.event_id,
            type: 'agent',
            content: event.payload.message,
            timestamp: event.timestamp,
            confidence: event.payload.confidence,
            routing_info: event.payload.routing_info,
            workflow_id: event.payload.workflow_id
          }]);
          break;
        
        case 'workflow_start':
          setActiveWorkflow({
            id: event.payload.workflow_id,
            type: event.payload.type,
            progress: 0,
            current_step: null
          });
          break;
        
        case 'workflow_progress':
          setActiveWorkflow(prev => prev?.id === event.payload.workflow_id ? {
            ...prev,
            progress: event.payload.progress,
            current_step: event.payload.current_step
          } : prev);
          break;
        
        case 'workflow_complete':
          setActiveWorkflow(null);
          break;
        
        case 'error':
          setMessages(prev => [...prev, {
            id: event.event_id,
            type: 'system',
            content: `Error: ${event.payload.error}`,
            timestamp: event.timestamp
          }]);
          break;
      }
    });
  }, [events]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = useCallback(async () => {
    if (!inputValue.trim() || !sessionId) return;

    const userMessage: Message = {
      id: Math.random().toString(36).substr(2, 9),
      type: 'user',
      content: inputValue,
      timestamp: Date.now()
    };

    setMessages(prev => [...prev, userMessage]);
    
    // Send via WebSocket
    sendEvent('user_message', {
      message: inputValue,
      context: {}
    });

    setInputValue('');
  }, [inputValue, sessionId, sendEvent]);

  const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  }, [handleSendMessage]);

  const toggleRecording = useCallback(() => {
    setIsRecording(prev => !prev);
    // TODO: Implement voice recording
  }, []);

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-semibold flex items-center gap-2">
              <Brain className="w-6 h-6 text-blue-500" />
              Sophia AI - Hybrid RAG
            </h1>
            <ConnectionStatus status={connectionStatus} />
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={refetchStats}>
              <Activity className="w-4 h-4 mr-1" />
              Refresh Stats
            </Button>
            <Button variant="outline" size="sm">
              <Settings className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex">
        {/* Chat Area */}
        <div className="flex-1 flex flex-col">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
            <TabsList className="mx-6 mt-4 w-fit">
              <TabsTrigger value="chat" className="flex items-center gap-2">
                <MessageCircle className="w-4 h-4" />
                Chat
              </TabsTrigger>
              <TabsTrigger value="workflow" className="flex items-center gap-2">
                <Activity className="w-4 h-4" />
                Workflows
              </TabsTrigger>
            </TabsList>

            <TabsContent value="chat" className="flex-1 flex flex-col mt-4">
              {/* Workflow Progress */}
              {activeWorkflow && (
                <div className="mx-6">
                  <WorkflowProgress workflow={activeWorkflow} />
                </div>
              )}

              {/* Messages */}
              <div className="flex-1 overflow-y-auto px-6 pb-4">
                {messages.length === 0 ? (
                  <div className="text-center py-12 text-gray-500">
                    <Brain className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                    <h3 className="text-lg font-medium mb-2">Welcome to Sophia AI</h3>
                    <p>Start a conversation to experience hybrid RAG intelligence</p>
                    <div className="flex justify-center gap-2 mt-4">
                      <Badge variant="outline" className="flex items-center gap-1">
                        <Zap className="w-3 h-3" />
                        Ultra-fast Agno
                      </Badge>
                      <Badge variant="outline" className="flex items-center gap-1">
                        <Database className="w-3 h-3" />
                        MCP Federation
                      </Badge>
                      <Badge variant="outline" className="flex items-center gap-1">
                        <FileText className="w-3 h-3" />
                        LlamaIndex
                      </Badge>
                    </div>
                  </div>
                ) : (
                  messages.map(message => (
                    <MessageBubble key={message.id} message={message} />
                  ))
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div className="border-t bg-white px-6 py-4">
                <div className="flex items-center gap-2">
                  <div className="flex-1 relative">
                    <Input
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Ask anything about your data..."
                      className="pr-24"
                    />
                    <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={toggleRecording}
                        className={isRecording ? 'text-red-500' : ''}
                      >
                        {isRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                      </Button>
                      <Button variant="ghost" size="sm">
                        <Image className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                  <Button onClick={handleSendMessage} disabled={!inputValue.trim()}>
                    <Send className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="workflow" className="flex-1 p-6">
              <div className="text-center py-12 text-gray-500">
                <Activity className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <h3 className="text-lg font-medium mb-2">Workflow Management</h3>
                <p>Advanced workflow orchestration coming soon</p>
              </div>
            </TabsContent>
          </Tabs>
        </div>

        {/* Stats Sidebar */}
        <div className="w-80 border-l bg-white p-6">
          <h2 className="text-lg font-semibold mb-4">System Stats</h2>
          <SystemStatsPanel stats={stats} loading={statsLoading} />
        </div>
      </div>
    </div>
  );
};

export default HybridRAGInterface;


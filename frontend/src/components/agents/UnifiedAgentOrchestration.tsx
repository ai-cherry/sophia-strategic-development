/**
 * 🤖 UNIFIED AGENT ORCHESTRATION COMPONENT
 * 
 * Combines MCP server orchestration with autonomous agent monitoring
 * Extracted from AgentDashboard.tsx and integrated into SophiaExecutiveDashboard
 * 
 * Features:
 * - Real-time agent status monitoring
 * - Action history with timeline view
 * - Control panel for agent management
 * - Analytics and ROI calculations
 * - Emergency stop capabilities
 * - MCP server status monitoring
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import {
  Bot,
  Activity,
  Clock,
  DollarSign,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Play,
  Pause,
  RotateCcw,
  Settings,
  TrendingUp,
  TrendingDown,
  Shield,
  Zap,
  Server,
  Database,
  Cpu,
  BarChart3,
  Filter,
  Download,
  RefreshCw,
  Power,
  History,
  Target,
  Award,
  GitBranch,
  Eye,
  Brain,
  Users,
  MessageSquare,
  ChevronDown,
  ChevronRight
} from 'lucide-react';

// Import unified environment configuration
import { getBaseURL, getWebSocketURL } from '../../config/environment';

// Types
interface Agent {
  id: string;
  name: string;
  type: 'infrastructure' | 'monitoring' | 'optimization' | 'integration';
  status: 'running' | 'paused' | 'stopped' | 'error';
  health: 'healthy' | 'degraded' | 'unhealthy';
  description: string;
  version: string;
  uptime: number;
  lastActivity: string;
  metrics: {
    actionsToday: number;
    successRate: number;
    avgResponseTime: number;
    resourceUsage: {
      cpu: number;
      memory: number;
      gpu?: number;
    };
  };
  config: {
    autoRestart: boolean;
    maxActionsPerHour: number;
    thresholds: {
      [key: string]: number;
    };
  };
}

interface AgentAction {
  id: string;
  agentId: string;
  agentName: string;
  type: 'automated' | 'manual' | 'scheduled';
  action: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'rolled_back';
  timestamp: string;
  duration?: number;
  impact?: {
    type: 'cost_savings' | 'performance' | 'reliability' | 'security';
    value: number;
    unit: string;
  };
  details?: any;
  canRollback: boolean;
}

interface AgentAnalytics {
  totalAgents: number;
  activeAgents: number;
  totalActions: number;
  successRate: number;
  costSavings: {
    today: number;
    week: number;
    month: number;
    total: number;
  };
  automationROI: {
    timeSaved: number;
    manualInterventionsAvoided: number;
    efficiencyGain: number;
  };
  performanceMetrics: {
    avgResponseTime: number;
    uptime: number;
    reliability: number;
  };
}

interface SystemHealth {
  mcp_servers: {
    [key: string]: {
      status: string;
      port: number;
    };
  };
  metrics: {
    uptime_hours: number;
    success_rate: number;
  };
}

interface UnifiedAgentOrchestrationProps {
  systemHealth?: SystemHealth;
  onTabChange?: (tab: string) => void;
}

const BACKEND_URL = getBaseURL();

const AGENT_TYPES = {
  infrastructure: { icon: Server, color: 'blue' },
  monitoring: { icon: Eye, color: 'green' },
  optimization: { icon: Zap, color: 'yellow' },
  integration: { icon: GitBranch, color: 'purple' }
};

const ACTION_STATUS_COLORS = {
  pending: 'gray',
  running: 'blue',
  completed: 'green',
  failed: 'red',
  rolled_back: 'orange'
};

const UnifiedAgentOrchestration: React.FC<UnifiedAgentOrchestrationProps> = ({ 
  systemHealth,
  onTabChange 
}) => {
  // State management
  const [viewMode, setViewMode] = useState<'overview' | 'agents' | 'mcp' | 'analytics'>('overview');
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [timeRange, setTimeRange] = useState<'1h' | '24h' | '7d' | '30d'>('24h');
  const [showEmergencyStop, setShowEmergencyStop] = useState(false);
  const [expandedAgents, setExpandedAgents] = useState<Set<string>>(new Set());
  const queryClient = useQueryClient();
  const wsRef = useRef<WebSocket | null>(null);

  // Fetch agents data
  const { data: agents, isLoading: agentsLoading } = useQuery<Agent[]>({
    queryKey: ['agents', 'status'],
    queryFn: async () => {
      const response = await fetch(`${BACKEND_URL}/api/agents/status`);
      if (!response.ok) throw new Error('Failed to fetch agents');
      return response.json();
    },
    refetchInterval: 5000,
    // Mock data for development
    placeholderData: [
      {
        id: 'lambda-monitor',
        name: 'Lambda Labs Monitor',
        type: 'infrastructure',
        status: 'running',
        health: 'healthy',
        description: 'Monitors Lambda Labs GPU instances and optimizes usage',
        version: '1.0.0',
        uptime: 86400,
        lastActivity: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
        metrics: {
          actionsToday: 24,
          successRate: 98.5,
          avgResponseTime: 120,
          resourceUsage: { cpu: 15, memory: 32, gpu: 78 }
        },
        config: {
          autoRestart: true,
          maxActionsPerHour: 10,
          thresholds: { gpu_utilization: 80, cost_limit: 100 }
        }
      },
      {
        id: 'qdrant-optimizer',
        name: 'Qdrant Optimizer',
        type: 'optimization',
        status: 'running',
        health: 'healthy',
        description: 'Optimizes Qdrant vector database performance and indexing',
        version: '1.0.0',
        uptime: 172800,
        lastActivity: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
        metrics: {
          actionsToday: 18,
          successRate: 99.2,
          avgResponseTime: 85,
          resourceUsage: { cpu: 22, memory: 45 }
        },
        config: {
          autoRestart: true,
          maxActionsPerHour: 20,
          thresholds: { query_latency: 100, index_size: 1000000 }
        }
      },
      {
        id: 'prometheus-exporter',
        name: 'Prometheus Metrics Exporter',
        type: 'monitoring',
        status: 'running',
        health: 'healthy',
        description: 'Exports system metrics to Prometheus for monitoring',
        version: '1.0.0',
        uptime: 259200,
        lastActivity: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
        metrics: {
          actionsToday: 288,
          successRate: 100,
          avgResponseTime: 15,
          resourceUsage: { cpu: 5, memory: 12 }
        },
        config: {
          autoRestart: true,
          maxActionsPerHour: 60,
          thresholds: { metric_lag: 5 }
        }
      }
    ]
  });

  // Fetch action history
  const { data: actions, isLoading: actionsLoading } = useQuery<AgentAction[]>({
    queryKey: ['agents', 'actions', selectedAgent, timeRange],
    queryFn: async () => {
      const url = selectedAgent 
        ? `${BACKEND_URL}/api/agents/${selectedAgent}/actions?range=${timeRange}`
        : `${BACKEND_URL}/api/agents/actions?range=${timeRange}`;
      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to fetch actions');
      return response.json();
    },
    refetchInterval: 10000,
    // Mock data for development
    placeholderData: [
      {
        id: '1',
        agentId: 'lambda-monitor',
        agentName: 'Lambda Labs Monitor',
        type: 'automated',
        action: 'Scaled down idle GPU instance',
        status: 'completed',
        timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
        duration: 45,
        impact: { type: 'cost_savings', value: 12.50, unit: 'USD' },
        details: { instance: 'gpu-instance-1', previousSize: 'A100', newSize: 'A40' },
        canRollback: true
      },
      {
        id: '2',
        agentId: 'qdrant-optimizer',
        agentName: 'Qdrant Optimizer',
        type: 'automated',
        action: 'Optimized vector index for faster queries',
        status: 'completed',
        timestamp: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
        duration: 120,
        impact: { type: 'performance', value: 35, unit: '%' },
        details: { collection: 'embeddings', indexType: 'hnsw', parameters: { ef: 128 } },
        canRollback: true
      },
      {
        id: '3',
        agentId: 'lambda-monitor',
        agentName: 'Lambda Labs Monitor',
        type: 'scheduled',
        action: 'Daily cost report generated',
        status: 'completed',
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        duration: 5,
        impact: { type: 'cost_savings', value: 0, unit: 'USD' },
        canRollback: false
      }
    ]
  });

  // Fetch analytics
  const { data: analytics, isLoading: analyticsLoading } = useQuery<AgentAnalytics>({
    queryKey: ['agents', 'analytics', timeRange],
    queryFn: async () => {
      const response = await fetch(`${BACKEND_URL}/api/agents/analytics?range=${timeRange}`);
      if (!response.ok) throw new Error('Failed to fetch analytics');
      return response.json();
    },
    refetchInterval: 30000,
    // Mock data for development
    placeholderData: {
      totalAgents: 3,
      activeAgents: 3,
      totalActions: 342,
      successRate: 98.8,
      costSavings: {
        today: 87.50,
        week: 612.30,
        month: 2451.20,
        total: 12842.75
      },
      automationROI: {
        timeSaved: 156,
        manualInterventionsAvoided: 89,
        efficiencyGain: 42.5
      },
      performanceMetrics: {
        avgResponseTime: 73.5,
        uptime: 99.8,
        reliability: 98.5
      }
    }
  });

  // Agent control mutations
  const startAgent = useMutation({
    mutationFn: async (agentId: string) => {
      const response = await fetch(`${BACKEND_URL}/api/agents/${agentId}/control`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'start' })
      });
      if (!response.ok) throw new Error('Failed to start agent');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] });
    }
  });

  const stopAgent = useMutation({
    mutationFn: async (agentId: string) => {
      const response = await fetch(`${BACKEND_URL}/api/agents/${agentId}/control`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'stop' })
      });
      if (!response.ok) throw new Error('Failed to stop agent');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] });
    }
  });

  const rollbackAction = useMutation({
    mutationFn: async (actionId: string) => {
      const response = await fetch(`${BACKEND_URL}/api/agents/actions/${actionId}/rollback`, {
        method: 'POST'
      });
      if (!response.ok) throw new Error('Failed to rollback action');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents', 'actions'] });
    }
  });

  // Emergency stop handler
  const handleEmergencyStop = useCallback(async () => {
    if (!window.confirm('⚠️ EMERGENCY STOP\n\nThis will immediately stop ALL autonomous agents.\n\nAre you sure?')) {
      return;
    }

    try {
      const response = await fetch(`${BACKEND_URL}/api/agents/emergency-stop`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirm: true })
      });
      
      if (!response.ok) throw new Error('Emergency stop failed');
      
      queryClient.invalidateQueries({ queryKey: ['agents'] });
      setShowEmergencyStop(false);
    } catch (error) {
      console.error('Emergency stop failed:', error);
      alert('Failed to execute emergency stop! Please check system manually.');
    }
  }, [queryClient]);

  // WebSocket connection for real-time updates
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        const ws = new WebSocket(getWebSocketURL().replace('/ws', '/ws/agents'));
        
        ws.onopen = () => {
          console.log('Agent WebSocket connected');
          wsRef.current = ws;
        };
        
        ws.onmessage = (event) => {
          const data = JSON.parse(event.data);
          
          if (data.type === 'agent_update') {
            queryClient.setQueryData(['agents', 'status'], (oldData: Agent[] | undefined) => {
              if (!oldData) return oldData;
              return oldData.map(agent => 
                agent.id === data.agentId ? { ...agent, ...data.update } : agent
              );
            });
          } else if (data.type === 'new_action') {
            queryClient.invalidateQueries({ queryKey: ['agents', 'actions'] });
            queryClient.invalidateQueries({ queryKey: ['agents', 'analytics'] });
          }
        };
        
        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
        };
        
        ws.onclose = () => {
          console.log('WebSocket disconnected, reconnecting...');
          setTimeout(connectWebSocket, 5000);
        };
        
      } catch (error) {
        console.error('Failed to connect WebSocket:', error);
      }
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [queryClient]);

  // Filter agents
  const filteredAgents = agents?.filter(agent => {
    if (filterType !== 'all' && agent.type !== filterType) return false;
    if (filterStatus !== 'all' && agent.status !== filterStatus) return false;
    return true;
  }) || [];

  // Helper functions
  const renderStatusBadge = (status: Agent['status']) => {
    const colors = {
      running: 'bg-green-500',
      paused: 'bg-yellow-500',
      stopped: 'bg-gray-500',
      error: 'bg-red-500'
    };
    
    return (
      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium text-white ${colors[status]}`}>
        {status}
      </span>
    );
  };

  const renderHealthIndicator = (health: Agent['health']) => {
    const icons = {
      healthy: <CheckCircle className="h-4 w-4 text-green-400" />,
      degraded: <AlertTriangle className="h-4 w-4 text-yellow-400" />,
      unhealthy: <XCircle className="h-4 w-4 text-red-400" />
    };
    
    return icons[health];
  };

  const formatDuration = (seconds: number) => {
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h`;
    return `${Math.floor(seconds / 86400)}d`;
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    
    return date.toLocaleDateString();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': case 'operational': return 'text-green-400';
      case 'degraded': return 'text-yellow-400';
      case 'unhealthy': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  // Chart data
  const costSavingsChartData = {
    labels: ['Today', 'This Week', 'This Month', 'Total'],
    datasets: [{
      label: 'Cost Savings ($)',
      data: analytics ? [
        analytics.costSavings.today,
        analytics.costSavings.week,
        analytics.costSavings.month,
        analytics.costSavings.total
      ] : [],
      backgroundColor: ['#3B82F6', '#10B981', '#F59E0B', '#8B5CF6'],
      borderWidth: 0
    }]
  };

  const performanceChartData = {
    labels: ['Response Time', 'Uptime', 'Reliability'],
    datasets: [{
      label: 'Performance Metrics',
      data: analytics ? [
        analytics.performanceMetrics.avgResponseTime,
        analytics.performanceMetrics.uptime,
        analytics.performanceMetrics.reliability
      ] : [],
      backgroundColor: ['#3B82F6', '#10B981', '#F59E0B'],
      borderWidth: 0
    }]
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Agent & MCP Orchestration</h2>
          <p className="text-gray-400">Unified control center for autonomous agents and MCP servers</p>
        </div>
        
        <div className="flex items-center space-x-4">
          <button
            onClick={() => queryClient.invalidateQueries({ queryKey: ['agents'] })}
            className="flex items-center space-x-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
          >
            <RefreshCw className="h-4 w-4" />
            <span>Refresh</span>
          </button>
          
          <button
            onClick={() => setShowEmergencyStop(true)}
            className="flex items-center space-x-2 px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg transition-colors"
          >
            <Power className="h-4 w-4" />
            <span>Emergency Stop</span>
          </button>
        </div>
      </div>

      {/* View Mode Tabs */}
      <div className="flex space-x-2">
        {['overview', 'agents', 'mcp', 'analytics'].map(mode => (
          <button
            key={mode}
            onClick={() => setViewMode(mode as any)}
            className={`px-4 py-2 rounded-lg transition-colors ${
              viewMode === mode 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            {mode.charAt(0).toUpperCase() + mode.slice(1)}
          </button>
        ))}
      </div>

      {/* Overview View */}
      {viewMode === 'overview' && (
        <>
          {/* Analytics Overview */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-gray-400">Active Agents</h3>
                <Bot className="h-5 w-5 text-blue-400" />
              </div>
              <div className="text-2xl font-bold">{analytics?.activeAgents || 0}/{analytics?.totalAgents || 0}</div>
              <div className="text-sm text-gray-400 mt-1">Running autonomously</div>
            </div>

            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-gray-400">Total Actions</h3>
                <Activity className="h-5 w-5 text-green-400" />
              </div>
              <div className="text-2xl font-bold">{analytics?.totalActions || 0}</div>
              <div className="text-sm text-gray-400 mt-1">{analytics?.successRate || 0}% success rate</div>
            </div>

            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-gray-400">Cost Savings</h3>
                <DollarSign className="h-5 w-5 text-yellow-400" />
              </div>
              <div className="text-2xl font-bold">${analytics?.costSavings.today.toFixed(2) || '0.00'}</div>
              <div className="text-sm text-gray-400 mt-1">Today</div>
            </div>

            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-gray-400">Time Saved</h3>
                <Clock className="h-5 w-5 text-purple-400" />
              </div>
              <div className="text-2xl font-bold">{analytics?.automationROI.timeSaved || 0}h</div>
              <div className="text-sm text-gray-400 mt-1">Manual work avoided</div>
            </div>
          </div>

          {/* Quick Overview Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Agent Status Summary */}
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <h3 className="font-semibold text-white mb-4">Agent Status Summary</h3>
              <div className="space-y-3">
                {filteredAgents.slice(0, 3).map(agent => {
                  const TypeIcon = AGENT_TYPES[agent.type].icon;
                  
                  return (
                    <div key={agent.id} className="flex items-center justify-between p-3 bg-gray-700 rounded">
                      <div className="flex items-center space-x-3">
                        <TypeIcon className={`h-5 w-5 text-${AGENT_TYPES[agent.type].color}-400`} />
                        <div>
                          <div className="font-medium text-white">{agent.name}</div>
                          <div className="text-xs text-gray-400">{agent.metrics.actionsToday} actions today</div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        {renderHealthIndicator(agent.health)}
                        {renderStatusBadge(agent.status)}
                      </div>
                    </div>
                  );
                })}
                
                {filteredAgents.length > 3 && (
                  <button 
                    onClick={() => setViewMode('agents')}
                    className="w-full text-center text-sm text-blue-400 hover:text-blue-300 py-2"
                  >
                    View all {filteredAgents.length} agents →
                  </button>
                )}
              </div>
            </div>

            {/* Recent Actions */}
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-white">Recent Actions</h3>
                <History className="h-4 w-4 text-gray-400" />
              </div>
              
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {actionsLoading ? (
                  <div className="text-center py-4 text-gray-400">Loading actions...</div>
                ) : actions?.length === 0 ? (
                  <div className="text-center py-4 text-gray-400">No actions yet</div>
                ) : (
                  actions?.slice(0, 5).map(action => (
                    <div key={action.id} className="border-l-2 border-gray-600 pl-4 py-2">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="text-sm font-medium text-white">{action.action}</div>
                          <div className="text-xs text-gray-400 mt-1">
                            {action.agentName} • {formatTimestamp(action.timestamp)}
                          </div>
                          {action.impact && (
                            <div className="text-xs text-green-400 mt-1">
                              {action.impact.type === 'cost_savings' && '$'}
                              {action.impact.value}
                              {action.impact.unit}
                              {action.impact.type === 'performance' && ' improvement'}
                            </div>
                          )}
                        </div>
                        
                        <span className={`text-xs px-2 py-1 rounded ${
                          action.status === 'completed' ? 'bg-green-600' :
                          action.status === 'failed' ? 'bg-red-600' :
                          action.status === 'running' ? 'bg-blue-600' :
                          'bg-gray-600'
                        }`}>
                          {action.status}
                        </span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Cost Savings Chart */}
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <h3 className="font-semibold text-white mb-4">Cost Savings Overview</h3>
            <Bar 
              data={costSavingsChartData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: { display: false }
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { color: '#9CA3AF' }
                  },
                  x: {
                    grid: { display: false },
                    ticks: { color: '#9CA3AF' }
                  }
                }
              }}
              height={200}
            />
          </div>
        </>
      )}

      {/* Agents View */}
      {viewMode === 'agents' && (
        <>
          {/* Filters */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Filter className="h-4 w-4 text-gray-400" />
              <span className="text-gray-400">Filters:</span>
            </div>
            
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="bg-gray-800 text-white rounded px-3 py-1 border border-gray-600"
            >
              <option value="all">All Types</option>
              <option value="infrastructure">Infrastructure</option>
              <option value="monitoring">Monitoring</option>
              <option value="optimization">Optimization</option>
              <option value="integration">Integration</option>
            </select>
            
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="bg-gray-800 text-white rounded px-3 py-1 border border-gray-600"
            >
              <option value="all">All Status</option>
              <option value="running">Running</option>
              <option value="paused">Paused</option>
              <option value="stopped">Stopped</option>
              <option value="error">Error</option>
            </select>
            
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value as any)}
              className="bg-gray-800 text-white rounded px-3 py-1 border border-gray-600"
            >
              <option value="1h">Last Hour</option>
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
            </select>
          </div>

          {/* Agent List */}
          <div className="space-y-4">
            {agentsLoading ? (
              <div className="text-center py-8 text-gray-400">Loading agents...</div>
            ) : filteredAgents.length === 0 ? (
              <div className="text-center py-8 text-gray-400">No agents found</div>
            ) : (
              filteredAgents.map(agent => {
                const TypeIcon = AGENT_TYPES[agent.type].icon;
                const isExpanded = expandedAgents.has(agent.id);
                
                return (
                  <div key={agent.id} className="bg-gray-800 rounded-lg border border-gray-700">
                    {/* Agent Header */}
                    <div className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <button
                            onClick={() => {
                              const newExpanded = new Set(expandedAgents);
                              if (isExpanded) {
                                newExpanded.delete(agent.id);
                              } else {
                                newExpanded.add(agent.id);
                              }
                              setExpandedAgents(newExpanded);
                            }}
                            className="text-gray-400 hover:text-white"
                          >
                            {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                          </button>
                          
                          <TypeIcon className={`h-5 w-5 text-${AGENT_TYPES[agent.type].color}-400`} />
                          
                          <div>
                            <h3 className="font-semibold">{agent.name}</h3>
                            <p className="text-sm text-gray-400">{agent.description}</p>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-4">
                          {renderHealthIndicator(agent.health)}
                          {renderStatusBadge(agent.status)}
                          
                          <div className="flex items-center space-x-2">
                            {agent.status === 'running' ? (
                              <button
                                onClick={() => stopAgent.mutate(agent.id)}
                                className="p-1 hover:bg-gray-700 rounded"
                                title="Stop agent"
                              >
                                <Pause className="h-4 w-4" />
                              </button>
                            ) : (
                              <button
                                onClick={() => startAgent.mutate(agent.id)}
                                className="p-1 hover:bg-gray-700 rounded"
                                title="Start agent"
                              >
                                <Play className="h-4 w-4" />
                              </button>
                            )}
                            
                            <button
                              onClick={() => setSelectedAgent(agent.id)}
                              className="p-1 hover:bg-gray-700 rounded"
                              title="View details"
                            >
                              <Settings className="h-4 w-4" />
                            </button>
                          </div>
                        </div>
                      </div>
                      
                      {/* Quick Stats */}
                      <div className="mt-3 grid grid-cols-4 gap-4 text-sm">
                        <div>
                          <span className="text-gray-400">Actions Today:</span>
                          <span className="ml-1 font-medium">{agent.metrics.actionsToday}</span>
                        </div>
                        <div>
                          <span className="text-gray-400">Success Rate:</span>
                          <span className="ml-1 font-medium">{agent.metrics.successRate}%</span>
                        </div>
                        <div>
                          <span className="text-gray-400">Response:</span>
                          <span className="ml-1 font-medium">{agent.metrics.avgResponseTime}ms</span>
                        </div>
                        <div>
                          <span className="text-gray-400">Uptime:</span>
                          <span className="ml-1 font-medium">{formatDuration(agent.uptime)}</span>
                        </div>
                      </div>
                    </div>
                    
                    {/* Expanded Details */}
                    {isExpanded && (
                      <div className="px-4 pb-4 pt-0 border-t border-gray-600">
                        <div className="grid grid-cols-3 gap-4 mt-4">
                          <div>
                            <h4 className="text-sm font-semibold text-gray-400 mb-2">Resource Usage</h4>
                            <div className="space-y-2">
                              <div>
                                <div className="flex justify-between text-xs mb-1">
                                  <span>CPU</span>
                                  <span>{agent.metrics.resourceUsage.cpu}%</span>
                                </div>
                                <div className="w-full bg-gray-700 rounded-full h-2">
                                  <div 
                                    className="bg-blue-400 h-2 rounded-full"
                                    style={{ width: `${agent.metrics.resourceUsage.cpu}%` }}
                                  />
                                </div>
                              </div>
                              <div>
                                <div className="flex justify-between text-xs mb-1">
                                  <span>Memory</span>
                                  <span>{agent.metrics.resourceUsage.memory}%</span>
                                </div>
                                <div className="w-full bg-gray-700 rounded-full h-2">
                                  <div 
                                    className="bg-green-400 h-2 rounded-full"
                                    style={{ width: `${agent.metrics.resourceUsage.memory}%` }}
                                  />
                                </div>
                              </div>
                              {agent.metrics.resourceUsage.gpu !== undefined && (
                                <div>
                                  <div className="flex justify-between text-xs mb-1">
                                    <span>GPU</span>
                                    <span>{agent.metrics.resourceUsage.gpu}%</span>
                                  </div>
                                  <div className="w-full bg-gray-700 rounded-full h-2">
                                    <div 
                                      className="bg-yellow-400 h-2 rounded-full"
                                      style={{ width: `${agent.metrics.resourceUsage.gpu}%` }}
                                    />
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                          
                          <div>
                            <h4 className="text-sm font-semibold text-gray-400 mb-2">Configuration</h4>
                            <div className="space-y-1 text-sm">
                              <div className="flex justify-between">
                                <span className="text-gray-400">Auto Restart:</span>
                                <span>{agent.config.autoRestart ? 'Enabled' : 'Disabled'}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-400">Max Actions/Hour:</span>
                                <span>{agent.config.maxActionsPerHour}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-400">Version:</span>
                                <span>{agent.version}</span>
                              </div>
                            </div>
                          </div>
                          
                          <div>
                            <h4 className="text-sm font-semibold text-gray-400 mb-2">Thresholds</h4>
                            <div className="space-y-1 text-sm">
                              {Object.entries(agent.config.thresholds).map(([key, value]) => (
                                <div key={key} className="flex justify-between">
                                  <span className="text-gray-400">{key.replace(/_/g, ' ')}:</span>
                                  <span>{value}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                        
                        <div className="mt-4 text-sm text-gray-400">
                          Last activity: {formatTimestamp(agent.lastActivity)}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </>
      )}

      {/* MCP Servers View */}
      {viewMode === 'mcp' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {systemHealth?.mcp_servers && Object.entries(systemHealth.mcp_servers).map(([name, server]) => (
              <div key={name} className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-white">{name}</h3>
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
                  <div>Category: {name.includes('ai') ? 'AI' : name.includes('git') ? 'Development' : 'Business'}</div>
                  <div>Uptime: {systemHealth.metrics.uptime_hours.toFixed(1)}h</div>
                  <div>Response: &lt;50ms</div>
                </div>
              </div>
            ))}
          </div>

          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-4">MCP Server Overview</h3>
            <div className="text-gray-400 space-y-2">
              <p>Model Context Protocol (MCP) servers provide specialized functionality for the Sophia AI system.</p>
              <p>Each server handles specific integration points with external services and APIs.</p>
              <ul className="list-disc list-inside mt-4 space-y-1">
                <li>GitHub integration for code management</li>
                <li>Linear for project tracking</li>
                <li>Gong.io for call analysis</li>
                <li>HubSpot for CRM operations</li>
                <li>Slack for team communication</li>
                <li>AI Memory for conversational context</li>
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Analytics View */}
      {viewMode === 'analytics' && (
        <div className="space-y-6">
          {/* ROI Summary */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-4">Automation ROI</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-3xl font-bold text-green-400">
                  {analytics?.automationROI.efficiencyGain || 0}%
                </div>
                <div className="text-gray-400">Efficiency Gain</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-400">
                  {analytics?.automationROI.manualInterventionsAvoided || 0}
                </div>
                <div className="text-gray-400">Manual Work Avoided</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-yellow-400">
                  ${analytics?.costSavings.total.toFixed(2) || '0.00'}
                </div>
                <div className="text-gray-400">Total Cost Saved</div>
              </div>
            </div>
          </div>

          {/* Performance Metrics */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-4">Performance Metrics</h3>
            <Doughnut 
              data={performanceChartData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'bottom',
                    labels: { color: '#9CA3AF' }
                  }
                }
              }}
              height={300}
            />
          </div>

          {/* Action Timeline */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-4">Recent Activity Timeline</h3>
            <div className="space-y-4">
              {actions?.map(action => (
                <div key={action.id} className="flex items-center space-x-4">
                  <div className={`w-3 h-3 rounded-full bg-${ACTION_STATUS_COLORS[action.status]}-500`} />
                  <div className="flex-1">
                    <div className="text-white">{action.action}</div>
                    <div className="text-xs text-gray-400">
                      {action.agentName} • {formatTimestamp(action.timestamp)}
                    </div>
                  </div>
                  {action.canRollback && (
                    <button
                      onClick={() => rollbackAction.mutate(action.id)}
                      className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-white"
                      title="Rollback action"
                    >
                      <RotateCcw className="h-3 w-3" />
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Emergency Stop Modal */}
      {showEmergencyStop && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 max-w-md border border-red-600">
            <div className="flex items-center space-x-3 mb-4">
              <Shield className="h-8 w-8 text-red-500" />
              <h2 className="text-xl font-bold">Emergency Stop</h2>
            </div>
            
            <p className="text-gray-300 mb-6">
              This action will immediately halt all autonomous agent operations. 
              Use only in case of critical issues.
            </p>
            
            <div className="bg-red-900 bg-opacity-20 border border-red-600 rounded p-4 mb-6">
              <p className="text-sm text-red-300">
                <strong>Warning:</strong> All running agents will be stopped. 
                Pending actions will be cancelled. This may require manual intervention to restart.
              </p>
            </div>
            
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowEmergencyStop(false)}
                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleEmergencyStop}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded transition-colors font-semibold"
              >
                Execute Emergency Stop
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UnifiedAgentOrchestration;

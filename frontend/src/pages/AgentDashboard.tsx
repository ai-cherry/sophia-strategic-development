/**
 * 🤖 AUTONOMOUS AGENTS UNIFIED DASHBOARD
 * 
 * Comprehensive monitoring and control center for all autonomous agents
 * 
 * Features:
 * - Real-time agent status monitoring
 * - Action history with timeline view
 * - Control panel for agent management
 * - Analytics and ROI calculations
 * - Emergency stop capabilities
 * 
 * Architecture:
 * - React + TypeScript
 * - Real-time WebSocket updates
 * - Chart.js for visualizations
 * - Integration with backend agent monitoring API
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Line, Bar, Doughnut, Scatter } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
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

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

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

// Constants
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

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

const AgentDashboard: React.FC = () => {
  // State management
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');

/**
 * 🎯 SOPHIA AI DASHBOARD TYPES
 * Comprehensive TypeScript definitions for the executive dashboard
 * 
 * Created as part of Phase 1 Frontend Refactoring
 * - Extracted from 2000+ line SophiaExecutiveDashboard.tsx
 * - Provides type safety for all dashboard components
 * - Enables proper component extraction and modularity
 */

import { ComponentType } from 'react';

// Tab Configuration Types
export interface TabConfig {
  icon: ComponentType<any>;
  label: string;
  color: string;
}

export interface IntelligenceTabs {
  [key: string]: TabConfig;
}

// Chat and Message Types
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  sources?: string[];
  insights?: string[];
  recommendations?: string[];
  metadata?: {
    processing_time_ms: number;
    confidence_score: number;
    orchestrator_version: string;
    servers_used: string[];
    session_id: string;
    user_id: string;
    conversation_length: number;
  };
  temporal_learning_applied?: boolean;
  temporal_interaction_id?: string;
}

// System Health Types
export interface MCPServerHealth {
  status: string;
  port: number;
}

export interface ServiceHealth {
  status: string;
  requests_total: number;
  requests_successful: number;
  requests_failed: number;
  active_sessions: number;
}

export interface OrchestratorHealth {
  status: string;
  initialized: boolean;
  version: string;
}

export interface LambdaLabsHealth {
  status: string;
  daily_cost: number;
  models_available: number;
  requests_today: number;
  cost_efficiency: string;
  gpu_utilization: number;
}

export interface TemporalLearningHealth {
  total_interactions: number;
  knowledge_entries: number;
  learning_active: boolean;
  last_update: string;
}

export interface SystemMetrics {
  uptime_hours: number;
  success_rate: number;
  average_response_time: string;
  memory_usage: string;
}

export interface SystemHealth {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  version: string;
  environment: string;
  uptime_seconds: number;
  services: {
    api: ServiceHealth;
    orchestrator: OrchestratorHealth;
  };
  mcp_servers: {
    [key: string]: MCPServerHealth;
  };
  lambda_labs: LambdaLabsHealth;
  temporal_learning: TemporalLearningHealth;
  metrics: SystemMetrics;
}

// Alert and Notification Types
export interface ProactiveAlert {
  id: string;
  type: 'opportunity' | 'risk' | 'system' | 'business';
  title: string;
  description: string;
  urgency: 'low' | 'medium' | 'high' | 'critical';
  timestamp: string;
  actionable: boolean;
}

// Ice Breaker Prompt Types
export interface IceBreakerPrompt {
  id: string;
  category: string;
  prompt: string;
  icon: ComponentType<any>;
  focusMode?: 'business' | 'data' | 'system';
}

// Workflow Automation Types
export interface WorkflowStatus {
  name: string;
  status: 'active' | 'inactive' | 'scheduled' | 'error';
  executions: number;
  lastRun: string;
  successRate?: number;
}

export interface WorkflowMetrics {
  activeWorkflows: number;
  executionsToday: number;
  timeSavedHours: number;
  successRate: number;
}

export interface WorkflowActivity {
  action: string;
  time: string;
  status: 'success' | 'warning' | 'error';
}

// System Command Types
export interface SystemCommandMetrics {
  serverHealth: number;
  mcpServersOnline: number;
  mcpServersTotal: number;
  responseTime: string;
  dailyCost: number;
}

// Memory Architecture Types
export interface MemoryLayer {
  name: string;
  type: 'cache' | 'vector' | 'sql' | 'graph';
  status: 'online' | 'offline' | 'degraded';
  latency: string;
  hitRate?: number;
  size?: string;
  capacity?: string;
}

// Agent Orchestration Types
export interface AgentStatus {
  name: string;
  type: string;
  status: 'active' | 'idle' | 'error';
  tasksProcessed: number;
  lastActivity: string;
  performance: number;
}

// Project Management Types
export interface ProjectTask {
  id: string;
  title: string;
  status: 'todo' | 'in-progress' | 'completed' | 'blocked';
  priority: 'low' | 'medium' | 'high' | 'critical';
  assignee?: string;
  dueDate?: string;
  progress?: number;
}

export interface Project {
  id: string;
  name: string;
  status: 'active' | 'completed' | 'on-hold';
  progress: number;
  tasks: ProjectTask[];
  deadline?: string;
  budget?: number;
  spent?: number;
}

// Component Props Types
export interface BaseTabProps {
  systemHealth?: SystemHealth;
  isLoading?: boolean;
  className?: string;
}

export interface ChatInterfaceProps extends BaseTabProps {
  messages: ChatMessage[];
  inputMessage: string;
  setInputMessage: (message: string) => void;
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  isListening: boolean;
  onToggleListening: () => void;
  iceBreakerPrompts: IceBreakerPrompt[];
  temporalLearningEnabled: boolean;
  personalityMode: string;
}

export interface WorkflowAutomationProps extends BaseTabProps {
  workflows: WorkflowStatus[];
  metrics: WorkflowMetrics;
  activities: WorkflowActivity[];
  onCreateWorkflow: () => void;
  onViewDashboard: () => void;
  onViewAnalytics: () => void;
}

export interface SystemCommandProps extends BaseTabProps {
  onRestartServices: () => void;
  onDeployUpdates: () => void;
  onViewLogs: () => void;
  onEmergencyStop: () => void;
}

export interface MemoryArchitectureProps extends BaseTabProps {
  memoryLayers: MemoryLayer[];
  totalMemoryUsage: number;
  cacheHitRate: number;
  queryLatency: string;
}

export interface AgentOrchestrationProps extends BaseTabProps {
  agents: AgentStatus[];
  totalTasks: number;
  activeTasks: number;
  averagePerformance: number;
}

export interface ProjectManagementProps extends BaseTabProps {
  projects: Project[];
  onCreateProject: () => void;
  onUpdateTask: (projectId: string, taskId: string, updates: Partial<ProjectTask>) => void;
}

// Dashboard Store Types (for future Zustand implementation)
export interface DashboardState {
  activeTab: string;
  sidebarCollapsed: boolean;
  searchQuery: string;
  searchResults: any[];
  isSearching: boolean;
  temporalLearningEnabled: boolean;
  personalityMode: string;
  websocket: WebSocket | null;
  proactiveAlerts: ProactiveAlert[];
}

export interface DashboardActions {
  setActiveTab: (tab: string) => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setSearchQuery: (query: string) => void;
  setSearchResults: (results: any[]) => void;
  setIsSearching: (searching: boolean) => void;
  setTemporalLearningEnabled: (enabled: boolean) => void;
  setPersonalityMode: (mode: string) => void;
  setWebsocket: (ws: WebSocket | null) => void;
  addProactiveAlert: (alert: ProactiveAlert) => void;
  removeProactiveAlert: (alertId: string) => void;
}

export type DashboardStore = DashboardState & DashboardActions;

// Environment and Configuration Types
export interface APIConfig {
  timeout: number;
  retries: number;
  baseURL: string;
  websocketURL: string;
}

export interface EnvironmentConfig {
  development: APIConfig;
  production: APIConfig;
  lambdaLabs: APIConfig;
} 
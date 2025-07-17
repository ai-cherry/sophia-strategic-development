export interface BusinessQuery {
  query: string;
  user_id: string;
  department?: string;
  priority?: 'low' | 'normal' | 'high' | 'urgent';
  context?: Record<string, any>;
}

export interface BusinessResponse {
  response: string;
  insights: string[];
  recommendations: string[];
  data_sources: string[];
  confidence: number;
  processing_time_ms: number;
  metadata?: Record<string, any>;
}

export interface AgentCapability {
  name: string;
  description: string;
  capabilities: string[];
  data_sources: string[];
  example_queries: string[];
}

export interface BusinessAIAgent {
  revenue: AgentCapability;
  team: AgentCapability;
  customer: AgentCapability;
  market: AgentCapability;
}

export interface BusinessAIHealth {
  status: 'healthy' | 'unhealthy';
  timestamp: string;
  agents: Record<string, string>;
  shared_mcp_servers: string[];
  configuration: Record<string, any>;
  error?: string;
}

export interface BusinessAIAnalytics {
  usage_metrics: {
    total_queries_today: number;
    total_queries_this_week: number;
    total_queries_this_month: number;
    average_response_time_ms: number;
    average_confidence_score: number;
  };
  agent_usage: Record<string, {
    queries: number;
    avg_confidence: number;
  }>;
  user_engagement: {
    active_users_today: number;
    active_users_this_week: number;
    average_queries_per_user: number;
    user_satisfaction_score: number;
  };
  performance_metrics: {
    uptime_percentage: number;
    error_rate_percentage: number;
    cache_hit_rate_percentage: number;
    p95_response_time_ms: number;
  };
  insights: string[];
} 
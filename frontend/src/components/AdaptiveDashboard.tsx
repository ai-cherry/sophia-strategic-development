/**
 * Adaptive Dashboard for Sophia AI
 * Dynamic, responsive interface with personality modes
 */

import React, { useState, useEffect, useMemo } from 'react';

interface AdaptiveDashboardProps {
  personalityMode?: 'professional' | 'snarky' | 'analytical' | 'creative';
  themePreference?: 'dark' | 'light' | 'cyberpunk';
  interactionStyle?: 'executive' | 'analytical' | 'overview';
}

export const AdaptiveDashboard: React.FC<AdaptiveDashboardProps> = ({
  personalityMode = 'professional',
  themePreference = 'dark',
  interactionStyle = 'executive'
}) => {
  const [metrics, setMetrics] = useState(null);
  const [routerStats, setRouterStats] = useState(null);
  
  // Theme configuration
  const themeConfig = useMemo(() => {
    const themes = {
      dark: {
        primary: '#3B82F6',
        secondary: '#8B5CF6',
        background: '#111827',
        containerClass: 'bg-gray-900 text-white'
      },
      light: {
        primary: '#2563EB',
        secondary: '#7C3AED',
        background: '#FFFFFF',
        containerClass: 'bg-white text-gray-900'
      },
      cyberpunk: {
        primary: '#00D2FF',
        secondary: '#FF0080',
        background: '#0A0A0A',
        containerClass: 'bg-black text-cyan-400'
      }
    };
    return themes[themePreference];
  }, [themePreference]);
  
  // Component layout based on interaction style
  const layoutConfig = useMemo(() => {
    const layouts = {
      executive: {
        kpiCards: { cols: 4, priority: 'high' },
        charts: { cols: 2, priority: 'medium' }
      },
      analytical: {
        charts: { cols: 3, priority: 'high' },
        kpiCards: { cols: 2, priority: 'medium' }
      },
      overview: {
        kpiCards: { cols: 3, priority: 'medium' },
        charts: { cols: 2, priority: 'medium' }
      }
    };
    return layouts[interactionStyle];
  }, [interactionStyle]);
  
  // Fetch real-time metrics
  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await fetch('/api/v4/dashboard/metrics');
        const data = await response.json();
        setMetrics(data);
      } catch (error) {
        console.error('Failed to fetch metrics:', error);
      }
    };
    
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000);
    return () => clearInterval(interval);
  }, []);
  
  // Fetch router statistics
  useEffect(() => {
    const fetchRouterStats = async () => {
      try {
        const response = await fetch('/api/v4/router/stats');
        const data = await response.json();
        setRouterStats(data);
      } catch (error) {
        console.error('Failed to fetch router stats:', error);
      }
    };
    
    fetchRouterStats();
    const interval = setInterval(fetchRouterStats, 10000);
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div className={`adaptive-dashboard ${themeConfig.containerClass} min-h-screen p-6`}>
      <header className="mb-8">
        <h1 className="text-3xl font-bold mb-2">
          Sophia AI Strategic Dashboard
        </h1>
        <div className="flex items-center gap-4">
          <span className="text-sm opacity-75">
            Mode: {personalityMode} | Theme: {themePreference} | Style: {interactionStyle}
          </span>
          <ThemeToggle currentTheme={themePreference} />
        </div>
      </header>
      
      <div className="grid gap-6">
        {/* Router Performance Section */}
        <section className="router-performance">
          <h2 className="text-xl font-semibold mb-4">🚀 Router Performance</h2>
          <div className="grid grid-cols-4 gap-4">
            <KPICard
              title="Routing Latency"
              value={routerStats?.latency_p95 || 0}
              unit="ms"
              target={180}
              trend="down"
            />
            <KPICard
              title="Model Selection Accuracy"
              value={routerStats?.accuracy || 0}
              unit="%"
              target={90}
              trend="up"
            />
            <KPICard
              title="Cost Per Query"
              value={routerStats?.cost_per_query || 0}
              unit="$"
              target={0.05}
              trend="down"
            />
            <KPICard
              title="Success Rate"
              value={routerStats?.success_rate || 0}
              unit="%"
              target={99.5}
              trend="up"
            />
          </div>
        </section>
        
        {/* System Health Section */}
        <section className="system-health">
          <h2 className="text-xl font-semibold mb-4">🔧 System Health</h2>
          <div className="grid grid-cols-3 gap-4">
            <HealthCard
              title="MCP Servers"
              status={metrics?.mcp_health || 'unknown'}
              count={metrics?.mcp_count || 0}
            />
            <HealthCard
              title="N8N Workflows"
              status={metrics?.workflow_health || 'unknown'}
              count={metrics?.workflow_count || 0}
            />
            <HealthCard
              title="Agent Builder"
              status={metrics?.agent_health || 'unknown'}
              count={metrics?.agent_count || 0}
            />
          </div>
        </section>
        
        {/* Interactive Charts */}
        <section className="charts">
          <h2 className="text-xl font-semibold mb-4">📊 Analytics</h2>
          <div className="grid grid-cols-2 gap-6">
            <ChartCard
              title="Model Usage Distribution"
              type="pie"
              data={routerStats?.model_distribution || []}
            />
            <ChartCard
              title="Response Time Trends"
              type="line"
              data={routerStats?.response_trends || []}
            />
          </div>
        </section>
      </div>
    </div>
  );
};

// Supporting components
const KPICard = ({ title, value, unit, target, trend }) => (
  <div className="bg-gray-800 p-4 rounded-lg">
    <h3 className="text-sm font-medium text-gray-400">{title}</h3>
    <div className="flex items-center justify-between mt-2">
      <span className="text-2xl font-bold">{value}{unit}</span>
      <TrendIndicator trend={trend} />
    </div>
    <div className="text-xs text-gray-500 mt-1">Target: {target}{unit}</div>
  </div>
);

const HealthCard = ({ title, status, count }) => (
  <div className="bg-gray-800 p-4 rounded-lg">
    <h3 className="text-sm font-medium text-gray-400">{title}</h3>
    <div className="flex items-center gap-2 mt-2">
      <StatusIndicator status={status} />
      <span className="text-lg font-semibold">{count} active</span>
    </div>
  </div>
);

const ChartCard = ({ title, type, data }) => (
  <div className="bg-gray-800 p-4 rounded-lg">
    <h3 className="text-sm font-medium text-gray-400 mb-4">{title}</h3>
    <div className="h-48">
      {/* Chart implementation would go here */}
      <div className="flex items-center justify-center h-full text-gray-500">
        {type.toUpperCase()} Chart - {data.length} data points
      </div>
    </div>
  </div>
);

const TrendIndicator = ({ trend }) => (
  <span className={`text-sm ${trend === 'up' ? 'text-green-400' : 'text-red-400'}`}>
    {trend === 'up' ? '↗️' : '↘️'}
  </span>
);

const StatusIndicator = ({ status }) => (
  <span className={`w-3 h-3 rounded-full ${
    status === 'healthy' ? 'bg-green-400' : 
    status === 'warning' ? 'bg-yellow-400' : 'bg-red-400'
  }`} />
);

const ThemeToggle = ({ currentTheme }) => (
  <button className="px-3 py-1 text-xs bg-gray-700 rounded">
    Theme: {currentTheme}
  </button>
);

export default AdaptiveDashboard;

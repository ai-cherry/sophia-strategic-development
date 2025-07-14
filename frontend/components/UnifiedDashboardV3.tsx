/**
 * Unified Dashboard v3 - Phase 3
 * Enhanced BI dashboard with Phase 2 integrations
 * Real-time trends, personality modes, multi-hop insights, optimization metrics
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  LinearProgress,
  Alert,
  IconButton,
  Tooltip,
  Switch,
  FormControlLabel,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  TrendingUp,
  Psychology,
  AccountTree,
  Speed,
  Chat,
  Refresh,
  Settings,
  Analytics,
  Timeline,
  AutoGraph,
  SmartToy,
  TrendingFlat
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  ScatterChart,
  Scatter
} from 'recharts';

// Types for Phase 3 integrations
interface ChatMetrics {
  total_chats: number;
  avg_processing_time_ms: number;
  avg_confidence_score: number;
  mode_distribution: Record<string, number>;
  stage_performance: Record<string, number>;
}

interface TrendData {
  topic: string;
  volume: number;
  sentiment: number;
  related_keywords: string[];
  timestamp: string;
}

interface PersonalityStats {
  responses_generated: number;
  avg_sass_level: number;
  personality_adjustments: number;
  user_profiles_created: number;
  personality_mode_distribution: Record<string, number>;
}

interface OptimizationMetrics {
  total_endpoints_monitored: number;
  optimized_endpoints: number;
  optimization_coverage: number;
  avg_performance_score: number;
  recent_optimizations: number;
}

interface UnifiedDashboardData {
  chat_metrics: ChatMetrics;
  trends_data: TrendData[];
  personality_stats: PersonalityStats;
  optimization_metrics: OptimizationMetrics;
  system_health: {
    status: 'healthy' | 'warning' | 'error';
    uptime_percentage: number;
    response_time_p95: number;
    error_rate: number;
  };
  last_updated: string;
}

// Color schemes for different data types
const COLORS = {
  primary: '#1976d2',
  secondary: '#dc004e',
  success: '#2e7d32',
  warning: '#ed6c02',
  error: '#d32f2f',
  trends: ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#8dd1e1'],
  personality: ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#8dd1e1', '#d084d0']
};

const UnifiedDashboardV3: React.FC = () => {
  // State management
  const [dashboardData, setDashboardData] = useState<UnifiedDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(5000); // 5 seconds
  const [selectedView, setSelectedView] = useState<'overview' | 'chat' | 'trends' | 'personality' | 'optimization'>('overview');
  const [settingsOpen, setSettingsOpen] = useState(false);

  // Mock data for development (replace with real API calls)
  const mockDashboardData: UnifiedDashboardData = {
    chat_metrics: {
      total_chats: 1247,
      avg_processing_time_ms: 156.7,
      avg_confidence_score: 0.847,
      mode_distribution: {
        'business_intelligence': 523,
        'strategic_analysis': 312,
        'quick_answer': 287,
        'conversational': 125
      },
      stage_performance: {
        'intent_analysis': 23.4,
        'trend_injection': 45.2,
        'multi_hop_reasoning': 67.8,
        'personality_synthesis': 12.1,
        'optimization': 8.2,
        'response_generation': 34.5
      }
    },
    trends_data: [
      { topic: 'AI Revenue Growth', volume: 15000, sentiment: 0.7, related_keywords: ['AI', 'revenue', 'growth'], timestamp: '2025-01-12T10:30:00Z' },
      { topic: 'Q4 Earnings', volume: 12000, sentiment: 0.3, related_keywords: ['earnings', 'Q4', 'financial'], timestamp: '2025-01-12T10:25:00Z' },
      { topic: 'Remote Work Trends', volume: 8500, sentiment: 0.5, related_keywords: ['remote', 'work', 'productivity'], timestamp: '2025-01-12T10:20:00Z' },
      { topic: 'SaaS Metrics', volume: 6200, sentiment: 0.6, related_keywords: ['SaaS', 'metrics', 'ARR'], timestamp: '2025-01-12T10:15:00Z' },
      { topic: 'Customer Success', volume: 4800, sentiment: 0.8, related_keywords: ['customer', 'success', 'retention'], timestamp: '2025-01-12T10:10:00Z' }
    ],
    personality_stats: {
      responses_generated: 1247,
      avg_sass_level: 0.67,
      personality_adjustments: 89,
      user_profiles_created: 234,
      personality_mode_distribution: {
        'professional': 456,
        'confident': 312,
        'snarky': 287,
        'ceo_savage': 134,
        'neutral': 58
      }
    },
    optimization_metrics: {
      total_endpoints_monitored: 23,
      optimized_endpoints: 19,
      optimization_coverage: 0.826,
      avg_performance_score: 0.784,
      recent_optimizations: 7
    },
    system_health: {
      status: 'healthy',
      uptime_percentage: 99.7,
      response_time_p95: 189.3,
      error_rate: 0.003
    },
    last_updated: new Date().toISOString()
  };

  // Data fetching
  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // In production, replace with actual API calls
      // const [chatResponse, trendsResponse, personalityResponse, optimizationResponse] = await Promise.all([
      //   fetch('/api/chat/stats'),
      //   fetch('/api/trends/summary'),
      //   fetch('/api/personality/stats'),
      //   fetch('/api/optimization/report')
      // ]);

      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setDashboardData(mockDashboardData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch dashboard data');
    } finally {
      setLoading(false);
    }
  }, []);

  // Auto-refresh effect
  useEffect(() => {
    fetchDashboardData();

    if (autoRefresh) {
      const interval = setInterval(fetchDashboardData, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [fetchDashboardData, autoRefresh, refreshInterval]);

  // Computed metrics
  const computedMetrics = useMemo(() => {
    if (!dashboardData) return null;

    const totalChatModes = Object.values(dashboardData.chat_metrics.mode_distribution).reduce((sum, count) => sum + count, 0);
    const totalPersonalityModes = Object.values(dashboardData.personality_stats.personality_mode_distribution).reduce((sum, count) => sum + count, 0);

    return {
      chat_mode_percentages: Object.entries(dashboardData.chat_metrics.mode_distribution).map(([mode, count]) => ({
        name: mode.replace('_', ' ').toUpperCase(),
        value: count,
        percentage: ((count / totalChatModes) * 100).toFixed(1)
      })),
      personality_mode_percentages: Object.entries(dashboardData.personality_stats.personality_mode_distribution).map(([mode, count]) => ({
        name: mode.toUpperCase(),
        value: count,
        percentage: ((count / totalPersonalityModes) * 100).toFixed(1)
      })),
      stage_performance_data: Object.entries(dashboardData.chat_metrics.stage_performance).map(([stage, time]) => ({
        name: stage.replace('_', ' ').toUpperCase(),
        time: time,
        efficiency: Math.max(0, 100 - (time / 100) * 100) // Inverse relationship for efficiency
      })),
      trends_sentiment_data: dashboardData.trends_data.map((trend, index) => ({
        name: trend.topic,
        volume: trend.volume,
        sentiment: trend.sentiment,
        sentiment_percentage: ((trend.sentiment + 1) / 2) * 100, // Convert -1,1 to 0,100
        color: COLORS.trends[index % COLORS.trends.length]
      }))
    };
  }, [dashboardData]);

  // Health status indicator
  const getHealthStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return COLORS.success;
      case 'warning': return COLORS.warning;
      case 'error': return COLORS.error;
      default: return COLORS.primary;
    }
  };

  // Render overview cards
  const renderOverviewCards = () => (
    <Grid container spacing={3}>
      {/* Chat Performance Card */}
      <Grid item xs={12} md={6} lg={3}>
        <Card elevation={3}>
          <CardContent>
            <Box display="flex" alignItems="center" mb={2}>
              <Chat color="primary" sx={{ mr: 1 }} />
              <Typography variant="h6">Chat Performance</Typography>
            </Box>
            <Typography variant="h4" color="primary" gutterBottom>
              {dashboardData?.chat_metrics.total_chats.toLocaleString()}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total Conversations
            </Typography>
            <Box mt={2}>
              <Typography variant="body2">
                Avg Response: {dashboardData?.chat_metrics.avg_processing_time_ms.toFixed(1)}ms
              </Typography>
              <Typography variant="body2">
                Confidence: {((dashboardData?.chat_metrics.avg_confidence_score || 0) * 100).toFixed(1)}%
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Trends Injection Card */}
      <Grid item xs={12} md={6} lg={3}>
        <Card elevation={3}>
          <CardContent>
            <Box display="flex" alignItems="center" mb={2}>
              <TrendingUp color="secondary" sx={{ mr: 1 }} />
              <Typography variant="h6">Live Trends</Typography>
            </Box>
            <Typography variant="h4" color="secondary" gutterBottom>
              {dashboardData?.trends_data.length}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Active Trends
            </Typography>
            <Box mt={2}>
              <Typography variant="body2">
                Avg Volume: {Math.round((dashboardData?.trends_data.reduce((sum, t) => sum + t.volume, 0) || 0) / (dashboardData?.trends_data.length || 1)).toLocaleString()}
              </Typography>
              <Typography variant="body2">
                Avg Sentiment: {((dashboardData?.trends_data.reduce((sum, t) => sum + t.sentiment, 0) || 0) / (dashboardData?.trends_data.length || 1)).toFixed(2)}
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Personality Engine Card */}
      <Grid item xs={12} md={6} lg={3}>
        <Card elevation={3}>
          <CardContent>
            <Box display="flex" alignItems="center" mb={2}>
              <Psychology color="success" sx={{ mr: 1 }} />
              <Typography variant="h6">Personality Engine</Typography>
            </Box>
            <Typography variant="h4" color="success" gutterBottom>
              {dashboardData?.personality_stats.user_profiles_created}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              User Profiles
            </Typography>
            <Box mt={2}>
              <Typography variant="body2">
                Avg Sass: {((dashboardData?.personality_stats.avg_sass_level || 0) * 100).toFixed(0)}%
              </Typography>
              <Typography variant="body2">
                Adjustments: {dashboardData?.personality_stats.personality_adjustments}
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Optimization Card */}
      <Grid item xs={12} md={6} lg={3}>
        <Card elevation={3}>
          <CardContent>
            <Box display="flex" alignItems="center" mb={2}>
              <Speed color="warning" sx={{ mr: 1 }} />
              <Typography variant="h6">Optimization</Typography>
            </Box>
            <Typography variant="h4" color="warning" gutterBottom>
              {((dashboardData?.optimization_metrics.optimization_coverage || 0) * 100).toFixed(0)}%
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Coverage
            </Typography>
            <Box mt={2}>
              <Typography variant="body2">
                Endpoints: {dashboardData?.optimization_metrics.optimized_endpoints}/{dashboardData?.optimization_metrics.total_endpoints_monitored}
              </Typography>
              <Typography variant="body2">
                Score: {((dashboardData?.optimization_metrics.avg_performance_score || 0) * 100).toFixed(0)}%
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  // Render chat analytics
  const renderChatAnalytics = () => (
    <Grid container spacing={3}>
      {/* Chat Mode Distribution */}
      <Grid item xs={12} md={6}>
        <Card elevation={3}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Chat Mode Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={computedMetrics?.chat_mode_percentages}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percentage }) => `${name}: ${percentage}%`}
                >
                  {computedMetrics?.chat_mode_percentages.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS.trends[index % COLORS.trends.length]} />
                  ))}
                </Pie>
                <RechartsTooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Grid>

      {/* Stage Performance */}
      <Grid item xs={12} md={6}>
        <Card elevation={3}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Processing Stage Performance
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={computedMetrics?.stage_performance_data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="name" 
                  angle={-45}
                  textAnchor="end"
                  height={100}
                  fontSize={10}
                />
                <YAxis />
                <RechartsTooltip />
                <Bar dataKey="time" fill={COLORS.primary} name="Time (ms)" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Grid>

      {/* Performance Metrics */}
      <Grid item xs={12}>
        <Card elevation={3}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Performance Metrics
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Average Processing Time
                  </Typography>
                  <Typography variant="h5" color="primary">
                    {dashboardData?.chat_metrics.avg_processing_time_ms.toFixed(1)}ms
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={Math.min(100, (dashboardData?.chat_metrics.avg_processing_time_ms || 0) / 3)}
                    sx={{ mt: 1 }}
                  />
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Average Confidence Score
                  </Typography>
                  <Typography variant="h5" color="success">
                    {((dashboardData?.chat_metrics.avg_confidence_score || 0) * 100).toFixed(1)}%
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={(dashboardData?.chat_metrics.avg_confidence_score || 0) * 100}
                    color="success"
                    sx={{ mt: 1 }}
                  />
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    System Health
                  </Typography>
                  <Typography variant="h5" style={{ color: getHealthStatusColor(dashboardData?.system_health.status || 'healthy') }}>
                    {dashboardData?.system_health.uptime_percentage.toFixed(1)}%
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={dashboardData?.system_health.uptime_percentage || 0}
                    color="success"
                    sx={{ mt: 1 }}
                  />
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  // Render trends analysis
  const renderTrendsAnalysis = () => (
    <Grid container spacing={3}>
      {/* Trending Topics */}
      <Grid item xs={12} md={8}>
        <Card elevation={3}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Trending Topics Analysis
            </Typography>
            <ResponsiveContainer width="100%" height={400}>
              <ScatterChart data={computedMetrics?.trends_sentiment_data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="volume" 
                  name="Volume"
                  type="number"
                  domain={['dataMin', 'dataMax']}
                />
                <YAxis 
                  dataKey="sentiment_percentage" 
                  name="Sentiment"
                  domain={[0, 100]}
                />
                <RechartsTooltip 
                  cursor={{ strokeDasharray: '3 3' }}
                  content={({ active, payload }) => {
                    if (active && payload && payload[0]) {
                      const data = payload[0].payload;
                      return (
                        <Box bgcolor="background.paper" p={2} border={1} borderColor="grey.300">
                          <Typography variant="subtitle2">{data.name}</Typography>
                          <Typography variant="body2">Volume: {data.volume.toLocaleString()}</Typography>
                          <Typography variant="body2">Sentiment: {data.sentiment.toFixed(2)}</Typography>
                        </Box>
                      );
                    }
                    return null;
                  }}
                />
                <Scatter dataKey="sentiment_percentage" fill={COLORS.secondary} />
              </ScatterChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Grid>

      {/* Trends List */}
      <Grid item xs={12} md={4}>
        <Card elevation={3}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Current Trends
            </Typography>
            <Box maxHeight={400} overflow="auto">
              {dashboardData?.trends_data.map((trend, index) => (
                <Box key={index} mb={2} p={2} bgcolor="grey.50" borderRadius={1}>
                  <Typography variant="subtitle2" gutterBottom>
                    {trend.topic}
                  </Typography>
                  <Box display="flex" alignItems="center" gap={1} mb={1}>
                    <Chip 
                      size="small" 
                      label={`${trend.volume.toLocaleString()} vol`}
                      color="primary"
                      variant="outlined"
                    />
                    <Chip 
                      size="small" 
                      label={`${trend.sentiment > 0 ? '+' : ''}${trend.sentiment.toFixed(2)}`}
                      color={trend.sentiment > 0 ? "success" : trend.sentiment < 0 ? "error" : "default"}
                      variant="outlined"
                    />
                  </Box>
                  <Box display="flex" flexWrap="wrap" gap={0.5}>
                    {trend.related_keywords.slice(0, 3).map((keyword, kidx) => (
                      <Chip 
                        key={kidx}
                        size="small" 
                        label={keyword}
                        variant="outlined"
                        sx={{ fontSize: '0.7rem' }}
                      />
                    ))}
                  </Box>
                </Box>
              ))}
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  // Render personality insights
  const renderPersonalityInsights = () => (
    <Grid container spacing={3}>
      {/* Personality Mode Distribution */}
      <Grid item xs={12} md={6}>
        <Card elevation={3}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Personality Mode Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={computedMetrics?.personality_mode_percentages}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <RechartsTooltip />
                <Bar dataKey="value" fill={COLORS.success} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Grid>

      {/* Sass Level Indicator */}
      <Grid item xs={12} md={6}>
        <Card elevation={3}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Personality Metrics
            </Typography>
            <Box mb={3}>
              <Typography variant="body2" color="text.secondary">
                Average Sass Level
              </Typography>
              <Typography variant="h4" color="secondary">
                {((dashboardData?.personality_stats.avg_sass_level || 0) * 100).toFixed(0)}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={(dashboardData?.personality_stats.avg_sass_level || 0) * 100}
                color="secondary"
                sx={{ mt: 1, height: 8 }}
              />
            </Box>

            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  Responses Generated
                </Typography>
                <Typography variant="h6">
                  {dashboardData?.personality_stats.responses_generated.toLocaleString()}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  Personality Adjustments
                </Typography>
                <Typography variant="h6">
                  {dashboardData?.personality_stats.personality_adjustments}
                </Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>

      {/* User Profiles Overview */}
      <Grid item xs={12}>
        <Card elevation={3}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              User Profile Analytics
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={3}>
                <Box textAlign="center">
                  <SmartToy sx={{ fontSize: 48, color: COLORS.primary, mb: 1 }} />
                  <Typography variant="h4" color="primary">
                    {dashboardData?.personality_stats.user_profiles_created}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Profiles Created
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={9}>
                <ResponsiveContainer width="100%" height={200}>
                  <AreaChart data={computedMetrics?.personality_mode_percentages}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <RechartsTooltip />
                    <Area 
                      type="monotone" 
                      dataKey="value" 
                      stroke={COLORS.success} 
                      fill={COLORS.success}
                      fillOpacity={0.3}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  // Render optimization metrics
  const renderOptimizationMetrics = () => (
    <Grid container spacing={3}>
      {/* Optimization Coverage */}
      <Grid item xs={12} md={6}>
        <Card elevation={3}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Optimization Coverage
            </Typography>
            <Box textAlign="center" mb={3}>
              <Typography variant="h2" color="warning">
                {((dashboardData?.optimization_metrics.optimization_coverage || 0) * 100).toFixed(0)}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Endpoints Optimized
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={(dashboardData?.optimization_metrics.optimization_coverage || 0) * 100}
              color="warning"
              sx={{ height: 12, borderRadius: 6 }}
            />
            <Box mt={2} display="flex" justifyContent="space-between">
              <Typography variant="body2">
                {dashboardData?.optimization_metrics.optimized_endpoints} optimized
              </Typography>
              <Typography variant="body2">
                {dashboardData?.optimization_metrics.total_endpoints_monitored} total
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Performance Score */}
      <Grid item xs={12} md={6}>
        <Card elevation={3}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Performance Score
            </Typography>
            <Box textAlign="center" mb={3}>
              <Typography variant="h2" color="success">
                {((dashboardData?.optimization_metrics.avg_performance_score || 0) * 100).toFixed(0)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Average Score
              </Typography>
            </Box>
            <Box>
              <Typography variant="body2" gutterBottom>
                Recent Optimizations: {dashboardData?.optimization_metrics.recent_optimizations}
              </Typography>
              <Chip 
                label="Alpha Tuning Active" 
                color="primary" 
                variant="outlined" 
                size="small"
                sx={{ mr: 1 }}
              />
              <Chip 
                label="Performance Monitoring" 
                color="success" 
                variant="outlined" 
                size="small"
              />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* System Health */}
      <Grid item xs={12}>
        <Card elevation={3}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              System Health Overview
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={3}>
                <Box textAlign="center">
                  <Typography variant="h4" style={{ color: getHealthStatusColor(dashboardData?.system_health.status || 'healthy') }}>
                    {dashboardData?.system_health.status?.toUpperCase()}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    System Status
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="success">
                    {dashboardData?.system_health.uptime_percentage.toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Uptime
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="primary">
                    {dashboardData?.system_health.response_time_p95.toFixed(1)}ms
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    P95 Response Time
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="error">
                    {(dashboardData?.system_health.error_rate * 100).toFixed(3)}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Error Rate
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  // Settings dialog
  const renderSettingsDialog = () => (
    <Dialog open={settingsOpen} onClose={() => setSettingsOpen(false)} maxWidth="sm" fullWidth>
      <DialogTitle>Dashboard Settings</DialogTitle>
      <DialogContent>
        <Box py={2}>
          <FormControlLabel
            control={
              <Switch
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
              />
            }
            label="Auto-refresh"
          />
          
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Refresh Interval</InputLabel>
            <Select
              value={refreshInterval}
              onChange={(e) => setRefreshInterval(Number(e.target.value))}
              disabled={!autoRefresh}
            >
              <MenuItem value={2000}>2 seconds</MenuItem>
              <MenuItem value={5000}>5 seconds</MenuItem>
              <MenuItem value={10000}>10 seconds</MenuItem>
              <MenuItem value={30000}>30 seconds</MenuItem>
              <MenuItem value={60000}>1 minute</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setSettingsOpen(false)}>Close</Button>
      </DialogActions>
    </Dialog>
  );

  // Main render
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Box textAlign="center">
          <LinearProgress sx={{ width: 200, mb: 2 }} />
          <Typography>Loading dashboard data...</Typography>
        </Box>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" action={
        <Button color="inherit" size="small" onClick={fetchDashboardData}>
          Retry
        </Button>
      }>
        {error}
      </Alert>
    );
  }

  return (
    <Box p={3}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Unified Dashboard v3
        </Typography>
        <Box display="flex" alignItems="center" gap={1}>
          <Chip 
            label={`Last updated: ${new Date(dashboardData?.last_updated || '').toLocaleTimeString()}`}
            size="small"
            variant="outlined"
          />
          <Tooltip title="Refresh">
            <IconButton onClick={fetchDashboardData} disabled={loading}>
              <Refresh />
            </IconButton>
          </Tooltip>
          <Tooltip title="Settings">
            <IconButton onClick={() => setSettingsOpen(true)}>
              <Settings />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* View Selector */}
      <Box mb={3}>
        <FormControl>
          <Select
            value={selectedView}
            onChange={(e) => setSelectedView(e.target.value as any)}
            variant="outlined"
            size="small"
          >
            <MenuItem value="overview">
              <Box display="flex" alignItems="center">
                <Analytics sx={{ mr: 1, fontSize: 20 }} />
                Overview
              </Box>
            </MenuItem>
            <MenuItem value="chat">
              <Box display="flex" alignItems="center">
                <Chat sx={{ mr: 1, fontSize: 20 }} />
                Chat Analytics
              </Box>
            </MenuItem>
            <MenuItem value="trends">
              <Box display="flex" alignItems="center">
                <TrendingUp sx={{ mr: 1, fontSize: 20 }} />
                Trends Analysis
              </Box>
            </MenuItem>
            <MenuItem value="personality">
              <Box display="flex" alignItems="center">
                <Psychology sx={{ mr: 1, fontSize: 20 }} />
                Personality Insights
              </Box>
            </MenuItem>
            <MenuItem value="optimization">
              <Box display="flex" alignItems="center">
                <Speed sx={{ mr: 1, fontSize: 20 }} />
                Optimization Metrics
              </Box>
            </MenuItem>
          </Select>
        </FormControl>
      </Box>

      {/* Content */}
      <Box>
        {selectedView === 'overview' && renderOverviewCards()}
        {selectedView === 'chat' && renderChatAnalytics()}
        {selectedView === 'trends' && renderTrendsAnalysis()}
        {selectedView === 'personality' && renderPersonalityInsights()}
        {selectedView === 'optimization' && renderOptimizationMetrics()}
      </Box>

      {/* Settings Dialog */}
      {renderSettingsDialog()}
    </Box>
  );
};

export default UnifiedDashboardV3; 
/**
 * 📊 BUSINESS INTELLIGENCE LIVE DASHBOARD
 * Real-time business metrics with external correlation and predictive insights
 * 
 * Features:
 * - Revenue intelligence with external factor correlation
 * - Customer health scores with external signals
 * - Sales intelligence with market factors
 * - Predictive analytics and trend analysis
 * - Actionable business recommendations
 */

import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
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
  BarChart3, 
  TrendingUp, 
  TrendingDown,
  DollarSign,
  Users,
  Target,
  AlertTriangle,
  CheckCircle,
  ArrowUp,
  ArrowDown,
  Zap,
  Eye,
  Clock,
  Award,
  Briefcase,
  PieChart,
  Activity
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
interface RevenueMetrics {
  current_month: number;
  previous_month: number;
  growth_rate: number;
  forecast_next_month: number;
  external_factors: ExternalFactor[];
  trend_data: TrendDataPoint[];
}

interface ExternalFactor {
  factor: string;
  impact: number;
  confidence: number;
  description: string;
}

interface TrendDataPoint {
  date: string;
  revenue: number;
  forecast: number;
  market_index: number;
}

interface CustomerHealth {
  customer_id: string;
  name: string;
  health_score: number;
  previous_score: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  external_signals: string[];
  expansion_opportunity: number;
  churn_risk: number;
  last_interaction: string;
  contract_value: number;
}

interface SalesIntelligence {
  pipeline_value: number;
  pipeline_growth: number;
  avg_deal_size: number;
  close_rate: number;
  sales_cycle_days: number;
  competitive_wins: number;
  competitive_losses: number;
  market_factors: MarketFactor[];
}

interface MarketFactor {
  factor: string;
  impact_on_sales: number;
  trend: 'positive' | 'negative' | 'neutral';
  description: string;
}

interface BusinessRecommendation {
  id: string;
  type: 'revenue' | 'customer' | 'sales' | 'market';
  priority: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  expected_impact: string;
  confidence: number;
  actionable: boolean;
}

const BusinessIntelligenceLive: React.FC = () => {
  const [activeMetric, setActiveMetric] = useState<string>('revenue');
  const [timeRange, setTimeRange] = useState<string>('30d');

  // Mock data - in production, would come from HubSpot, Gong, Slack, etc.
  const revenueMetrics: RevenueMetrics = {
    current_month: 4200000,
    previous_month: 3800000,
    growth_rate: 10.5,
    forecast_next_month: 4550000,
    external_factors: [
      { factor: 'Market expansion', impact: 0.15, confidence: 0.89, description: 'New market opportunities driving growth' },
      { factor: 'Competitor pricing', impact: -0.08, confidence: 0.76, description: 'Competitor price increases creating advantage' },
      { factor: 'Economic indicators', impact: 0.12, confidence: 0.82, description: 'Positive economic trends supporting sales' }
    ],
    trend_data: [
      { date: '2025-01', revenue: 3200000, forecast: 3100000, market_index: 100 },
      { date: '2025-02', revenue: 3500000, forecast: 3400000, market_index: 105 },
      { date: '2025-03', revenue: 3800000, forecast: 3700000, market_index: 108 },
      { date: '2025-04', revenue: 4200000, forecast: 4000000, market_index: 112 },
      { date: '2025-05', revenue: 0, forecast: 4550000, market_index: 115 }
    ]
  };

  const customerHealth: CustomerHealth[] = [
    {
      customer_id: 'tech_corp',
      name: 'TechCorp',
      health_score: 94,
      previous_score: 78,
      risk_level: 'low',
      external_signals: ['Website activity +340%', 'Executive engagement', 'Expansion signals'],
      expansion_opportunity: 0.92,
      churn_risk: 0.03,
      last_interaction: '2 hours ago',
      contract_value: 250000
    },
    {
      customer_id: 'mega_corp',
      name: 'MegaCorp',
      health_score: 87,
      previous_score: 85,
      risk_level: 'low',
      external_signals: ['Infrastructure modernization', 'AI partner search', 'Budget approval'],
      expansion_opportunity: 0.78,
      churn_risk: 0.08,
      last_interaction: '6 hours ago',
      contract_value: 180000
    },
    {
      customer_id: 'growth_co',
      name: 'GrowthCo',
      health_score: 65,
      previous_score: 72,
      risk_level: 'medium',
      external_signals: ['Reduced engagement', 'Competitor evaluation', 'Budget constraints'],
      expansion_opportunity: 0.34,
      churn_risk: 0.28,
      last_interaction: '3 days ago',
      contract_value: 120000
    },
    {
      customer_id: 'startup_x',
      name: 'StartupX',
      health_score: 45,
      previous_score: 58,
      risk_level: 'high',
      external_signals: ['Funding delays', 'Team changes', 'Usage decline'],
      expansion_opportunity: 0.12,
      churn_risk: 0.65,
      last_interaction: '1 week ago',
      contract_value: 80000
    }
  ];

  const salesIntelligence: SalesIntelligence = {
    pipeline_value: 2800000,
    pipeline_growth: 18.5,
    avg_deal_size: 145000,
    close_rate: 32.5,
    sales_cycle_days: 87,
    competitive_wins: 12,
    competitive_losses: 5,
    market_factors: [
      { factor: 'AI market expansion', impact: 0.23, trend: 'positive', description: 'Growing demand for AI solutions' },
      { factor: 'Economic uncertainty', impact: -0.12, trend: 'negative', description: 'Longer sales cycles due to budget scrutiny' },
      { factor: 'Competitor pricing', impact: 0.15, trend: 'positive', description: 'Competitive advantage from pricing strategy' }
    ]
  };

  const businessRecommendations: BusinessRecommendation[] = [
    {
      id: '1',
      type: 'customer',
      priority: 'critical',
      title: 'Immediate intervention required for StartupX',
      description: 'Customer health score dropped 13 points with high churn risk. Schedule executive call within 24h.',
      expected_impact: 'Potential $80K ARR retention',
      confidence: 0.89,
      actionable: true
    },
    {
      id: '2',
      type: 'revenue',
      priority: 'high',
      title: 'Accelerate TechCorp expansion opportunity',
      description: 'External signals show 340% website activity increase. Strike while engagement is high.',
      expected_impact: 'Potential $150K expansion',
      confidence: 0.94,
      actionable: true
    },
    {
      id: '3',
      type: 'sales',
      priority: 'medium',
      title: 'Leverage competitive pricing advantage',
      description: 'Competitor price increases create 15% sales advantage. Update positioning materials.',
      expected_impact: '12% pipeline acceleration',
      confidence: 0.76,
      actionable: true
    },
    {
      id: '4',
      type: 'market',
      priority: 'medium',
      title: 'Capitalize on AI market expansion',
      description: 'Market expansion creating 23% growth opportunity. Increase marketing spend in AI segment.',
      expected_impact: '18% revenue growth',
      confidence: 0.82,
      actionable: true
    }
  ];

  // Chart configurations
  const revenueChartData = {
    labels: revenueMetrics.trend_data.map(d => d.date),
    datasets: [
      {
        label: 'Actual Revenue',
        data: revenueMetrics.trend_data.map(d => d.revenue || null),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4,
      },
      {
        label: 'Forecast',
        data: revenueMetrics.trend_data.map(d => d.forecast),
        borderColor: 'rgb(168, 85, 247)',
        backgroundColor: 'rgba(168, 85, 247, 0.1)',
        borderDash: [5, 5],
        fill: false,
        tension: 0.4,
      }
    ]
  };

  const customerHealthChartData = {
    labels: customerHealth.map(c => c.name),
    datasets: [
      {
        label: 'Health Score',
        data: customerHealth.map(c => c.health_score),
        backgroundColor: customerHealth.map(c => {
          if (c.health_score >= 80) return 'rgba(34, 197, 94, 0.8)';
          if (c.health_score >= 60) return 'rgba(234, 179, 8, 0.8)';
          return 'rgba(239, 68, 68, 0.8)';
        }),
        borderColor: customerHealth.map(c => {
          if (c.health_score >= 80) return 'rgb(34, 197, 94)';
          if (c.health_score >= 60) return 'rgb(234, 179, 8)';
          return 'rgb(239, 68, 68)';
        }),
        borderWidth: 1,
      }
    ]
  };

  const pipelineChartData = {
    labels: ['Won', 'Lost', 'In Progress'],
    datasets: [
      {
        data: [salesIntelligence.competitive_wins, salesIntelligence.competitive_losses, 25],
        backgroundColor: [
          'rgba(34, 197, 94, 0.8)',
          'rgba(239, 68, 68, 0.8)',
          'rgba(59, 130, 246, 0.8)'
        ],
        borderColor: [
          'rgb(34, 197, 94)',
          'rgb(239, 68, 68)',
          'rgb(59, 130, 246)'
        ],
        borderWidth: 1,
      }
    ]
  };

  // Helper functions
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getHealthColor = (score: number) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low': return 'text-green-400 bg-green-900/20';
      case 'medium': return 'text-yellow-400 bg-yellow-900/20';
      case 'high': return 'text-red-400 bg-red-900/20';
      case 'critical': return 'text-red-400 bg-red-900/40';
      default: return 'text-gray-400 bg-gray-900/20';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'text-red-400 bg-red-900/20';
      case 'high': return 'text-orange-400 bg-orange-900/20';
      case 'medium': return 'text-yellow-400 bg-yellow-900/20';
      case 'low': return 'text-green-400 bg-green-900/20';
      default: return 'text-gray-400 bg-gray-900/20';
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Business Intelligence Live</h2>
          <p className="text-gray-400">Real-time business metrics with external correlation and predictive insights</p>
        </div>
        <div className="flex items-center space-x-4">
          <select 
            value={timeRange} 
            onChange={(e) => setTimeRange(e.target.value)}
            className="bg-gray-800 text-white border border-gray-600 rounded-lg px-3 py-2 text-sm"
          >
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
            <option value="1y">Last Year</option>
          </select>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
            <span className="text-sm text-gray-400">Live data</span>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Monthly Revenue</p>
              <p className="text-2xl font-bold text-white">{formatCurrency(revenueMetrics.current_month)}</p>
            </div>
            <DollarSign className="h-8 w-8 text-green-400" />
          </div>
          <div className="flex items-center mt-2">
            <ArrowUp className="h-4 w-4 text-green-400 mr-1" />
            <span className="text-sm text-green-400">+{revenueMetrics.growth_rate}%</span>
            <span className="text-sm text-gray-400 ml-2">vs last month</span>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Pipeline Value</p>
              <p className="text-2xl font-bold text-white">{formatCurrency(salesIntelligence.pipeline_value)}</p>
            </div>
            <Target className="h-8 w-8 text-blue-400" />
          </div>
          <div className="flex items-center mt-2">
            <ArrowUp className="h-4 w-4 text-green-400 mr-1" />
            <span className="text-sm text-green-400">+{salesIntelligence.pipeline_growth}%</span>
            <span className="text-sm text-gray-400 ml-2">growth</span>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Avg Customer Health</p>
              <p className="text-2xl font-bold text-white">
                {Math.round(customerHealth.reduce((sum, c) => sum + c.health_score, 0) / customerHealth.length)}
              </p>
            </div>
            <Users className="h-8 w-8 text-purple-400" />
          </div>
          <div className="flex items-center mt-2">
            <span className="text-sm text-green-400">
              {customerHealth.filter(c => c.health_score >= 80).length} healthy
            </span>
            <span className="text-sm text-gray-400 ml-2">customers</span>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Close Rate</p>
              <p className="text-2xl font-bold text-white">{salesIntelligence.close_rate}%</p>
            </div>
            <Award className="h-8 w-8 text-orange-400" />
          </div>
          <div className="flex items-center mt-2">
            <span className="text-sm text-blue-400">
              {salesIntelligence.competitive_wins}W/{salesIntelligence.competitive_losses}L
            </span>
            <span className="text-sm text-gray-400 ml-2">vs competitors</span>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue Trends */}
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h3 className="font-semibold text-white mb-4 flex items-center space-x-2">
            <TrendingUp className="h-5 w-5" />
            <span>Revenue Trends & Forecast</span>
          </h3>
          <div className="h-64">
            <Line 
              data={revenueChartData} 
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    labels: { color: 'white' }
                  }
                },
                scales: {
                  x: { 
                    ticks: { color: 'gray' },
                    grid: { color: 'rgba(255,255,255,0.1)' }
                  },
                  y: { 
                    ticks: { color: 'gray' },
                    grid: { color: 'rgba(255,255,255,0.1)' }
                  }
                }
              }}
            />
          </div>
        </div>

        {/* Customer Health */}
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h3 className="font-semibold text-white mb-4 flex items-center space-x-2">
            <Users className="h-5 w-5" />
            <span>Customer Health Scores</span>
          </h3>
          <div className="h-64">
            <Bar 
              data={customerHealthChartData} 
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: { display: false }
                },
                scales: {
                  x: { 
                    ticks: { color: 'gray' },
                    grid: { color: 'rgba(255,255,255,0.1)' }
                  },
                  y: { 
                    ticks: { color: 'gray' },
                    grid: { color: 'rgba(255,255,255,0.1)' },
                    min: 0,
                    max: 100
                  }
                }
              }}
            />
          </div>
        </div>
      </div>

      {/* Detailed Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Customer Health Details */}
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h3 className="font-semibold text-white mb-4 flex items-center space-x-2">
            <Activity className="h-5 w-5" />
            <span>Customer Health Details</span>
          </h3>
          <div className="space-y-3">
            {customerHealth.map((customer) => (
              <div key={customer.customer_id} className="bg-gray-700 rounded-lg p-3">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="font-medium text-white">{customer.name}</span>
                    <span className={`text-xs px-2 py-1 rounded ${getRiskColor(customer.risk_level)}`}>
                      {customer.risk_level}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`text-sm font-medium ${getHealthColor(customer.health_score)}`}>
                      {customer.health_score}
                    </span>
                    <span className="text-xs text-gray-400">
                      {customer.health_score > customer.previous_score ? '+' : ''}
                      {customer.health_score - customer.previous_score}
                    </span>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4 text-xs text-gray-400 mb-2">
                  <div>Contract: {formatCurrency(customer.contract_value)}</div>
                  <div>Last contact: {customer.last_interaction}</div>
                  <div>Expansion: {Math.round(customer.expansion_opportunity * 100)}%</div>
                  <div>Churn risk: {Math.round(customer.churn_risk * 100)}%</div>
                </div>
                
                <div className="flex flex-wrap gap-1">
                  {customer.external_signals.map((signal, idx) => (
                    <span key={idx} className="text-xs bg-blue-600 text-white px-2 py-1 rounded">
                      {signal}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Business Recommendations */}
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h3 className="font-semibold text-white mb-4 flex items-center space-x-2">
            <Zap className="h-5 w-5" />
            <span>Actionable Recommendations</span>
          </h3>
          <div className="space-y-3">
            {businessRecommendations.map((rec) => (
              <div key={rec.id} className="bg-gray-700 rounded-lg p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className={`text-xs px-2 py-1 rounded ${getPriorityColor(rec.priority)}`}>
                    {rec.priority}
                  </span>
                  <span className="text-xs text-gray-400">
                    {Math.round(rec.confidence * 100)}% confidence
                  </span>
                </div>
                
                <h4 className="font-medium text-white text-sm mb-1">{rec.title}</h4>
                <p className="text-sm text-gray-300 mb-2">{rec.description}</p>
                
                <div className="flex items-center justify-between">
                  <span className="text-xs text-green-400">{rec.expected_impact}</span>
                  {rec.actionable && (
                    <button className="text-xs bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700">
                      Take Action
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* External Factors */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h3 className="font-semibold text-white mb-4 flex items-center space-x-2">
          <Eye className="h-5 w-5" />
          <span>External Factors Impact</span>
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {revenueMetrics.external_factors.map((factor, idx) => (
            <div key={idx} className="bg-gray-700 rounded-lg p-3">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-white">{factor.factor}</span>
                <span className={`text-sm ${factor.impact > 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {factor.impact > 0 ? '+' : ''}{Math.round(factor.impact * 100)}%
                </span>
              </div>
              <p className="text-sm text-gray-300 mb-2">{factor.description}</p>
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-400">
                  Confidence: {Math.round(factor.confidence * 100)}%
                </span>
                <div className={`w-2 h-2 rounded-full ${factor.impact > 0 ? 'bg-green-400' : 'bg-red-400'}`}></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default BusinessIntelligenceLive; 
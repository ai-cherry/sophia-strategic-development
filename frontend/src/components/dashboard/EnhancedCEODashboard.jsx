/**
 * CEO Dashboard Component
 * Comprehensive executive dashboard with glassmorphism design
 */

import React, { useState, useEffect } from 'react';
import { 
  DollarSign, 
  Users, 
  TrendingUp, 
  Target, 
  AlertTriangle, 
  Calendar,
  Search,
  RefreshCw,
  Filter,
  BarChart3,
  PieChart,
  Activity
} from 'lucide-react';
import KPICard, { RevenueCard, MetricCard, AlertCard } from './KPICard.jsx';
import ExecutiveChart, { RevenueChart, PerformanceChart, MarketShareChart } from './ExecutiveChart.jsx';
import { glassmorphism, layout, typography, animations } from '../lib/design-system.js';

// Mock data for demonstration
const mockKPIData = [
  {
    title: 'Total Revenue',
    value: '$2.4M',
    trend: 'up',
    trendValue: '+12.5%',
    description: 'Trending up this month',
    status: 'success',
    icon: DollarSign
  },
  {
    title: 'Active Deals',
    value: '156',
    trend: 'up',
    trendValue: '+8.2%',
    description: 'Strong pipeline growth',
    status: 'success',
    icon: Target
  },
  {
    title: 'Team Efficiency',
    value: '94%',
    trend: 'up',
    trendValue: '+2.1%',
    description: 'Above target performance',
    status: 'success',
    icon: Activity
  },
  {
    title: 'Customer Acquisition',
    value: '1,234',
    trend: 'down',
    trendValue: '-5.3%',
    description: 'Needs attention this quarter',
    status: 'warning',
    icon: Users
  }
];

const mockRevenueData = [
  { name: 'Jan', revenue: 2100, projected: 2000 },
  { name: 'Feb', revenue: 2300, projected: 2200 },
  { name: 'Mar', revenue: 2800, projected: 2400 },
  { name: 'Apr', revenue: 2600, projected: 2600 },
  { name: 'May', revenue: 3100, projected: 2800 },
  { name: 'Jun', revenue: 2900, projected: 3000 }
];

const mockTeamData = [
  { name: 'Sales', performance: 94, target: 90 },
  { name: 'Engineering', performance: 88, target: 85 },
  { name: 'Marketing', performance: 96, target: 92 },
  { name: 'Customer Success', performance: 91, target: 88 },
  { name: 'Operations', performance: 87, target: 85 }
];

const mockMarketData = [
  { name: 'Sophia AI', value: 35, color: '#6366f1' },
  { name: 'EliseAI', value: 28, color: '#8b5cf6' },
  { name: 'Competitor C', value: 20, color: '#06b6d4' },
  { name: 'Others', value: 17, color: '#10b981' }
];

const mockAlerts = [
  {
    id: 1,
    type: 'success',
    title: 'Q2 Revenue Target Exceeded',
    message: 'Revenue has exceeded Q2 targets by 12.5%',
    timestamp: '2 hours ago'
  },
  {
    id: 2,
    type: 'warning',
    title: 'Customer Acquisition Declining',
    message: 'CAC has increased 15% over last month',
    timestamp: '4 hours ago'
  },
  {
    id: 3,
    type: 'info',
    title: 'New Market Opportunity',
    message: 'NMHC conference presents expansion opportunity',
    timestamp: '1 day ago'
  }
];

const CEODashboard = () => {
  const [selectedTimeRange, setSelectedTimeRange] = useState('30d');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Time range options
  const timeRanges = [
    { value: '7d', label: '7 Days' },
    { value: '30d', label: '30 Days' },
    { value: '90d', label: '90 Days' },
    { value: '1y', label: '1 Year' }
  ];

  // Handle refresh
  const handleRefresh = async () => {
    setIsRefreshing(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    setIsRefreshing(false);
  };

  // Dashboard header
  const renderHeader = () => (
    <div className="mb-8">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
        {/* Title and subtitle */}
        <div>
          <h1 
            className="text-3xl font-bold text-white tracking-tight mb-2"
            style={typography.getHeadingStyles(1)}
          >
            CEO Dashboard
          </h1>
          <p 
            className="text-lg text-white/70"
            style={typography.getTextStyles('lead')}
          >
            Executive Command Center
          </p>
        </div>

        {/* Controls */}
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Time range selector */}
          <div className="flex bg-white/5 backdrop-blur-md rounded-lg p-1 border border-white/10">
            {timeRanges.map((range) => (
              <button
                key={range.value}
                onClick={() => setSelectedTimeRange(range.value)}
                className={`
                  px-4 py-2 rounded-md text-sm font-medium transition-all duration-200
                  ${selectedTimeRange === range.value 
                    ? 'bg-white/20 text-white border border-white/30' 
                    : 'text-white/70 hover:text-white hover:bg-white/10'
                  }
                `}
              >
                {range.label}
              </button>
            ))}
          </div>

          {/* Search and refresh */}
          <div className="flex gap-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/50" size={18} />
              <input
                type="text"
                placeholder="Search across all executive data..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="
                  pl-10 pr-4 py-2 w-64 rounded-lg backdrop-blur-md bg-white/10 
                  border border-white/20 text-white placeholder-white/50
                  focus:outline-none focus:border-white/40 focus:bg-white/15
                  transition-all duration-200
                "
              />
            </div>
            <button
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="
                p-2 rounded-lg backdrop-blur-md bg-white/10 border border-white/20
                text-white hover:bg-white/20 transition-all duration-200
                disabled:opacity-50 disabled:cursor-not-allowed
              "
            >
              <RefreshCw 
                className={`${isRefreshing ? 'animate-spin' : ''}`} 
                size={18} 
              />
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  // KPI cards grid
  const renderKPIGrid = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {mockKPIData.map((kpi, index) => (
        <KPICard
          key={index}
          title={kpi.title}
          value={kpi.value}
          trend={kpi.trend}
          trendValue={kpi.trendValue}
          description={kpi.description}
          status={kpi.status}
          icon={kpi.icon}
          onClick={() => console.log(`Clicked ${kpi.title}`)}
        />
      ))}
    </div>
  );

  // Charts section
  const renderCharts = () => (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      {/* Revenue chart */}
      <RevenueChart
        data={mockRevenueData}
        dataKeys={['revenue', 'projected']}
        title="Revenue Trends"
        subtitle="Actual vs Projected Revenue"
        height={300}
        valueFormatter={(value) => `$${(value / 1000).toFixed(1)}k`}
      />

      {/* Team performance chart */}
      <PerformanceChart
        data={mockTeamData}
        dataKeys={['performance', 'target']}
        title="Team Performance"
        subtitle="Current vs Target Performance"
        height={300}
        valueFormatter={(value) => `${value}%`}
      />
    </div>
  );

  // Market share and alerts section
  const renderBottomSection = () => (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Market share chart */}
      <div className="lg:col-span-1">
        <MarketShareChart
          data={mockMarketData}
          dataKeys={['value']}
          title="Market Share"
          subtitle="Competitive Analysis"
          height={250}
          valueFormatter={(value) => `${value}%`}
        />
      </div>

      {/* Strategic alerts */}
      <div className="lg:col-span-2">
        <div 
          className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-xl p-6"
          style={glassmorphism.getStyles(0.05, 15)}
        >
          <h3 
            className="text-lg font-semibold text-white mb-4"
            style={typography.getHeadingStyles(3)}
          >
            Strategic Alerts
          </h3>
          <div className="space-y-4">
            {mockAlerts.map((alert) => (
              <div
                key={alert.id}
                className="flex items-start space-x-3 p-4 rounded-lg backdrop-blur-md bg-white/5 border border-white/10"
              >
                <div className={`
                  p-2 rounded-lg
                  ${alert.type === 'success' ? 'bg-green-500/20 text-green-400' : ''}
                  ${alert.type === 'warning' ? 'bg-yellow-500/20 text-yellow-400' : ''}
                  ${alert.type === 'info' ? 'bg-blue-500/20 text-blue-400' : ''}
                `}>
                  {alert.type === 'success' && <TrendingUp size={16} />}
                  {alert.type === 'warning' && <AlertTriangle size={16} />}
                  {alert.type === 'info' && <BarChart3 size={16} />}
                </div>
                <div className="flex-1">
                  <h4 className="text-sm font-medium text-white mb-1">
                    {alert.title}
                  </h4>
                  <p className="text-sm text-white/70 mb-2">
                    {alert.message}
                  </p>
                  <span className="text-xs text-white/50">
                    {alert.timestamp}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {renderHeader()}
        {renderKPIGrid()}
        {renderCharts()}
        {renderBottomSection()}
      </div>
    </div>
  );
};

export default CEODashboard;


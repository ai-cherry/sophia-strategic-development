import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../../../services/apiClient';
import { useChatInterface } from '../../../hooks/useChatInterface';
import { useBackendConnection } from '../../../hooks/useBackendConnection';
import ExecutiveKPIGrid from './components/ExecutiveKPIGrid';

// KPI Card Component
const KPICard = ({ title, value, target, change, trend, icon, color = 'purple' }) => {
  const formatValue = (val) => {
    if (val >= 1000000) return `$${(val / 1000000).toFixed(1)}M`;
    if (val >= 1000) return `${(val / 1000).toFixed(0)}K`;
    return val?.toLocaleString();
  };

  const trendIcon = trend === 'up' ? '↗️' : trend === 'down' ? '↘️' : '→';
  const changeColor = change > 0 ? 'text-green-400' : change < 0 ? 'text-red-400' : 'text-gray-400';

  return (
    <div className={`bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-${color}-500 transition-all duration-300 hover:shadow-lg hover:shadow-${color}-500/20`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`p-2 bg-${color}-500/20 rounded-lg`}>
            <span className="text-2xl">{icon}</span>
          </div>
          <h3 className="text-gray-300 text-sm font-medium">{title}</h3>
        </div>
        <span className="text-lg">{trendIcon}</span>
      </div>
      
      <div className="space-y-2">
        <div className="flex items-baseline space-x-2">
          <span className="text-3xl font-bold text-white">{formatValue(value)}</span>
          <span className={`text-sm font-medium ${changeColor}`}>
            {change > 0 ? '+' : ''}{change}%
          </span>
        </div>
        
        {target && (
          <div className="flex items-center space-x-2">
            <span className="text-xs text-gray-400">Target:</span>
            <span className="text-xs text-gray-300">{formatValue(target)}</span>
            <div className="flex-1 bg-gray-700 rounded-full h-1.5">
              <div 
                className={`bg-${color}-500 h-1.5 rounded-full transition-all duration-500`}
                style={{ width: `${Math.min((value / target) * 100, 100)}%` }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Team Performance Card
const TeamPerformanceCard = ({ department, performance, target, trend }) => {
  const percentage = Math.round((performance / target) * 100);
  const isAboveTarget = performance >= target;
  
  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 hover:border-blue-500 transition-all duration-300">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-white font-medium capitalize">{department}</h4>
        <span className={`text-sm ${isAboveTarget ? 'text-green-400' : 'text-yellow-400'}`}>
          {performance}%
        </span>
      </div>
      
      <div className="space-y-2">
        <div className="flex justify-between text-xs text-gray-400">
          <span>Target: {target}%</span>
          <span>{percentage}% of target</span>
        </div>
        
        <div className="bg-gray-700 rounded-full h-2">
          <div 
            className={`h-2 rounded-full transition-all duration-500 ${
              isAboveTarget ? 'bg-green-500' : 'bg-yellow-500'
            }`}
            style={{ width: `${Math.min(percentage, 100)}%` }}
          />
        </div>
      </div>
    </div>
  );
};

// Strategic Alert Component
const StrategicAlert = ({ alert }) => {
  const alertColors = {
    success: 'border-green-500 bg-green-500/10',
    warning: 'border-yellow-500 bg-yellow-500/10',
    info: 'border-blue-500 bg-blue-500/10',
    error: 'border-red-500 bg-red-500/10'
  };

  const alertIcons = {
    success: '✅',
    warning: '⚠️',
    info: 'ℹ️',
    error: '❌'
  };

  return (
    <div className={`p-4 rounded-lg border ${alertColors[alert.type]} hover:shadow-lg transition-all duration-300`}>
      <div className="flex items-start space-x-3">
        <span className="text-lg">{alertIcons[alert.type]}</span>
        <div className="flex-1">
          <h4 className="text-white font-medium mb-1">{alert.title}</h4>
          <p className="text-gray-300 text-sm mb-2">{alert.message}</p>
          <span className="text-xs text-gray-400">
            {new Date(alert.timestamp).toLocaleString()}
          </span>
        </div>
      </div>
    </div>
  );
};

// Market Share Chart Component
const MarketShareChart = ({ data }) => {
  const total = data.reduce((sum, item) => sum + item.value, 0);
  
  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <h3 className="text-white text-lg font-semibold mb-4">Market Share Analysis</h3>
      
      <div className="space-y-4">
        {data.map((item, index) => {
          const percentage = ((item.value / total) * 100).toFixed(1);
          return (
            <div key={index} className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-gray-300">{item.name}</span>
                <span className="text-white font-medium">{percentage}%</span>
              </div>
              <div className="bg-gray-700 rounded-full h-2">
                <div 
                  className="h-2 rounded-full transition-all duration-500"
                  style={{ 
                    width: `${percentage}%`,
                    backgroundColor: item.color 
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// Revenue Chart Component
const RevenueChart = ({ data }) => {
  const maxValue = Math.max(...data.projections.map(p => Math.max(p.actual || 0, p.projected)));
  
  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <h3 className="text-white text-lg font-semibold mb-4">Revenue Trends</h3>
      
      <div className="space-y-4">
        {data.projections.map((item, index) => (
          <div key={index} className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-gray-300">{item.month}</span>
              <div className="flex space-x-4">
                {item.actual && (
                  <span className="text-green-400 text-sm">
                    Actual: ${(item.actual / 1000000).toFixed(1)}M
                  </span>
                )}
                <span className="text-blue-400 text-sm">
                  Target: ${(item.projected / 1000000).toFixed(1)}M
                </span>
              </div>
            </div>
            
            <div className="relative bg-gray-700 rounded-full h-3">
              {item.actual && (
                <div 
                  className="absolute bg-green-500 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${(item.actual / maxValue) * 100}%` }}
                />
              )}
              <div 
                className="absolute bg-blue-500/50 h-3 rounded-full transition-all duration-500"
                style={{ width: `${(item.projected / maxValue) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Main CEO Dashboard Component
const CEODashboardLayout = () => {
  const navigate = useNavigate();
  const { connectionStatus } = useBackendConnection();
  const { messages, sendMessage, isConnected } = useChatInterface();
  
  const [timeRange, setTimeRange] = useState('30d');
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [chatInput, setChatInput] = useState('');
  
  // Dashboard data state
  const [kpiData, setKpiData] = useState(null);
  const [teamData, setTeamData] = useState(null);
  const [marketData, setMarketData] = useState(null);
  const [alertsData, setAlertsData] = useState([]);

  // Time range options
  const timeRangeOptions = [
    { value: '7d', label: '7 Days' },
    { value: '30d', label: '30 Days' },
    { value: '90d', label: '90 Days' },
    { value: '1y', label: '1 Year' }
  ];

  // Mock data for demonstration
  const mockKPIData = [
    {
      title: 'Total Revenue',
      value: 2400000,
      target: 2500000,
      change: 12.5,
      trend: 'up',
      icon: '💰',
      color: 'green'
    },
    {
      title: 'Active Deals',
      value: 156,
      target: 150,
      change: 8.2,
      trend: 'up',
      icon: '🎯',
      color: 'blue'
    },
    {
      title: 'Team Efficiency',
      value: 94,
      target: 90,
      change: 2.1,
      trend: 'up',
      icon: '⚡',
      color: 'purple'
    },
    {
      title: 'Customer Satisfaction',
      value: 4.8,
      target: 4.5,
      change: 5.2,
      trend: 'up',
      icon: '⭐',
      color: 'yellow'
    }
  ];

  const mockTeamData = [
    { department: 'sales', performance: 105, target: 100, trend: 'up' },
    { department: 'marketing', performance: 92, target: 95, trend: 'down' },
    { department: 'engineering', performance: 98, target: 95, trend: 'up' },
    { department: 'support', performance: 87, target: 90, trend: 'down' }
  ];

  const mockMarketData = [
    { name: 'Our Company', value: 35, color: '#8B5CF6' },
    { name: 'Competitor A', value: 28, color: '#EF4444' },
    { name: 'Competitor B', value: 22, color: '#F59E0B' },
    { name: 'Others', value: 15, color: '#6B7280' }
  ];

  const mockAlertsData = [
    {
      type: 'success',
      title: 'Q4 Revenue Target Achieved',
      message: 'Exceeded quarterly revenue target by 12.5%',
      timestamp: new Date().toISOString()
    },
    {
      type: 'warning',
      title: 'Marketing Performance Below Target',
      message: 'Marketing team performance at 92% of target',
      timestamp: new Date().toISOString()
    },
    {
      type: 'info',
      title: 'New Market Opportunity',
      message: 'Potential expansion opportunity in European market',
      timestamp: new Date().toISOString()
    }
  ];

  const mockRevenueData = {
    projections: [
      { month: 'Jan', actual: 2100000, projected: 2000000 },
      { month: 'Feb', actual: 2300000, projected: 2200000 },
      { month: 'Mar', actual: 2400000, projected: 2300000 },
      { month: 'Apr', actual: null, projected: 2500000 },
      { month: 'May', actual: null, projected: 2600000 },
      { month: 'Jun', actual: null, projected: 2700000 }
    ]
  };

  useEffect(() => {
    // Simulate loading
    setTimeout(() => {
      setKpiData(mockKPIData);
      setTeamData(mockTeamData);
      setMarketData(mockMarketData);
      setAlertsData(mockAlertsData);
      setLoading(false);
    }, 1000);
  }, [timeRange]);

  const handleTimeRangeChange = (newRange) => {
    setTimeRange(newRange);
    setLoading(true);
  };

  const handleSearch = (query) => {
    console.log('Searching for:', query);
    // Implement search functionality
  };

  const handleRefresh = () => {
    setLoading(true);
    // Simulate refresh
    setTimeout(() => setLoading(false), 1000);
  };

  const handleSendMessage = () => {
    if (chatInput.trim()) {
      sendMessage(chatInput);
      setChatInput('');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="animate-pulse space-y-8">
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="bg-gray-800 rounded-xl p-6 h-32"></div>
              ))}
            </div>
            <div className="grid gap-6 lg:grid-cols-2">
              <div className="bg-gray-800 rounded-xl h-96"></div>
              <div className="bg-gray-800 rounded-xl h-96"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Executive Header */}
      <div className="sticky top-0 z-20 bg-gray-900/95 backdrop-blur-sm border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center">
                  <span className="text-2xl">👑</span>
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-white">CEO Dashboard</h1>
                  <p className="text-gray-400">Executive Command Center</p>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-6">
              {/* Time Range Filters */}
              <div className="flex space-x-2">
                {timeRangeOptions.map((option) => (
                  <button
                    key={option.value}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                      timeRange === option.value
                        ? 'bg-purple-600 text-white'
                        : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                    }`}
                    onClick={() => handleTimeRangeChange(option.value)}
                  >
                    {option.label}
                  </button>
                ))}
              </div>

              {/* Refresh Button */}
              <button
                className="p-2 bg-gray-800 rounded-lg hover:bg-gray-700 transition-colors"
                onClick={handleRefresh}
              >
                <span className="text-xl">🔄</span>
              </button>

              {/* Connection Status */}
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${
                  connectionStatus === 'connected' ? 'bg-green-500' : 'bg-red-500'
                }`}></div>
                <span className="text-sm text-gray-400">
                  {connectionStatus === 'connected' ? 'Connected' : 'Offline'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Executive Search */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6">
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center">
              <span className="text-xl">🔍</span>
            </div>
            <div className="flex-1 relative">
              <input
                type="text"
                placeholder="Search across all executive data..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch(searchQuery)}
                className="w-full bg-transparent border-0 text-white text-lg placeholder-gray-400 focus:outline-none"
              />
              <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-purple-500 to-transparent"></div>
            </div>
            <button
              className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
              onClick={() => handleSearch(searchQuery)}
            >
              Search
            </button>
          </div>
        </div>
      </div>

      {/* Main Dashboard Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Executive KPI Grid */}
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            {kpiData?.map((kpi, index) => (
              <KPICard key={index} {...kpi} />
            ))}
          </div>

          {/* Main Analytics Grid */}
          <div className="grid gap-8 lg:grid-cols-3">
            {/* Left Column - 2/3 width */}
            <div className="lg:col-span-2 space-y-8">
              {/* Revenue Projections */}
              <RevenueChart data={mockRevenueData} />

              {/* Team Performance */}
              <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
                <h3 className="text-white text-lg font-semibold mb-4">Team Performance</h3>
                <div className="grid gap-4 md:grid-cols-2">
                  {teamData?.map((team, index) => (
                    <TeamPerformanceCard key={index} {...team} />
                  ))}
                </div>
              </div>
            </div>

            {/* Right Column - 1/3 width */}
            <div className="space-y-8">
              {/* Market Analytics */}
              <MarketShareChart data={marketData} />

              {/* Strategic Alerts */}
              <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
                <h3 className="text-white text-lg font-semibold mb-4">Strategic Alerts</h3>
                <div className="space-y-4">
                  {alertsData?.map((alert, index) => (
                    <StrategicAlert key={index} alert={alert} />
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Executive Chat Interface */}
          <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
            <h3 className="text-white text-lg font-semibold mb-4">Executive Assistant</h3>
            
            <div className="space-y-4">
              {/* Messages */}
              <div className="h-64 bg-gray-900 rounded-lg p-4 overflow-y-auto">
                {messages.length === 0 ? (
                  <div className="text-gray-400 text-center py-8">
                    Ask me anything about your business metrics, team performance, or strategic insights.
                  </div>
                ) : (
                  <div className="space-y-3">
                    {messages.map((message, index) => (
                      <div key={index} className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                          message.sender === 'user' 
                            ? 'bg-purple-600 text-white' 
                            : 'bg-gray-700 text-gray-100'
                        }`}>
                          {message.text}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Input */}
              <div className="flex space-x-4">
                <input
                  type="text"
                  placeholder="Ask about metrics, trends, or strategic insights..."
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  className="flex-1 bg-gray-900 border border-gray-600 rounded-lg px-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:border-purple-500"
                />
                <button
                  onClick={handleSendMessage}
                  disabled={!chatInput.trim() || !isConnected}
                  className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Send
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CEODashboardLayout;


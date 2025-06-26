import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../../../services/apiClient';
import { useChatInterface } from '../../../hooks/useChatInterface';
import { useBackendConnection } from '../../../hooks/useBackendConnection';

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
<<<<<<< HEAD
    <div className={`bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-${color}-500 transition-all duration-300 hover:shadow-lg hover:shadow-${color}-500/20`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`p-2 bg-${color}-500/20 rounded-lg`}>
            <span className="text-2xl">{icon}</span>
=======
    <div className="min-h-screen">
      {/* Executive Header */}
      <div className="sticky top-0 z-20 executive-header">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-4">
                <div className="executive-icon-lg gradient-purple-blue">
                  <i className="fas fa-crown"></i>
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-white">CEO Dashboard</h1>
                  <p className="text-executive-secondary">Executive Command Center</p>
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
                        ? 'time-range-active'
                        : 'time-range-inactive hover:bg-opacity-80'
                    }`}
                    onClick={() => handleTimeRangeChange(option.value)}
                    disabled={isInitialLoading || refreshing}
                  >
                    {option.label}
                  </button>
                ))}
              </div>

              {/* Refresh Button */}
              <button
                className="executive-icon hover-scale hover-glow"
                onClick={handleRefresh}
                disabled={refreshing}
                style={{ background: 'rgba(75, 85, 99, 0.5)' }}
              >
                {refreshing ? (
                  <i className="fas fa-spinner fa-spin"></i>
                ) : (
                  <i className="fas fa-sync-alt"></i>
                )}
              </button>

              {/* Connection Status */}
              <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-2">
                  <div className={`w-3 h-3 rounded-full pulse-dot ${
                    isHealthy ? 'status-online' : 'status-offline'
                  }`}></div>
                  <span className="text-sm text-executive-secondary">
                    {isHealthy ? 'Connected' : 'Offline'}
                  </span>
                </div>
              </div>
            </div>
>>>>>>> 28336639693e9537cc10d264c0726f97d138a7b4
          </div>
          <h3 className="text-gray-300 text-sm font-medium">{title}</h3>
        </div>
        <span className="text-lg">{trendIcon}</span>
      </div>
<<<<<<< HEAD
      
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
=======

      {/* Connection Error Alert */}
      {connectionError && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6">
          <div className="glassmorphism-card alert-error p-4 mb-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <i className="fas fa-exclamation-triangle text-red-500"></i>
                <span className="text-executive-secondary">
                  Connection issue detected. Some data may be outdated.
                </span>
              </div>
              <button
                className="btn-executive-secondary"
                onClick={handleRefresh}
              >
                <i className="fas fa-redo mr-2"></i>
                Retry
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Executive Search */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6">
        <div className="glassmorphism-card p-6">
          <div className="flex items-center space-x-4">
            <div className="executive-icon gradient-purple-blue">
              <i className="fas fa-search"></i>
            </div>
            <div className="flex-1 relative">
              <input
                type="text"
                placeholder="Search across all executive data..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch(searchQuery)}
                className="w-full bg-transparent border-0 text-white text-lg placeholder-executive-muted focus:outline-none"
              />
              <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-purple-500 to-transparent"></div>
            </div>
            <button
              className="btn-executive-primary"
              onClick={() => handleSearch(searchQuery)}
            >
              <i className="fas fa-search mr-2"></i>
              Search
            </button>
          </div>
        </div>
      </div>

      {/* Main Dashboard Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {isInitialLoading ? (
          // Executive Loading State
          <div className="space-y-8">
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="glassmorphism-card p-6">
                  <div className="flex items-center justify-between">
                    <div className="space-y-3">
                      <div className="skeleton h-4 w-20"></div>
                      <div className="skeleton h-8 w-32"></div>
                      <div className="skeleton h-3 w-24"></div>
                    </div>
                    <div className="skeleton h-12 w-12 rounded-full"></div>
                  </div>
                </div>
              ))}
            </div>
            <div className="grid gap-6 lg:grid-cols-2">
              <div className="glassmorphism-card skeleton" style={{ height: '400px' }}></div>
              <div className="glassmorphism-card skeleton" style={{ height: '400px' }}></div>
            </div>
          </div>
        ) : (
          // Executive Dashboard Content
          <div className="space-y-8">
            {/* Executive KPI Grid */}
            <ExecutiveKPIGrid
              metrics={ceoMetrics}
              loading={metricsLoading}
              error={metricsError}
              timeRange={timeRange}
            />

            {/* Main Analytics Grid */}
            <div className="grid gap-8 lg:grid-cols-3">
              {/* Left Column - 2/3 width */}
              <div className="lg:col-span-2 space-y-8">
                {/* Revenue Projections */}
                <RevenueProjectionChart
                  data={ceoMetrics?.revenueData}
                  loading={metricsLoading}
                  error={metricsError}
                  timeRange={timeRange}
                />

                {/* Team Performance */}
                <TeamPerformancePanel
                  data={teamData}
                  loading={teamLoading}
                  error={teamError}
                  timeRange={timeRange}
                />
              </div>

              {/* Right Column - 1/3 width */}
              <div className="space-y-8">
                {/* Market Analytics */}
                <MarketAnalyticsChart
                  data={marketData}
                  loading={marketLoading}
                  error={marketError}
                  timeRange={timeRange}
                />

                {/* Strategic Alerts */}
                <StrategicAlertsPanel
                  alerts={ceoMetrics?.alerts}
                  loading={metricsLoading}
                  error={metricsError}
                />
              </div>
            </div>

            {/* Executive Chat Interface */}
            <ExecutiveChatInterface
              messages={messages}
              onSendMessage={sendMessage}
              isConnected={chatConnected}
              connectionStatus={wsStatus}
            />
>>>>>>> 28336639693e9537cc10d264c0726f97d138a7b4
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
  const [revenueData, setRevenueData] = useState(null);

  // Load dashboard data
  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [kpis, team, market, alerts, revenue] = await Promise.all([
        api.getCEOKPIs(timeRange),
        api.getTeamPerformance(timeRange),
        api.getMarketData(),
        api.getStrategicAlerts(),
        api.getRevenueProjections()
      ]);
      
      setKpiData(kpis);
      setTeamData(team);
      setMarketData(market);
      setAlertsData(alerts);
      setRevenueData(revenue);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, [timeRange]);

  const handleChatSubmit = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;
    
    try {
      await sendMessage(chatInput);
      setChatInput('');
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    
    // Implement search functionality
    console.log('Searching for:', searchQuery);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <p className="text-gray-300">Loading Executive Dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/')}
              className="flex items-center space-x-2 text-gray-300 hover:text-white transition-colors"
            >
              <span>←</span>
              <span>Back to Home</span>
            </button>
            <div className="h-6 w-px bg-gray-600"></div>
            <h1 className="text-2xl font-bold">CEO Dashboard</h1>
            <span className="text-sm text-gray-400">Executive Command Center</span>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-xs ${
              connectionStatus.connected 
                ? 'bg-green-500/20 text-green-400' 
                : 'bg-red-500/20 text-red-400'
            }`}>
              <div className={`w-2 h-2 rounded-full ${
                connectionStatus.connected ? 'bg-green-400' : 'bg-red-400'
              }`}></div>
              <span>{connectionStatus.connected ? 'Online' : 'Offline'}</span>
            </div>
            
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-1 text-sm focus:outline-none focus:border-purple-500"
            >
              <option value="7d">7 Days</option>
              <option value="30d">30 Days</option>
              <option value="90d">90 Days</option>
              <option value="1y">1 Year</option>
            </select>
            
            <button
              onClick={loadDashboardData}
              className="bg-purple-600 hover:bg-purple-700 px-4 py-1 rounded-lg text-sm transition-colors"
            >
              Refresh
            </button>
          </div>
        </div>
        
        {/* Search Bar */}
        <form onSubmit={handleSearch} className="mt-4">
          <div className="flex space-x-2">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search across all executive data..."
              className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:border-purple-500"
            />
            <button
              type="submit"
              className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-lg transition-colors"
            >
              Search
            </button>
          </div>
        </form>
      </header>

      {/* Main Content */}
      <main className="p-6 space-y-6">
        {/* KPI Grid */}
        {kpiData && (
          <section>
            <h2 className="text-xl font-semibold mb-4">Executive KPIs</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <KPICard
                title="Revenue"
                value={kpiData.revenue.current}
                target={kpiData.revenue.target}
                change={kpiData.revenue.change}
                trend={kpiData.revenue.trend}
                icon="💰"
                color="green"
              />
              <KPICard
                title="Active Deals"
                value={kpiData.deals.current}
                target={kpiData.deals.target}
                change={kpiData.deals.change}
                trend={kpiData.deals.trend}
                icon="🤝"
                color="blue"
              />
              <KPICard
                title="Efficiency"
                value={kpiData.efficiency.current}
                target={kpiData.efficiency.target}
                change={kpiData.efficiency.change}
                trend={kpiData.efficiency.trend}
                icon="⚡"
                color="yellow"
              />
              <KPICard
                title="ARR"
                value={kpiData.arr.current}
                target={kpiData.arr.target}
                change={kpiData.arr.change}
                trend={kpiData.arr.trend}
                icon="📈"
                color="purple"
              />
            </div>
          </section>
        )}

        {/* Charts and Analytics */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Revenue Chart */}
          {revenueData && (
            <RevenueChart data={revenueData} />
          )}
          
          {/* Market Share */}
          {marketData && (
            <MarketShareChart data={marketData.marketShare} />
          )}
        </div>

        {/* Team Performance */}
        {teamData && (
          <section>
            <h2 className="text-xl font-semibold mb-4">Team Performance</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              {Object.entries(teamData).map(([dept, data]) => (
                <TeamPerformanceCard
                  key={dept}
                  department={dept}
                  performance={data.performance}
                  target={data.target}
                  trend={data.trend}
                />
              ))}
            </div>
          </section>
        )}

        {/* Strategic Alerts */}
        <section>
          <h2 className="text-xl font-semibold mb-4">Strategic Alerts</h2>
          <div className="space-y-4">
            {alertsData.length > 0 ? (
              alertsData.map(alert => (
                <StrategicAlert key={alert.id} alert={alert} />
              ))
            ) : (
              <div className="bg-gray-800 rounded-lg p-6 text-center">
                <span className="text-2xl mb-2 block">⚠️</span>
                <p className="text-gray-400">No alerts at this time</p>
              </div>
            )}
          </div>
        </section>

        {/* Executive AI Assistant */}
        <section>
          <h2 className="text-xl font-semibold mb-4">Executive AI Assistant</h2>
          <div className="bg-gray-800 rounded-xl border border-gray-700">
            {/* Chat Messages */}
            <div className="p-6 space-y-4 max-h-64 overflow-y-auto">
              {messages.length > 0 ? (
                messages.map((message, index) => (
                  <div key={index} className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      message.sender === 'user' 
                        ? 'bg-purple-600 text-white' 
                        : 'bg-gray-700 text-gray-100'
                    }`}>
                      <p className="text-sm">{message.text}</p>
                      <span className="text-xs opacity-70">
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center text-gray-400">
                  <span className="text-2xl mb-2 block">🤖</span>
                  <p>No messages yet. Ask me about your business metrics!</p>
                </div>
              )}
            </div>
            
            {/* Chat Input */}
            <form onSubmit={handleChatSubmit} className="border-t border-gray-700 p-4">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder="Ask about revenue, team performance, market trends..."
                  className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:border-purple-500"
                />
                <button
                  type="submit"
                  disabled={!chatInput.trim()}
                  className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 px-4 py-2 rounded-lg transition-colors"
                >
                  Send
                </button>
              </div>
              
              <div className="flex items-center justify-between mt-2">
                <div className="flex space-x-2">
                  <button
                    type="button"
                    onClick={() => setChatInput('What is our current revenue performance?')}
                    className="text-xs bg-gray-700 hover:bg-gray-600 px-2 py-1 rounded transition-colors"
                  >
                    Ask about revenue
                  </button>
                  <button
                    type="button"
                    onClick={() => setChatInput('How is our team performing?')}
                    className="text-xs bg-gray-700 hover:bg-gray-600 px-2 py-1 rounded transition-colors"
                  >
                    Team performance
                  </button>
                </div>
                
                <span className={`text-xs ${isConnected ? 'text-green-400' : 'text-red-400'}`}>
                  Chat {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
            </form>
          </div>
        </section>
      </main>
    </div>
  );
};

export default CEODashboardLayout;


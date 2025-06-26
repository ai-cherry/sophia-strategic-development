import React, { useState, useEffect } from 'react';
import { useBackendConnection } from '../../../hooks/useBackendConnection';
import { useSophiaWebSocket } from '../../../hooks/useSophiaWebSocket';
import { Card, CardContent } from '../../ui/card';
import { Button } from '../../ui/button';
import { Input } from '../../ui/input';
import { Alert, AlertDescription } from '../../ui/alert';
import { Skeleton } from '../../ui/skeleton';

// Import dashboard components
import ExecutiveKPIGrid from './components/ExecutiveKPIGrid';
import TeamPerformancePanel from './components/TeamPerformancePanel';
import MarketAnalyticsChart from './components/MarketAnalyticsChart';
import StrategicAlertsPanel from './components/StrategicAlertsPanel';
import RevenueProjectionChart from './components/RevenueProjectionChart';
import ExecutiveChatInterface from './components/ExecutiveChatInterface';

// Import hooks
import { useCEOMetrics } from './hooks/useCEOMetrics';
import { useTeamPerformance } from './hooks/useTeamPerformance';
import { useMarketData } from './hooks/useMarketData';

const CEODashboardLayout = () => {
  // Connection and chat state
  const { isHealthy, connectionStatus, error: connectionError } = useBackendConnection();
  const { 
    messages, 
    sendMessage, 
    isConnected: chatConnected, 
    connectionStatus: wsStatus 
  } = useSophiaWebSocket('ceo_dashboard');

  // Dashboard state
  const [timeRange, setTimeRange] = useState('30d');
  const [searchQuery, setSearchQuery] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  // Data hooks
  const {
    metrics: ceoMetrics,
    loading: metricsLoading,
    error: metricsError,
    refresh: refreshMetrics
  } = useCEOMetrics(timeRange);

  const {
    performance: teamData,
    loading: teamLoading,
    error: teamError,
    refresh: refreshTeamData
  } = useTeamPerformance(timeRange);

  const {
    marketData,
    loading: marketLoading,
    error: marketError,
    refresh: refreshMarketData
  } = useMarketData(timeRange);

  // Time range options
  const timeRangeOptions = [
    { value: '7d', label: '7 Days' },
    { value: '30d', label: '30 Days' },
    { value: '90d', label: '90 Days' },
    { value: '1y', label: '1 Year' }
  ];

  // Handle time range change
  const handleTimeRangeChange = (newTimeRange) => {
    setTimeRange(newTimeRange);
  };

  // Handle manual refresh
  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await Promise.all([
        refreshMetrics(),
        refreshTeamData(),
        refreshMarketData()
      ]);
    } catch (error) {
      console.error('Refresh failed:', error);
    } finally {
      setRefreshing(false);
    }
  };

  // Handle search
  const handleSearch = (query) => {
    setSearchQuery(query);
    // Implement search logic here
    console.log('Searching for:', query);
  };

  // Loading state for initial load
  const isInitialLoading = metricsLoading && teamLoading && marketLoading;

  // Error state
  const hasErrors = metricsError || teamError || marketError || connectionError;

  return (
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
          </div>
        </div>
      </div>

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
          </div>
        )}
      </div>
    </div>
  );
};

export default CEODashboardLayout;

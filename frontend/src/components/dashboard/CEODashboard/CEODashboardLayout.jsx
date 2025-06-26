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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <div className="sticky top-0 z-20 bg-white/80 backdrop-blur-md border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm font-bold">S</span>
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900">CEO Dashboard</h1>
                  <p className="text-sm text-gray-500">Executive Command Center</p>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              {/* Time Range Filters */}
              <div className="flex space-x-1">
                {timeRangeOptions.map((option) => (
                  <Button
                    key={option.value}
                    variant={timeRange === option.value ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => handleTimeRangeChange(option.value)}
                    disabled={isInitialLoading || refreshing}
                  >
                    {option.label}
                  </Button>
                ))}
              </div>

              {/* Refresh Button */}
              <Button
                variant="outline"
                size="sm"
                onClick={handleRefresh}
                disabled={refreshing}
              >
                {refreshing ? (
                  <div className="w-4 h-4 border-2 border-gray-300 border-t-gray-900 rounded-full animate-spin" />
                ) : (
                  '🔄'
                )}
              </Button>

              {/* Connection Status */}
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${
                  isHealthy ? 'bg-green-500' : 'bg-red-500'
                }`} />
                <span className="text-sm text-gray-600">
                  {isHealthy ? 'Connected' : 'Offline'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Connection Error Alert */}
      {connectionError && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-4">
          <Alert variant="destructive">
            <AlertDescription>
              Connection issue detected. Some data may be outdated. 
              <Button variant="outline" size="sm" className="ml-2" onClick={handleRefresh}>
                Retry
              </Button>
            </AlertDescription>
          </Alert>
        </div>
      )}

      {/* Search Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6">
        <Card>
          <CardContent className="p-4">
            <div className="flex space-x-2">
              <Input
                placeholder="Search across all executive data..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch(searchQuery)}
                className="flex-1"
              />
              <Button onClick={() => handleSearch(searchQuery)}>
                🔍 Search
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Dashboard Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {isInitialLoading ? (
          // Loading State
          <div className="space-y-6">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              {[...Array(4)].map((_, i) => (
                <Card key={i}>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div className="space-y-2">
                        <Skeleton className="h-4 w-20" />
                        <Skeleton className="h-8 w-32" />
                        <Skeleton className="h-3 w-24" />
                      </div>
                      <Skeleton className="h-12 w-12 rounded-full" />
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
            <div className="grid gap-6 lg:grid-cols-2">
              <Skeleton className="h-96" />
              <Skeleton className="h-96" />
            </div>
          </div>
        ) : (
          // Main Content
          <div className="space-y-6">
            {/* Executive KPI Grid */}
            <ExecutiveKPIGrid
              metrics={ceoMetrics}
              loading={metricsLoading}
              error={metricsError}
              timeRange={timeRange}
            />

            {/* Main Analytics Grid */}
            <div className="grid gap-6 lg:grid-cols-3">
              {/* Left Column - 2/3 width */}
              <div className="lg:col-span-2 space-y-6">
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
              <div className="space-y-6">
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

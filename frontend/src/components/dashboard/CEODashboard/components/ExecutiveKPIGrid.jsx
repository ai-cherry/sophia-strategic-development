import React from 'react';
<<<<<<< HEAD
<<<<<<< HEAD
=======
import { Card, CardContent, CardHeader, CardTitle } from '../../../ui/card';
=======
>>>>>>> 28336639693e9537cc10d264c0726f97d138a7b4
import { Skeleton } from '../../../ui/skeleton';
import { Alert, AlertDescription } from '../../../ui/alert';
>>>>>>> 1f64b2078be639c83d504e01809c555a3126abbd

const ExecutiveKPIGrid = ({ metrics, loading, error, timeRange }) => {
  if (loading) {
    return (
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
<<<<<<< HEAD
<<<<<<< HEAD
          <div key={i} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div className="space-y-2">
                <div className="h-4 w-20 bg-gray-200 rounded animate-pulse"></div>
                <div className="h-8 w-32 bg-gray-200 rounded animate-pulse"></div>
                <div className="h-3 w-24 bg-gray-200 rounded animate-pulse"></div>
              </div>
              <div className="h-12 w-12 bg-gray-200 rounded-full animate-pulse"></div>
            </div>
          </div>
=======
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
>>>>>>> 1f64b2078be639c83d504e01809c555a3126abbd
=======
          <div key={i} className="glassmorphism-card kpi-card p-6">
            <div className="flex items-center justify-between">
              <div className="space-y-3">
                <div className="skeleton h-4 w-20"></div>
                <div className="skeleton h-8 w-32"></div>
                <div className="skeleton h-3 w-24"></div>
              </div>
              <div className="skeleton h-12 w-12 rounded-full"></div>
            </div>
          </div>
>>>>>>> 28336639693e9537cc10d264c0726f97d138a7b4
        ))}
      </div>
    );
  }

  if (error) {
    return (
<<<<<<< HEAD
<<<<<<< HEAD
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">Failed to load KPI data: {error}</p>
      </div>
=======
      <Alert variant="destructive">
        <AlertDescription>
          Failed to load KPI data: {error}
        </AlertDescription>
      </Alert>
>>>>>>> 1f64b2078be639c83d504e01809c555a3126abbd
=======
      <div className="glassmorphism-card alert-error p-6">
        <div className="flex items-center space-x-3">
          <i className="fas fa-exclamation-triangle text-red-500"></i>
          <span className="text-executive-secondary">
            Failed to load KPI data: {error}
          </span>
        </div>
      </div>
>>>>>>> 28336639693e9537cc10d264c0726f97d138a7b4
    );
  }

  if (!metrics) {
    return (
<<<<<<< HEAD
<<<<<<< HEAD
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-yellow-800">No KPI data available for the selected time range.</p>
      </div>
=======
      <Alert>
        <AlertDescription>
          No KPI data available for the selected time range.
        </AlertDescription>
      </Alert>
>>>>>>> 1f64b2078be639c83d504e01809c555a3126abbd
=======
      <div className="glassmorphism-card alert-info p-6">
        <div className="flex items-center space-x-3">
          <i className="fas fa-info-circle text-blue-500"></i>
          <span className="text-executive-secondary">
            No KPI data available for the selected time range.
          </span>
        </div>
      </div>
>>>>>>> 28336639693e9537cc10d264c0726f97d138a7b4
    );
  }

  const formatChange = (change, trend) => {
    const sign = change >= 0 ? '+' : '';
    const trendClasses = {
      'up': 'trend-up',
      'down': 'trend-down',
      'neutral': 'trend-neutral'
    };
    
    return (
      <span className={`text-sm font-medium ${trendClasses[trend] || 'trend-neutral'}`}>
        <i className={`fas ${trend === 'up' ? 'fa-arrow-up' : trend === 'down' ? 'fa-arrow-down' : 'fa-arrow-right'} mr-1`}></i>
        {sign}{change.toFixed(1)}%
      </span>
    );
  };

  const kpiCards = [
    {
      title: 'Total Revenue',
      value: metrics.revenue?.current || '$2.4M',
      change: metrics.revenue?.change || 5.2,
      trend: metrics.revenue?.trend || 'up',
      target: metrics.revenue?.target || '$3.0M',
      icon: 'fa-dollar-sign',
      gradient: 'gradient-green'
    },
    {
      title: 'Active Deals',
      value: metrics.deals?.current || '156',
      change: metrics.deals?.change || 12.3,
      trend: metrics.deals?.trend || 'up',
      target: metrics.deals?.target || '200',
      icon: 'fa-handshake',
      gradient: 'gradient-purple-blue'
    },
    {
      title: 'Customer Health',
      value: metrics.customerHealth?.current || '94%',
      change: metrics.customerHealth?.change || 2.1,
      trend: metrics.customerHealth?.trend || 'up',
      target: metrics.customerHealth?.target || '95%',
      icon: 'fa-heart',
      gradient: 'gradient-pink'
    },
    {
      title: 'Team Performance',
      value: metrics.teamPerformance?.current || '88%',
      change: metrics.teamPerformance?.change || -1.5,
      trend: metrics.teamPerformance?.trend || 'down',
      target: metrics.teamPerformance?.target || '90%',
      icon: 'fa-users',
      gradient: 'gradient-orange'
    }
  ];

  const getTimeRangeLabel = (timeRange) => {
    const labels = {
      '7d': 'Last 7 days',
      '30d': 'Last 30 days',
      '90d': 'Last 90 days',
      '1y': 'Last year'
    };
    return labels[timeRange] || 'Custom range';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
<<<<<<< HEAD
<<<<<<< HEAD
        <h2 className="text-2xl font-bold text-white">Executive KPIs</h2>
        <span className="text-sm text-gray-400">
=======
        <h2 className="text-2xl font-bold text-gray-900">Executive KPIs</h2>
        <span className="text-sm text-gray-500">
>>>>>>> 1f64b2078be639c83d504e01809c555a3126abbd
          {timeRange === '7d' ? 'Last 7 days' : 
           timeRange === '30d' ? 'Last 30 days' : 
           timeRange === '90d' ? 'Last 90 days' : 'Last year'}
        </span>
=======
        <div className="flex items-center space-x-3">
          <div className="executive-icon gradient-purple-blue">
            <i className="fas fa-chart-line"></i>
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white">Executive KPIs</h2>
            <p className="text-executive-secondary">Real-time performance metrics</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <i className="fas fa-clock text-executive-muted"></i>
          <span className="text-sm text-executive-secondary">
            {getTimeRangeLabel(timeRange)}
          </span>
        </div>
>>>>>>> 28336639693e9537cc10d264c0726f97d138a7b4
      </div>
      
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {kpiCards.map((kpi, index) => (
<<<<<<< HEAD
<<<<<<< HEAD
          <div key={index} className="bg-gray-800 rounded-lg shadow-lg p-6 relative overflow-hidden">
            <div className="flex items-center justify-between">
              <div className="space-y-2">
                <p className="text-sm font-medium text-gray-300">{kpi.title}</p>
                <p className="text-3xl font-bold text-white">{kpi.value}</p>
                <div className="flex items-center space-x-2">
                  {formatChange(kpi.change, kpi.trend)}
                  {kpi.target && (
                    <span className="text-xs text-gray-400">
                      Target: {kpi.target}
                    </span>
                  )}
                </div>
              </div>
              <div className={`w-12 h-12 ${kpi.color} rounded-full flex items-center justify-center text-white text-2xl`}>
                {kpi.icon}
              </div>
            </div>
            
            {/* Progress bar for target */}
            {kpi.target && kpi.value !== 'N/A' && (
              <div className="mt-4">
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${kpi.color}`}
                    style={{
                      width: `${Math.min(100, (parseFloat(kpi.value.replace(/[^0-9.]/g, '')) / parseFloat(kpi.target.replace(/[^0-9.]/g, ''))) * 100)}%`
                    }}
                  ></div>
                </div>
              </div>
            )}
          </div>
=======
          <Card key={index} className="relative overflow-hidden">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="space-y-2">
                  <p className="text-sm font-medium text-gray-600">{kpi.title}</p>
                  <p className="text-3xl font-bold text-gray-900">{kpi.value}</p>
                  <div className="flex items-center space-x-2">
                    {formatChange(kpi.change, kpi.trend)}
                    {kpi.target && (
                      <span className="text-xs text-gray-400">
                        Target: {kpi.target}
                      </span>
                    )}
                  </div>
=======
          <div key={index} className="glassmorphism-card kpi-card hover-scale hover-glow p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <p className="text-sm font-medium text-executive-secondary">{kpi.title}</p>
                  <i className="fas fa-info-circle text-executive-muted text-xs"></i>
>>>>>>> 28336639693e9537cc10d264c0726f97d138a7b4
                </div>
                <p className="text-3xl font-bold text-white">{kpi.value}</p>
                <div className="flex items-center space-x-3">
                  {formatChange(kpi.change, kpi.trend)}
                  {kpi.target && (
                    <span className="text-xs text-executive-muted">
                      Target: {kpi.target}
                    </span>
                  )}
                </div>
              </div>
              <div className={`executive-icon-lg ${kpi.gradient}`}>
                <i className={`fas ${kpi.icon}`}></i>
              </div>
            </div>
            
            {/* Target Progress Bar */}
            {kpi.target && kpi.value !== 'N/A' && (
              <div className="space-y-2">
                <div className="w-full bg-gray-800 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${kpi.gradient}`}
                    style={{
                      width: `${Math.min(100, (parseFloat(kpi.value.replace(/[^0-9.]/g, '')) / parseFloat(kpi.target.replace(/[^0-9.]/g, ''))) * 100)}%`
                    }}
                  />
                </div>
<<<<<<< HEAD
              )}
            </CardContent>
          </Card>
>>>>>>> 1f64b2078be639c83d504e01809c555a3126abbd
=======
                <div className="flex justify-between items-center">
                  <span className="text-xs text-executive-muted">
                    Progress to target
                  </span>
                  <span className="text-xs text-executive-secondary font-medium">
                    {Math.round((parseFloat(kpi.value.replace(/[^0-9.]/g, '')) / parseFloat(kpi.target.replace(/[^0-9.]/g, ''))) * 100)}%
                  </span>
                </div>
              </div>
            )}

            {/* Mini Trend Indicator */}
            <div className="mt-3 pt-3 border-t border-gray-700">
              <div className="flex items-center justify-between">
                <span className="text-xs text-executive-muted">
                  vs previous period
                </span>
                <div className="flex items-center space-x-1">
                  <div className={`w-2 h-2 rounded-full pulse-dot ${
                    kpi.trend === 'up' ? 'status-online' : 
                    kpi.trend === 'down' ? 'status-offline' : 'status-warning'
                  }`}></div>
                  <span className="text-xs text-executive-secondary">
                    {kpi.trend === 'up' ? 'Improving' : 
                     kpi.trend === 'down' ? 'Declining' : 'Stable'}
                  </span>
                </div>
              </div>
            </div>
          </div>
>>>>>>> 28336639693e9537cc10d264c0726f97d138a7b4
        ))}
      </div>
    </div>
  );
};

export default ExecutiveKPIGrid;
<<<<<<< HEAD

=======
>>>>>>> 1f64b2078be639c83d504e01809c555a3126abbd

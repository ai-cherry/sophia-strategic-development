import React from 'react';
<<<<<<< HEAD
=======
import { Card, CardContent, CardHeader, CardTitle } from '../../../ui/card';
import { Skeleton } from '../../../ui/skeleton';
import { Alert, AlertDescription } from '../../../ui/alert';
>>>>>>> 1f64b2078be639c83d504e01809c555a3126abbd

const ExecutiveKPIGrid = ({ metrics, loading, error, timeRange }) => {
  if (loading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
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
        ))}
      </div>
    );
  }

  if (error) {
    return (
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
    );
  }

  if (!metrics) {
    return (
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
    );
  }

  const formatChange = (change, trend) => {
    const sign = change >= 0 ? '+' : '';
    const arrow = trend === 'up' ? '↗' : trend === 'down' ? '↘' : '→';
    const color = trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-gray-600';
    
    return (
      <span className={`text-sm ${color}`}>
        {arrow} {sign}{change.toFixed(1)}%
      </span>
    );
  };

  const kpiCards = [
    {
      title: 'Total Revenue',
      value: metrics.revenue?.current || 'N/A',
      change: metrics.revenue?.change || 0,
      trend: metrics.revenue?.trend || 'neutral',
      target: metrics.revenue?.target,
      icon: '💰',
      color: 'bg-green-500'
    },
    {
      title: 'Active Deals',
      value: metrics.deals?.current || 'N/A',
      change: metrics.deals?.change || 0,
      trend: metrics.deals?.trend || 'neutral',
      target: metrics.deals?.target,
      icon: '🤝',
      color: 'bg-blue-500'
    },
    {
      title: 'Customer Health',
      value: metrics.customerHealth?.current || 'N/A',
      change: metrics.customerHealth?.change || 0,
      trend: metrics.customerHealth?.trend || 'neutral',
      target: metrics.customerHealth?.target,
      icon: '❤️',
      color: 'bg-red-500'
    },
    {
      title: 'Team Performance',
      value: metrics.teamPerformance?.current || 'N/A',
      change: metrics.teamPerformance?.change || 0,
      trend: metrics.teamPerformance?.trend || 'neutral',
      target: metrics.teamPerformance?.target,
      icon: '⭐',
      color: 'bg-purple-500'
    }
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
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
      </div>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {kpiCards.map((kpi, index) => (
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
                </div>
                <div className={`w-12 h-12 ${kpi.color} rounded-full flex items-center justify-center text-white text-2xl`}>
                  {kpi.icon}
                </div>
              </div>
              
              {/* Progress bar for target */}
              {kpi.target && kpi.value !== 'N/A' && (
                <div className="mt-4">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${kpi.color}`}
                      style={{
                        width: `${Math.min(100, (parseFloat(kpi.value.replace(/[^0-9.]/g, '')) / parseFloat(kpi.target.replace(/[^0-9.]/g, ''))) * 100)}%`
                      }}
                    />
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    Progress to target
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
>>>>>>> 1f64b2078be639c83d504e01809c555a3126abbd
        ))}
      </div>
    </div>
  );
};

export default ExecutiveKPIGrid;
<<<<<<< HEAD

=======
>>>>>>> 1f64b2078be639c83d504e01809c555a3126abbd

import React from 'react';

const ExecutiveKPIGrid = ({ metrics, loading, error, timeRange }) => {
  if (loading) {
    return (
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-gray-800 rounded-xl p-6 border border-gray-700 animate-pulse">
            <div className="flex items-center justify-between mb-4">
              <div className="space-y-3">
                <div className="h-4 bg-gray-700 rounded w-20"></div>
                <div className="h-8 bg-gray-700 rounded w-32"></div>
                <div className="h-3 bg-gray-700 rounded w-24"></div>
              </div>
              <div className="h-12 w-12 bg-gray-700 rounded-full"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <div className="col-span-full bg-red-900/20 border border-red-500 rounded-xl p-4">
          <div className="flex items-center space-x-3">
            <span className="text-red-500 text-xl">⚠️</span>
            <div>
              <h3 className="text-red-400 font-medium">Error Loading KPIs</h3>
              <p className="text-red-300 text-sm">{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Default metrics if none provided
  const defaultMetrics = [
    {
      title: 'Total Revenue',
      value: '$2.4M',
      trend: 'up',
      trendValue: '+12.5%',
      description: 'Trending up this month',
      status: 'success',
      icon: '💰'
    },
    {
      title: 'Active Deals',
      value: '156',
      trend: 'up',
      trendValue: '+8.2%',
      description: 'Strong pipeline growth',
      status: 'success',
      icon: '🎯'
    },
    {
      title: 'Team Efficiency',
      value: '94%',
      trend: 'up',
      trendValue: '+2.1%',
      description: 'Above target performance',
      status: 'success',
      icon: '⚡'
    },
    {
      title: 'Customer Satisfaction',
      value: '4.8/5',
      trend: 'up',
      trendValue: '+5.2%',
      description: 'Excellent feedback scores',
      status: 'success',
      icon: '⭐'
    }
  ];

  const displayMetrics = metrics || defaultMetrics;

  const getStatusColor = (status) => {
    switch (status) {
      case 'success': return 'border-green-500 bg-green-500/10';
      case 'warning': return 'border-yellow-500 bg-yellow-500/10';
      case 'error': return 'border-red-500 bg-red-500/10';
      default: return 'border-gray-500 bg-gray-500/10';
    }
  };

  const getTrendColor = (trend) => {
    switch (trend) {
      case 'up': return 'text-green-400';
      case 'down': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'up': return '↗️';
      case 'down': return '↘️';
      default: return '→';
    }
  };

  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
      {displayMetrics.map((metric, index) => (
        <div
          key={index}
          className={`bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-purple-500 transition-all duration-300 hover:shadow-lg hover:shadow-purple-500/20 ${getStatusColor(metric.status)}`}
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-purple-500/20 rounded-lg">
                <span className="text-2xl">{metric.icon}</span>
              </div>
              <h3 className="text-gray-300 text-sm font-medium">{metric.title}</h3>
            </div>
            <span className="text-lg">{getTrendIcon(metric.trend)}</span>
          </div>
          
          <div className="space-y-2">
            <div className="flex items-baseline space-x-2">
              <span className="text-3xl font-bold text-white">{metric.value}</span>
              {metric.trendValue && (
                <span className={`text-sm font-medium ${getTrendColor(metric.trend)}`}>
                  {metric.trendValue}
                </span>
              )}
            </div>
            
            {metric.description && (
              <p className="text-xs text-gray-400">{metric.description}</p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default ExecutiveKPIGrid;


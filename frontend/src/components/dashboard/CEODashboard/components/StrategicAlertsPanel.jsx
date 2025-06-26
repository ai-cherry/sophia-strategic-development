import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../../ui/card';
import { Alert, AlertDescription } from '../../../ui/alert';
import { Skeleton } from '../../../ui/skeleton';

const StrategicAlertsPanel = ({ alerts, loading, error }) => {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Strategic Alerts</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="border rounded-lg p-4">
                <Skeleton className="h-4 w-32 mb-2" />
                <Skeleton className="h-6 w-full mb-1" />
                <Skeleton className="h-4 w-24" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Strategic Alerts</CardTitle>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertDescription>
              Failed to load alerts: {error}
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (!alerts || alerts.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Strategic Alerts</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-gray-500">
            <div className="text-4xl mb-2">✅</div>
            <p>No alerts at this time</p>
            <p className="text-sm">All systems are running normally</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const getAlertColor = (type) => {
    switch (type) {
      case 'success': return 'border-green-200 bg-green-50';
      case 'warning': return 'border-yellow-200 bg-yellow-50';
      case 'error': return 'border-red-200 bg-red-50';
      default: return 'border-blue-200 bg-blue-50';
    }
  };

  const getAlertIcon = (type) => {
    switch (type) {
      case 'success': return '✅';
      case 'warning': return '⚠️';
      case 'error': return '🚨';
      default: return 'ℹ️';
    }
  };

  const getPriorityBadge = (priority) => {
    const colors = {
      high: 'bg-red-100 text-red-800',
      medium: 'bg-yellow-100 text-yellow-800',
      low: 'bg-gray-100 text-gray-800'
    };
    
    return colors[priority] || colors.low;
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    
    const now = new Date();
    const alertTime = new Date(timestamp);
    const diffMs = now - alertTime;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-xl font-bold">Strategic Alerts</CardTitle>
        <span className="px-2 py-1 bg-gray-100 text-gray-700 text-sm rounded-full">
          {alerts.length}
        </span>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {alerts.map((alert) => (
            <div 
              key={alert.id} 
              className={`border rounded-lg p-4 ${getAlertColor(alert.type)} hover:shadow-md transition-shadow cursor-pointer`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  <span className="text-lg">{getAlertIcon(alert.type)}</span>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <h4 className="font-semibold text-gray-900">{alert.title}</h4>
                      <span className={`px-2 py-1 text-xs rounded-full ${getPriorityBadge(alert.priority)}`}>
                        {alert.priority}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{alert.message}</p>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-500">
                        {formatTimestamp(alert.timestamp)}
                      </span>
                      {alert.action && (
                        <button className="text-xs text-blue-600 hover:text-blue-800 font-medium">
                          {alert.action} →
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
        
        <div className="mt-4 pt-4 border-t">
          <button className="text-sm text-blue-600 hover:text-blue-800 font-medium">
            View all alerts →
          </button>
        </div>
      </CardContent>
    </Card>
  );
};

export default StrategicAlertsPanel;

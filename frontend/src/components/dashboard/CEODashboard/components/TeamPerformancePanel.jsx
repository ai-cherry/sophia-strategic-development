import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../../ui/card';
import { Skeleton } from '../../../ui/skeleton';
import { Alert, AlertDescription } from '../../../ui/alert';

const TeamPerformancePanel = ({ data, loading, error, timeRange }) => {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Team Performance</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="space-y-2">
                  <Skeleton className="h-4 w-20" />
                  <Skeleton className="h-6 w-32" />
                </div>
                <Skeleton className="h-8 w-16" />
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
          <CardTitle>Team Performance</CardTitle>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertDescription>
              Failed to load team performance data: {error}
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (!data || !data.departments) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Team Performance</CardTitle>
        </CardHeader>
        <CardContent>
          <Alert>
            <AlertDescription>
              No team performance data available.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  const getScoreColor = (score) => {
    if (score >= 90) return 'text-green-600 bg-green-100';
    if (score >= 80) return 'text-blue-600 bg-blue-100';
    if (score >= 70) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getTrendIcon = (trend) => {
    switch(trend) {
      case 'up': return '📈';
      case 'down': return '📉';
      default: return '➡️';
    }
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-xl font-bold">Team Performance</CardTitle>
        <div className="text-sm text-gray-500">
          Overall Score: <span className="font-bold text-lg">{data.overall?.score || 0}/100</span>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {data.departments.map((dept, index) => (
            <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
              <div className="flex-1">
                <div className="flex items-center space-x-3">
                  <h3 className="font-semibold text-gray-900">{dept.name}</h3>
                  <span className="text-lg">{getTrendIcon(dept.trend)}</span>
                  <span className="text-sm text-gray-500">
                    {dept.change >= 0 ? '+' : ''}{dept.change?.toFixed(1)}%
                  </span>
                </div>
                <div className="mt-2 grid grid-cols-3 gap-4 text-sm">
                  {Object.entries(dept.metrics || {}).map(([key, value]) => (
                    <div key={key}>
                      <span className="text-gray-500 capitalize">{key}: </span>
                      <span className="font-medium">{value}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${getScoreColor(dept.score)}`}>
                  {dept.score}/100
                </div>
                <div className="text-xs text-gray-400">
                  Target: {dept.target}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Goals Section */}
        {data.goals && data.goals.length > 0 && (
          <div className="mt-6">
            <h4 className="font-semibold text-gray-900 mb-3">Department Goals</h4>
            <div className="space-y-2">
              {data.goals.map((goal, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-white border rounded-lg">
                  <div>
                    <span className="font-medium">{goal.department}</span>
                    <span className="text-gray-500 ml-2">- {goal.goal}</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="flex-1 w-24 bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${
                          goal.status === 'ahead' ? 'bg-green-500' :
                          goal.status === 'on-track' ? 'bg-blue-500' :
                          'bg-yellow-500'
                        }`}
                        style={{ width: `${goal.progress}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium w-12">{goal.progress}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default TeamPerformancePanel;

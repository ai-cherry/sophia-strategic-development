import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../../ui/card';
import { Skeleton } from '../../../ui/skeleton';
import { Alert, AlertDescription } from '../../../ui/alert';

const RevenueProjectionChart = ({ data, loading, error, timeRange }) => {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Revenue Projections</CardTitle>
        </CardHeader>
        <CardContent>
          <Skeleton className="h-80 w-full" />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Revenue Projections</CardTitle>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertDescription>
              Failed to load revenue data: {error}
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (!data || !Array.isArray(data)) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Revenue Projections</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-gray-500">
            No revenue data available
          </div>
        </CardContent>
      </Card>
    );
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const maxValue = Math.max(...data.map(d => Math.max(d.revenue, d.target, d.forecast)));
  const minValue = Math.min(...data.map(d => Math.min(d.revenue, d.target, d.forecast)));
  const range = maxValue - minValue;

  const getYPosition = (value) => {
    return 100 - ((value - minValue) / range) * 100;
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-xl font-bold">Revenue Projections</CardTitle>
        <div className="flex items-center space-x-4 text-sm">
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-blue-500 rounded-full" />
            <span>Actual</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-gray-400 rounded-full" />
            <span>Target</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-green-500 rounded-full" />
            <span>Forecast</span>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Simple Chart Representation */}
          <div className="relative h-64 bg-gray-50 rounded-lg p-4">
            <svg width="100%" height="100%" className="overflow-visible">
              {/* Grid lines */}
              {[0, 25, 50, 75, 100].map(y => (
                <line
                  key={y}
                  x1="0"
                  y1={`${y}%`}
                  x2="100%"
                  y2={`${y}%`}
                  stroke="#e5e7eb"
                  strokeWidth="1"
                />
              ))}
              
              {/* Revenue line */}
              <polyline
                fill="none"
                stroke="#3b82f6"
                strokeWidth="3"
                points={data.map((d, i) => 
                  `${(i / (data.length - 1)) * 100},${getYPosition(d.revenue)}`
                ).join(' ')}
              />
              
              {/* Target line */}
              <polyline
                fill="none"
                stroke="#9ca3af"
                strokeWidth="2"
                strokeDasharray="5,5"
                points={data.map((d, i) => 
                  `${(i / (data.length - 1)) * 100},${getYPosition(d.target)}`
                ).join(' ')}
              />
              
              {/* Forecast line */}
              <polyline
                fill="none"
                stroke="#10b981"
                strokeWidth="2"
                strokeDasharray="3,3"
                points={data.map((d, i) => 
                  `${(i / (data.length - 1)) * 100},${getYPosition(d.forecast)}`
                ).join(' ')}
              />
              
              {/* Data points */}
              {data.map((d, i) => (
                <circle
                  key={i}
                  cx={`${(i / (data.length - 1)) * 100}%`}
                  cy={`${getYPosition(d.revenue)}%`}
                  r="4"
                  fill="#3b82f6"
                  className="hover:r-6 cursor-pointer"
                  title={`${d.month}: ${formatCurrency(d.revenue)}`}
                />
              ))}
            </svg>
            
            {/* X-axis labels */}
            <div className="absolute bottom-0 left-0 right-0 flex justify-between text-xs text-gray-500 mt-2">
              {data.map((d, i) => (
                <span key={i}>{d.month}</span>
              ))}
            </div>
          </div>

          {/* Data Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2">Month</th>
                  <th className="text-right py-2">Actual</th>
                  <th className="text-right py-2">Target</th>
                  <th className="text-right py-2">Forecast</th>
                  <th className="text-right py-2">vs Target</th>
                </tr>
              </thead>
              <tbody>
                {data.map((d, i) => {
                  const vsTarget = ((d.revenue - d.target) / d.target) * 100;
                  return (
                    <tr key={i} className="border-b">
                      <td className="py-2 font-medium">{d.month}</td>
                      <td className="text-right py-2">{formatCurrency(d.revenue)}</td>
                      <td className="text-right py-2 text-gray-600">{formatCurrency(d.target)}</td>
                      <td className="text-right py-2 text-green-600">{formatCurrency(d.forecast)}</td>
                      <td className={`text-right py-2 ${vsTarget >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {vsTarget >= 0 ? '+' : ''}{vsTarget.toFixed(1)}%
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default RevenueProjectionChart;

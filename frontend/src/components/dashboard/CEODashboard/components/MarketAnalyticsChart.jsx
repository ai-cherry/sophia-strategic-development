import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../../ui/card';
import { Skeleton } from '../../../ui/skeleton';
import { Alert, AlertDescription } from '../../../ui/alert';

const MarketAnalyticsChart = ({ data, loading, error, timeRange }) => {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Market Analytics</CardTitle>
        </CardHeader>
        <CardContent>
          <Skeleton className="h-64 w-full" />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Market Analytics</CardTitle>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertDescription>
              Failed to load market data: {error}
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (!data) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Market Analytics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-gray-500">
            No market data available
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Market Intelligence</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Market Share */}
          {data.marketShare && (
            <div>
              <h4 className="font-semibold text-gray-900 mb-3">Market Share</h4>
              <div className="space-y-2">
                {data.marketShare.competitors?.map((competitor, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className={`w-3 h-3 rounded-full ${
                        competitor.name === 'Pay Ready' ? 'bg-blue-500' : 'bg-gray-300'
                      }`} />
                      <span className={`text-sm ${
                        competitor.name === 'Pay Ready' ? 'font-semibold' : ''
                      }`}>
                        {competitor.name}
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium">{competitor.share}%</span>
                      <span className={`text-xs ${
                        competitor.change >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {competitor.change >= 0 ? '+' : ''}{competitor.change}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Market Trends */}
          {data.marketTrends && data.marketTrends.length > 0 && (
            <div>
              <h4 className="font-semibold text-gray-900 mb-3">Key Trends</h4>
              <div className="space-y-3">
                {data.marketTrends.map((trend, index) => (
                  <div key={index} className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium text-sm">{trend.trend}</span>
                      <span className="text-green-600 text-sm font-medium">+{trend.growth}%</span>
                    </div>
                    <p className="text-xs text-gray-600">{trend.opportunity}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Industry Metrics */}
          {data.industryMetrics && (
            <div>
              <h4 className="font-semibold text-gray-900 mb-3">Industry Overview</h4>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Market Size</span>
                  <p className="font-semibold">{data.industryMetrics.marketSize}</p>
                </div>
                <div>
                  <span className="text-gray-500">Growth Rate</span>
                  <p className="font-semibold text-green-600">{data.industryMetrics.growthRate}</p>
                </div>
                <div>
                  <span className="text-gray-500">Total Funding</span>
                  <p className="font-semibold">{data.industryMetrics.funding}</p>
                </div>
                <div>
                  <span className="text-gray-500">Companies</span>
                  <p className="font-semibold">{data.industryMetrics.totalCompanies}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default MarketAnalyticsChart;

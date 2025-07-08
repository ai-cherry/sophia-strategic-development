import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import {
  Activity,
  Zap,
  Database,
  TrendingUp,
  AlertCircle,
  CheckCircle
} from 'lucide-react';

interface CacheStats {
  hits: number;
  misses: number;
  hit_rate: number;
  total_queries: number;
  cache_size: number;
  avg_similarity: number;
  model: string;
  threshold: number;
}

export const CacheMonitoringWidget: React.FC = () => {
  const [stats, setStats] = useState<CacheStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch('/api/cache/stats');
        if (!response.ok) throw new Error('Failed to fetch cache stats');
        const data = await response.json();
        setStats(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 5000); // Update every 5 seconds

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Card className="w-full">
        <CardContent className="p-6">
          <div className="animate-pulse space-y-3">
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            <div className="h-8 bg-gray-200 rounded"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="w-full border-red-200">
        <CardContent className="p-6">
          <div className="flex items-center gap-2 text-red-600">
            <AlertCircle className="h-5 w-5" />
            <span>Error loading cache stats: {error}</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!stats) return null;

  const hitRatePercent = stats.hit_rate * 100;
  const isHealthy = hitRatePercent > 60;

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-semibold">
            AI Cache Performance
          </CardTitle>
          <Badge
            variant={isHealthy ? "success" : "warning"}
            className="flex items-center gap-1"
          >
            {isHealthy ? (
              <CheckCircle className="h-3 w-3" />
            ) : (
              <AlertCircle className="h-3 w-3" />
            )}
            {isHealthy ? 'Healthy' : 'Needs Attention'}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Hit Rate */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Zap className="h-4 w-4 text-yellow-500" />
              <span className="text-sm font-medium">Cache Hit Rate</span>
            </div>
            <span className="text-2xl font-bold text-green-600">
              {hitRatePercent.toFixed(1)}%
            </span>
          </div>
          <Progress value={hitRatePercent} className="h-2" />
          <p className="text-xs text-gray-500 mt-1">
            {stats.hits} hits / {stats.total_queries} total queries
          </p>
        </div>

        {/* Cache Stats Grid */}
        <div className="grid grid-cols-2 gap-4 pt-2">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <Database className="h-4 w-4 text-blue-500" />
              <span className="text-xs text-gray-500">Cache Size</span>
            </div>
            <p className="text-lg font-semibold">{stats.cache_size}</p>
          </div>

          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-purple-500" />
              <span className="text-xs text-gray-500">Avg Similarity</span>
            </div>
            <p className="text-lg font-semibold">
              {(stats.avg_similarity * 100).toFixed(1)}%
            </p>
          </div>
        </div>

        {/* Model Info */}
        <div className="pt-2 border-t">
          <div className="flex items-center justify-between text-xs">
            <span className="text-gray-500">Model</span>
            <span className="font-mono">{stats.model}</span>
          </div>
          <div className="flex items-center justify-between text-xs mt-1">
            <span className="text-gray-500">Threshold</span>
            <span className="font-mono">{(stats.threshold * 100).toFixed(0)}%</span>
          </div>
        </div>

        {/* Performance Insight */}
        <div className="bg-blue-50 rounded-lg p-3">
          <div className="flex items-start gap-2">
            <TrendingUp className="h-4 w-4 text-blue-600 mt-0.5" />
            <div className="text-xs">
              <p className="font-medium text-blue-900">Performance Impact</p>
              <p className="text-blue-700 mt-1">
                {hitRatePercent > 70
                  ? `Excellent! Saving ~${((stats.hits * 150) / 1000).toFixed(1)}s in query time`
                  : hitRatePercent > 50
                  ? `Good performance. Consider pre-warming more queries`
                  : `Low hit rate. Cache may need optimization`
                }
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Line, Doughnut } from 'react-chartjs-2';
import { BrainCircuit, Activity, Database, Zap, Clock, CheckCircle } from 'lucide-react';
import { useOptimizedQuery } from '@/hooks/useDataFetching';
import apiClient from '../../services/apiClient';

interface AIMemoryHealthData {
  performance_score: number;
  response_times: {
    average: number;
    p95: number;
    p99: number;
  };
  cache_performance: {
    hit_rate: number;
    size: number;
    efficiency: number;
  };
  operation_stats: {
    total_operations: number;
    successful_operations: number;
    error_rate: number;
  };
  memory_usage: {
    current: number;
    peak: number;
    efficiency: number;
  };
  recent_operations: Array<{
    id: string;
    operation: string;
    duration: number;
    status: string;
    timestamp: string;
  }>;
}

const AIMemoryHealthTab: React.FC = () => {
  const { data: healthData, isLoading } = useOptimizedQuery<AIMemoryHealthData>(
    ['aiMemoryHealth'],
    '/api/v1/ai-memory/health',
    { refetchInterval: 30000 }
  );

  const { data: trendsData } = useOptimizedQuery(
    ['aiMemoryTrends'],
    '/api/v1/ai-memory/performance-trends',
    { refetchInterval: 60000 }
  );

  if (isLoading || !healthData) {
    return <div>Loading AI Memory health data...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Performance Overview Cards */}
      <div className="grid gap-6 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Performance Score</CardTitle>
            <BrainCircuit className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{healthData.performance_score}/100</div>
            <Progress value={healthData.performance_score} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Response Time</CardTitle>
            <Clock className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{healthData.response_times.average}ms</div>
            <p className="text-xs text-green-600">Target: <100ms</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Cache Hit Rate</CardTitle>
            <Zap className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(healthData.cache_performance.hit_rate * 100).toFixed(1)}%</div>
            <Progress value={healthData.cache_performance.hit_rate * 100} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {((1 - healthData.operation_stats.error_rate) * 100).toFixed(1)}%
            </div>
            <p className="text-xs text-green-600">
              {healthData.operation_stats.successful_operations} successful ops
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Performance Trends Chart */}
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Response Time Trends</CardTitle>
          </CardHeader>
          <CardContent>
            {trendsData && (
              <Line
                data={{
                  labels: trendsData.labels,
                  datasets: [
                    {
                      label: 'Response Time (ms)',
                      data: trendsData.response_times,
                      borderColor: 'rgb(59, 130, 246)',
                      backgroundColor: 'rgba(59, 130, 246, 0.1)',
                      tension: 0.4
                    }
                  ]
                }}
                options={{
                  responsive: true,
                  plugins: { legend: { display: false } },
                  scales: {
                    y: { beginAtZero: true, title: { display: true, text: 'Milliseconds' } }
                  }
                }}
              />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Cache Performance</CardTitle>
          </CardHeader>
          <CardContent>
            <Doughnut
              data={{
                labels: ['Cache Hits', 'Cache Misses'],
                datasets: [{
                  data: [
                    healthData.cache_performance.hit_rate * 100,
                    (1 - healthData.cache_performance.hit_rate) * 100
                  ],
                  backgroundColor: ['#10B981', '#EF4444']
                }]
              }}
              options={{
                responsive: true,
                plugins: { legend: { position: 'bottom' } }
              }}
            />
          </CardContent>
        </Card>
      </div>

      {/* Recent Operations Table */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Operations</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {healthData.recent_operations.map((op) => (
              <div key={op.id} className="flex items-center justify-between p-2 border rounded">
                <div className="flex items-center gap-3">
                  <Badge variant={op.status === 'success' ? 'default' : 'destructive'}>
                    {op.status}
                  </Badge>
                  <span className="font-medium">{op.operation}</span>
                </div>
                <div className="text-sm text-gray-500">
                  {op.duration}ms • {new Date(op.timestamp).toLocaleTimeString()}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AIMemoryHealthTab;

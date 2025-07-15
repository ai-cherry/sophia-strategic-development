import React, { useState, useEffect } from 'react';
import { 
  Card, 
  CardContent, 
  CardHeader, 
  CardTitle,
  CardDescription 
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  TrendingUp, 
  TrendingDown, 
  Target,
  CheckCircle,
  AlertCircle,
  Clock
} from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts';

interface OKR {
  id: string;
  title: string;
  progress: number;
  target: number;
  status: 'on_track' | 'at_risk' | 'completed' | 'blocked';
  keyResults: KeyResult[];
  owner: string;
  dueDate: string;
}

interface KeyResult {
  id: string;
  description: string;
  progress: number;
  target: number;
  unit: string;
  status: 'on_track' | 'at_risk' | 'completed';
}

interface ExecutiveSummary {
  overallHealth: number;
  completedOKRs: number;
  atRiskOKRs: number;
  keyInsights: string[];
  strategicRecommendations: string[];
  lastUpdated: string;
}

const COLORS = ['#10B981', '#F59E0B', '#EF4444', '#6B7280'];

const StrategicOverviewPanel: React.FC = () => {
  const [okrs, setOKRs] = useState<OKR[]>([]);
  const [executiveSummary, setExecutiveSummary] = useState<ExecutiveSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Mock data for demonstration
  const mockOKRs: OKR[] = [
    {
      id: '1',
      title: 'Achieve 25% YoY Revenue Growth',
      progress: 82,
      target: 100,
      status: 'on_track',
      owner: 'CEO',
      dueDate: '2025-12-31',
      keyResults: [
        { id: '1.1', description: 'Reach $5.2M quarterly revenue', progress: 95, target: 100, unit: '%', status: 'completed' },
        { id: '1.2', description: 'Acquire 50 new enterprise clients', progress: 76, target: 100, unit: 'clients', status: 'on_track' },
        { id: '1.3', description: 'Expand into 3 new markets', progress: 67, target: 100, unit: 'markets', status: 'at_risk' }
      ]
    },
    {
      id: '2',
      title: 'Scale AI Platform Performance',
      progress: 91,
      target: 100,
      status: 'on_track',
      owner: 'CTO',
      dueDate: '2025-11-30',
      keyResults: [
        { id: '2.1', description: 'Reduce average latency to <100ms', progress: 88, target: 100, unit: 'ms', status: 'on_track' },
        { id: '2.2', description: 'Achieve 99.9% uptime', progress: 99, target: 100, unit: '%', status: 'completed' },
        { id: '2.3', description: 'Process 10K+ concurrent users', progress: 85, target: 100, unit: 'users', status: 'on_track' }
      ]
    },
    {
      id: '3',
      title: 'Enhance Customer Success',
      progress: 58,
      target: 100,
      status: 'at_risk',
      owner: 'VP Customer Success',
      dueDate: '2025-12-15',
      keyResults: [
        { id: '3.1', description: 'Achieve 95% customer satisfaction', progress: 78, target: 100, unit: '%', status: 'at_risk' },
        { id: '3.2', description: 'Reduce churn to <5%', progress: 45, target: 100, unit: '%', status: 'at_risk' },
        { id: '3.3', description: 'Implement 24/7 support', progress: 52, target: 100, unit: '%', status: 'at_risk' }
      ]
    }
  ];

  const mockExecutiveSummary: ExecutiveSummary = {
    overallHealth: 77,
    completedOKRs: 1,
    atRiskOKRs: 1,
    keyInsights: [
      "Revenue growth exceeding expectations with 95% of Q4 target achieved",
      "Technical platform performing exceptionally well with 99.9% uptime",
      "Customer success metrics need immediate attention - action plan required"
    ],
    strategicRecommendations: [
      "Accelerate customer success initiatives to prevent churn",
      "Consider expanding successful revenue strategies to new markets",
      "Maintain technical excellence while scaling operations"
    ],
    lastUpdated: new Date().toISOString()
  };

  useEffect(() => {
    // Simulate API call to MCP servers
    const loadStrategicData = async () => {
      setIsLoading(true);
      try {
        // In production, this would call the Notion Strategic MCP server
        await new Promise(resolve => setTimeout(resolve, 1000));
        setOKRs(mockOKRs);
        setExecutiveSummary(mockExecutiveSummary);
      } catch (error) {
        console.error('Failed to load strategic data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadStrategicData();
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'on_track':
        return <TrendingUp className="h-4 w-4 text-blue-500" />;
      case 'at_risk':
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      case 'blocked':
        return <Clock className="h-4 w-4 text-red-500" />;
      default:
        return <Target className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500';
      case 'on_track':
        return 'bg-blue-500';
      case 'at_risk':
        return 'bg-yellow-500';
      case 'blocked':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const okrDistributionData = okrs.map(okr => ({
    name: okr.title.split(' ').slice(0, 3).join(' ') + '...',
    progress: okr.progress,
    status: okr.status
  }));

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Executive Summary Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5" />
                Strategic Overview
              </CardTitle>
              <CardDescription>
                Real-time OKR progress and strategic insights
              </CardDescription>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-green-600">
                {executiveSummary?.overallHealth}%
              </div>
              <div className="text-sm text-gray-500">Overall Health</div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {okrs.filter(okr => okr.status === 'completed').length}
              </div>
              <div className="text-sm text-gray-500">Completed OKRs</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-600">
                {okrs.filter(okr => okr.status === 'at_risk').length}
              </div>
              <div className="text-sm text-gray-500">At Risk OKRs</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {okrs.filter(okr => okr.status === 'on_track').length}
              </div>
              <div className="text-sm text-gray-500">On Track OKRs</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* OKR Progress Cards */}
      <div className="grid gap-4 md:grid-cols-1 lg:grid-cols-3">
        {okrs.map((okr) => (
          <Card key={okr.id} className="relative">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    {getStatusIcon(okr.status)}
                    <Badge variant={okr.status === 'at_risk' ? 'destructive' : 'default'}>
                      {okr.status.replace('_', ' ').toUpperCase()}
                    </Badge>
                  </div>
                  <CardTitle className="text-sm mt-2">{okr.title}</CardTitle>
                  <CardDescription className="text-xs">
                    Owner: {okr.owner} • Due: {new Date(okr.dueDate).toLocaleDateString()}
                  </CardDescription>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold">{okr.progress}%</div>
                </div>
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              {/* Progress Bar */}
              <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
                <div 
                  className={`h-2 rounded-full ${getStatusColor(okr.status)}`}
                  style={{ width: `${okr.progress}%` }}
                ></div>
              </div>
              
              {/* Key Results */}
              <div className="space-y-2">
                <div className="text-xs font-medium text-gray-700">Key Results:</div>
                {okr.keyResults.map((kr) => (
                  <div key={kr.id} className="flex items-center justify-between text-xs">
                    <span className="flex-1 truncate">{kr.description}</span>
                    <div className="flex items-center gap-1 ml-2">
                      {getStatusIcon(kr.status)}
                      <span className="font-medium">{kr.progress}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts and Analytics */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">OKR Progress Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={okrDistributionData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="name" 
                  fontSize={12}
                  angle={-45}
                  textAnchor="end"
                  height={60}
                />
                <YAxis fontSize={12} />
                <Tooltip />
                <Bar dataKey="progress" fill="#3B82F6" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Strategic Insights</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {executiveSummary?.keyInsights.map((insight, index) => (
              <div key={index} className="p-2 bg-blue-50 rounded text-xs">
                <div className="flex items-start gap-2">
                  <TrendingUp className="h-3 w-3 text-blue-500 mt-0.5 flex-shrink-0" />
                  <span>{insight}</span>
                </div>
              </div>
            ))}
            
            <div className="pt-2 border-t">
              <div className="text-xs font-medium text-gray-700 mb-2">
                Strategic Recommendations:
              </div>
              {executiveSummary?.strategicRecommendations.map((rec, index) => (
                <div key={index} className="p-2 bg-green-50 rounded text-xs mb-1">
                  <div className="flex items-start gap-2">
                    <Target className="h-3 w-3 text-green-500 mt-0.5 flex-shrink-0" />
                    <span>{rec}</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default StrategicOverviewPanel; 
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
import { Input } from '@/components/ui/input';
import { 
  Brain,
  TrendingUp, 
  TrendingDown, 
  AlertTriangle,
  CheckCircle,
  Clock,
  Target,
  Users,
  MessageSquare,
  Search,
  Lightbulb,
  Activity,
  BarChart3
} from 'lucide-react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Area,
  AreaChart
} from 'recharts';

interface CrossPlatformInsight {
  id: string;
  type: 'alignment' | 'bottleneck' | 'opportunity' | 'risk';
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  platforms: string[];
  impact: string;
  recommendation: string;
  confidence: number;
  timestamp: string;
}

interface PlatformStatus {
  platform: string;
  status: 'healthy' | 'warning' | 'critical';
  score: number;
  issues: number;
  lastSync: string;
  data: {
    total_items: number;
    active_items: number;
    completed_items: number;
    overdue_items: number;
  };
}

interface AlignmentAnalysis {
  overallAlignment: number;
  strategicOKRs: number;
  engineeringWork: number;
  productRoadmap: number;
  gaps: Array<{
    area: string;
    gap: string;
    impact: 'high' | 'medium' | 'low';
    recommendation: string;
  }>;
}

interface AIQuery {
  id: string;
  query: string;
  response: string;
  confidence: number;
  sources: string[];
  timestamp: string;
  insights: string[];
}

const COLORS = ['#10B981', '#F59E0B', '#EF4444', '#6B7280'];

const CrossPlatformIntelligencePanel: React.FC = () => {
  const [insights, setInsights] = useState<CrossPlatformInsight[]>([]);
  const [platformStatus, setPlatformStatus] = useState<PlatformStatus[]>([]);
  const [alignmentAnalysis, setAlignmentAnalysis] = useState<AlignmentAnalysis | null>(null);
  const [aiQueries, setAIQueries] = useState<AIQuery[]>([]);
  const [currentQuery, setCurrentQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isQuerying, setIsQuerying] = useState(false);

  // Real data from API
  const mockInsights: CrossPlatformInsight[] = [
    {
      id: '1',
      type: 'alignment',
      severity: 'high',
      title: 'Strategic OKR Misalignment Detected',
      description: 'Revenue growth OKR (Notion) not reflected in current engineering sprint (Linear)',
      platforms: ['Notion', 'Linear'],
      impact: 'Engineering team may be working on non-strategic initiatives',
      recommendation: 'Align next sprint planning with Q4 revenue objectives',
      confidence: 0.87,
      timestamp: new Date().toISOString()
    },
    {
      id: '2',
      type: 'bottleneck',
      severity: 'medium',
      title: 'Cross-Team Dependency Bottleneck',
      description: 'Product roadmap (Asana) blocked by pending engineering features (Linear)',
      platforms: ['Asana', 'Linear'],
      impact: 'Product delivery timeline at risk',
      recommendation: 'Prioritize dependent engineering tasks in next sprint',
      confidence: 0.92,
      timestamp: new Date().toISOString()
    },
    {
      id: '3',
      type: 'opportunity',
      severity: 'low',
      title: 'Customer Success Initiative Opportunity',
      description: 'High customer satisfaction in engineering but declining in product accounts',
      platforms: ['Linear', 'Asana'],
      impact: 'Opportunity to leverage engineering success patterns',
      recommendation: 'Apply engineering customer success practices to product team',
      confidence: 0.78,
      timestamp: new Date().toISOString()
    }
  ];

  const mockPlatformStatus: PlatformStatus[] = [
    {
      platform: 'Notion',
      status: 'healthy',
      score: 92,
      issues: 1,
      lastSync: '2 mins ago',
      data: { total_items: 23, active_items: 18, completed_items: 4, overdue_items: 1 }
    },
    {
      platform: 'Linear',
      status: 'warning',
      score: 78,
      issues: 3,
      lastSync: '1 min ago',
      data: { total_items: 67, active_items: 42, completed_items: 22, overdue_items: 3 }
    },
    {
      platform: 'Asana',
      status: 'healthy',
      score: 85,
      issues: 2,
      lastSync: '3 mins ago',
      data: { total_items: 45, active_items: 28, completed_items: 15, overdue_items: 2 }
    }
  ];

  const mockAlignmentAnalysis: AlignmentAnalysis = {
    overallAlignment: 74,
    strategicOKRs: 85,
    engineeringWork: 68,
    productRoadmap: 79,
    gaps: [
      {
        area: 'Engineering-Strategy Alignment',
        gap: 'Only 68% of engineering work mapped to strategic OKRs',
        impact: 'medium',
        recommendation: 'Create quarterly OKR-to-sprint mapping sessions'
      },
      {
        area: 'Product-Engineering Sync',
        gap: 'Product roadmap dependencies not reflected in Linear priorities',
        impact: 'high',
        recommendation: 'Implement automated dependency tracking between platforms'
      }
    ]
  };

  useEffect(() => {
    const loadCrossPlatformData = async () => {
      setIsLoading(true);
      try {
        // In production, this would call all MCP servers for unified analysis
        await new Promise(resolve => setTimeout(resolve, 1200));
        setInsights(mockInsights);
        setPlatformStatus(mockPlatformStatus);
        setAlignmentAnalysis(mockAlignmentAnalysis);
      } catch (error) {
        console.error('Failed to load cross-platform data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadCrossPlatformData();
  }, []);

  const handleAIQuery = async () => {
    if (!currentQuery.trim()) return;
    
    setIsQuerying(true);
    try {
      // Simulate AI query to unified MCP servers
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const mockResponse: AIQuery = {
        id: Date.now().toString(),
        query: currentQuery,
        response: currentQuery.toLowerCase().includes('alignment') 
          ? "Based on analysis across Notion OKRs, Linear tasks, and Asana projects, current strategic alignment is 74%. The main gap is between engineering work (68% aligned) and strategic objectives. I recommend quarterly alignment reviews and automated OKR-to-task mapping."
          : currentQuery.toLowerCase().includes('bottleneck')
          ? "Cross-platform analysis reveals 3 critical bottlenecks: 1) Code review delays in Linear affecting Asana product timelines, 2) Unassigned strategic initiatives in Notion, 3) Resource conflicts between teams. Priority recommendation: resolve dependency mapping between Linear and Asana."
          : "AI analysis complete. Current cross-platform health: Notion (92%), Linear (78%), Asana (85%). Key insight: Engineering velocity is high but not aligned with strategic priorities. Consider realigning sprint planning with OKR objectives.",
        confidence: 0.89,
        sources: ['Notion Strategic', 'Linear Engineering', 'Asana Product'],
        timestamp: new Date().toISOString(),
        insights: [
          "Strategic alignment can be improved by 15-20% with better OKR-to-task mapping",
          "Engineering team productivity is high but misdirected",
          "Product roadmap dependencies need clearer visualization"
        ]
      };
      
      setAIQueries(prev => [mockResponse, ...prev].slice(0, 5));
      setCurrentQuery('');
    } catch (error) {
      console.error('AI query failed:', error);
    } finally {
      setIsQuerying(false);
    }
  };

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'alignment':
        return <Target className="h-4 w-4" />;
      case 'bottleneck':
        return <AlertTriangle className="h-4 w-4" />;
      case 'opportunity':
        return <Lightbulb className="h-4 w-4" />;
      case 'risk':
        return <Clock className="h-4 w-4" />;
      default:
        return <Brain className="h-4 w-4" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'border-red-500 bg-red-50';
      case 'high':
        return 'border-orange-500 bg-orange-50';
      case 'medium':
        return 'border-yellow-500 bg-yellow-50';
      case 'low':
        return 'border-blue-500 bg-blue-50';
      default:
        return 'border-gray-500 bg-gray-50';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'text-green-500';
      case 'warning':
        return 'text-yellow-500';
      case 'critical':
        return 'text-red-500';
      default:
        return 'text-gray-500';
    }
  };

  const platformDistributionData = platformStatus.map(platform => ({
    name: platform.platform,
    total: platform.data.total_items,
    active: platform.data.active_items,
    completed: platform.data.completed_items,
    overdue: platform.data.overdue_items
  }));

  const alignmentTrendData = [
    { month: 'Jan', alignment: 65, target: 80 },
    { month: 'Feb', alignment: 68, target: 80 },
    { month: 'Mar', alignment: 71, target: 80 },
    { month: 'Apr', alignment: 74, target: 80 },
    { month: 'May', alignment: 74, target: 80 }
  ];

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with AI Query */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5" />
                Cross-Platform Intelligence
              </CardTitle>
              <CardDescription>
                AI-powered insights across Notion, Linear, and Asana
              </CardDescription>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-blue-600">
                {alignmentAnalysis?.overallAlignment}%
              </div>
              <div className="text-sm text-gray-500">Strategic Alignment</div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <Input
              placeholder="Ask AI about cross-platform patterns, bottlenecks, or alignment..."
              value={currentQuery}
              onChange={(e) => setCurrentQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAIQuery()}
              className="flex-1"
            />
            <Button onClick={handleAIQuery} disabled={isQuerying}>
              <Search className="h-4 w-4 mr-2" />
              {isQuerying ? 'Analyzing...' : 'Ask AI'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Platform Status Overview */}
      <div className="grid gap-4 md:grid-cols-3">
        {platformStatus.map((platform) => (
          <Card key={platform.platform}>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm">{platform.platform}</CardTitle>
                <div className="flex items-center gap-2">
                  <Activity className={`h-4 w-4 ${getStatusColor(platform.status)}`} />
                  <Badge variant={platform.status === 'healthy' ? 'default' : 'destructive'}>
                    {platform.status}
                  </Badge>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-2xl font-bold">{platform.score}%</span>
                <span className="text-xs text-gray-500">Health Score</span>
              </div>
              
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="text-center">
                  <div className="font-bold text-green-600">{platform.data.completed_items}</div>
                  <div className="text-gray-500">Completed</div>
                </div>
                <div className="text-center">
                  <div className="font-bold text-blue-600">{platform.data.active_items}</div>
                  <div className="text-gray-500">Active</div>
                </div>
              </div>
              
              <div className="flex items-center justify-between text-xs">
                <span>{platform.data.overdue_items} overdue</span>
                <span className="text-gray-500">Synced {platform.lastSync}</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* AI Insights */}
      {insights.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">AI-Powered Insights</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {insights.map((insight) => (
              <div 
                key={insight.id} 
                className={`p-4 rounded-lg border-l-4 ${getSeverityColor(insight.severity)}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      {getInsightIcon(insight.type)}
                      <span className="font-medium text-sm">{insight.title}</span>
                      <Badge variant="outline" className="text-xs">
                        {insight.type}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{insight.description}</p>
                    <div className="text-xs text-gray-500 mb-2">
                      <strong>Impact:</strong> {insight.impact}
                    </div>
                    <div className="text-xs text-blue-600">
                      <strong>Recommendation:</strong> {insight.recommendation}
                    </div>
                  </div>
                  <div className="text-right ml-4">
                    <div className="text-xs text-gray-500">Confidence</div>
                    <div className="text-sm font-bold">{(insight.confidence * 100).toFixed(0)}%</div>
                    <div className="text-xs text-gray-500 mt-1">
                      {insight.platforms.join(', ')}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* AI Query History */}
      {aiQueries.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Recent AI Analysis</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {aiQueries.map((query) => (
              <div key={query.id} className="border rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="text-sm font-medium mb-1">Q: {query.query}</div>
                    <div className="text-sm text-gray-600 mb-2">A: {query.response}</div>
                  </div>
                  <Badge variant="outline" className="text-xs">
                    {(query.confidence * 100).toFixed(0)}% confident
                  </Badge>
                </div>
                
                {query.insights.length > 0 && (
                  <div className="border-t pt-2 mt-2">
                    <div className="text-xs font-medium text-gray-700 mb-1">Key Insights:</div>
                    {query.insights.map((insight, index) => (
                      <div key={index} className="text-xs text-blue-600 mb-1">
                        • {insight}
                      </div>
                    ))}
                  </div>
                )}
                
                <div className="flex items-center justify-between text-xs text-gray-500 mt-2">
                  <span>Sources: {query.sources.join(', ')}</span>
                  <span>{new Date(query.timestamp).toLocaleTimeString()}</span>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Analytics Charts */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Cross-Platform Item Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={platformDistributionData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" fontSize={12} />
                <YAxis fontSize={12} />
                <Tooltip />
                <Legend />
                <Bar dataKey="active" stackId="a" fill="#3B82F6" name="Active" />
                <Bar dataKey="completed" stackId="a" fill="#10B981" name="Completed" />
                <Bar dataKey="overdue" stackId="a" fill="#EF4444" name="Overdue" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Strategic Alignment Trend</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <AreaChart data={alignmentTrendData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" fontSize={12} />
                <YAxis fontSize={12} />
                <Tooltip />
                <Legend />
                <Area type="monotone" dataKey="alignment" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.3} name="Current Alignment" />
                <Line type="monotone" dataKey="target" stroke="#10B981" strokeDasharray="5 5" name="Target" />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Alignment Analysis */}
      {alignmentAnalysis && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Strategic Alignment Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3 mb-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{alignmentAnalysis.strategicOKRs}%</div>
                <div className="text-sm text-gray-500">Strategic OKRs</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{alignmentAnalysis.engineeringWork}%</div>
                <div className="text-sm text-gray-500">Engineering Work</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{alignmentAnalysis.productRoadmap}%</div>
                <div className="text-sm text-gray-500">Product Roadmap</div>
              </div>
            </div>

            <div className="space-y-3">
              <div className="text-sm font-medium text-gray-700">Identified Gaps:</div>
              {alignmentAnalysis.gaps.map((gap, index) => (
                <div key={index} className="p-3 bg-gray-50 rounded border-l-4 border-orange-400">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-sm">{gap.area}</span>
                    <Badge variant={gap.impact === 'high' ? 'destructive' : 'default'}>
                      {gap.impact} impact
                    </Badge>
                  </div>
                  <div className="text-sm text-gray-600 mb-1">{gap.gap}</div>
                  <div className="text-xs text-blue-600">
                    <strong>Recommendation:</strong> {gap.recommendation}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default CrossPlatformIntelligencePanel; 
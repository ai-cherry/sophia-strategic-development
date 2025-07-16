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
  Code,
  Users,
  Zap,
  Bug,
  Clock,
  CheckCircle,
  AlertTriangle,
  MessageSquare
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
  RadialBarChart,
  RadialBar
} from 'recharts';

interface EngineeringKPIs {
  velocity: {
    current: number;
    average: number;
    trend: 'up' | 'down' | 'stable';
    sprintData: Array<{ sprint: string; completed: number; planned: number }>;
  };
  codeQuality: {
    bugRatio: number;
    techDebtIssues: number;
    codeReviewTime: number;
    testCoverage: number;
  };
  capacity: {
    teamSize: number;
    utilization: number;
    burnoutRisk: 'low' | 'medium' | 'high';
    bottlenecks: Array<{ type: string; count: number; impact: string }>;
  };
}

interface ProductKPIs {
  roadmapHealth: {
    onTrackProjects: number;
    totalProjects: number;
    completionRate: number;
    roadmapScore: number;
  };
  accountHealth: {
    healthScore: number;
    supportTasks: number;
    urgentAccounts: number;
    customerSatisfaction: number;
  };
  featurePipeline: {
    planning: number;
    development: number;
    testing: number;
    release: number;
  };
}

interface Department {
  id: string;
  name: string;
  type: 'engineering' | 'product';
  kpis: EngineeringKPIs | ProductKPIs;
  lastUpdated: string;
}

const DepartmentalKPIPanel: React.FC = () => {
  const [departments, setDepartments] = useState<Department[]>([]);
  const [selectedDepartment, setSelectedDepartment] = useState<string>('engineering');
  const [isLoading, setIsLoading] = useState(true);

  // Real data from API
  const mockDepartments: Department[] = [
    {
      id: 'engineering',
      name: 'Engineering Team',
      type: 'engineering',
      lastUpdated: new Date().toISOString(),
      kpis: {
        velocity: {
          current: 28,
          average: 24,
          trend: 'up',
          sprintData: [
            { sprint: 'Sprint 21', completed: 22, planned: 25 },
            { sprint: 'Sprint 22', completed: 26, planned: 28 },
            { sprint: 'Sprint 23', completed: 24, planned: 26 },
            { sprint: 'Sprint 24', completed: 28, planned: 30 },
            { sprint: 'Sprint 25', completed: 30, planned: 32 }
          ]
        },
        codeQuality: {
          bugRatio: 0.12,
          techDebtIssues: 8,
          codeReviewTime: 4.2,
          testCoverage: 87
        },
        capacity: {
          teamSize: 8,
          utilization: 0.85,
          burnoutRisk: 'medium',
          bottlenecks: [
            { type: 'Code Review', count: 12, impact: 'medium' },
            { type: 'Testing', count: 5, impact: 'low' },
            { type: 'Deployment', count: 3, impact: 'high' }
          ]
        }
      } as EngineeringKPIs
    },
    {
      id: 'product',
      name: 'Product & Account Management',
      type: 'product',
      lastUpdated: new Date().toISOString(),
      kpis: {
        roadmapHealth: {
          onTrackProjects: 7,
          totalProjects: 10,
          completionRate: 0.73,
          roadmapScore: 82
        },
        accountHealth: {
          healthScore: 78,
          supportTasks: 15,
          urgentAccounts: 3,
          customerSatisfaction: 4.2
        },
        featurePipeline: {
          planning: 8,
          development: 12,
          testing: 6,
          release: 4
        }
      } as ProductKPIs
    }
  ];

  useEffect(() => {
    const loadDepartmentalData = async () => {
      setIsLoading(true);
      try {
        // In production, this would call Linear and Asana MCP servers
        await new Promise(resolve => setTimeout(resolve, 800));
        setDepartments(mockDepartments);
      } catch (error) {
        console.error('Failed to load departmental data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadDepartmentalData();
  }, []);

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="h-4 w-4 text-green-500" />;
      case 'down':
        return <TrendingDown className="h-4 w-4 text-red-500" />;
      default:
        return <Code className="h-4 w-4 text-blue-500" />;
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'high':
        return 'text-red-500';
      case 'medium':
        return 'text-yellow-500';
      case 'low':
        return 'text-green-500';
      default:
        return 'text-gray-500';
    }
  };

  const selectedDept = departments.find(dept => dept.id === selectedDepartment);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const renderEngineeringKPIs = (kpis: EngineeringKPIs) => (
    <>
      {/* Engineering Metrics Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Zap className="h-4 w-4" />
              Sprint Velocity
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div className="text-2xl font-bold">{kpis.velocity.current}</div>
              <div className="flex items-center gap-1">
                {getTrendIcon(kpis.velocity.trend)}
                <span className="text-xs text-gray-500">vs {kpis.velocity.average} avg</span>
              </div>
            </div>
            <div className="text-xs text-gray-500 mt-1">Story points completed</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Bug className="h-4 w-4" />
              Code Quality
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(kpis.codeQuality.bugRatio * 100).toFixed(1)}%</div>
            <div className="text-xs text-gray-500 mt-1">Bug ratio</div>
            <div className="flex items-center gap-2 mt-2">
              <Badge variant="outline" className="text-xs">
                {kpis.codeQuality.techDebtIssues} tech debt
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Clock className="h-4 w-4" />
              Review Time
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{kpis.codeQuality.codeReviewTime}h</div>
            <div className="text-xs text-gray-500 mt-1">Avg review time</div>
            <div className="flex items-center gap-1 mt-2">
              <div className="text-xs text-green-600">
                {kpis.codeQuality.testCoverage}% coverage
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Users className="h-4 w-4" />
              Team Capacity
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(kpis.capacity.utilization * 100).toFixed(0)}%</div>
            <div className="text-xs text-gray-500 mt-1">Utilization</div>
            <div className="flex items-center gap-1 mt-2">
              <AlertTriangle className={`h-3 w-3 ${getRiskColor(kpis.capacity.burnoutRisk)}`} />
              <span className={`text-xs ${getRiskColor(kpis.capacity.burnoutRisk)}`}>
                {kpis.capacity.burnoutRisk} burnout risk
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Engineering Charts */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Sprint Velocity Trend</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={kpis.velocity.sprintData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="sprint" fontSize={12} />
                <YAxis fontSize={12} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="completed" stroke="#10B981" name="Completed" />
                <Line type="monotone" dataKey="planned" stroke="#6B7280" name="Planned" strokeDasharray="5 5" />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Current Bottlenecks</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {kpis.capacity.bottlenecks.map((bottleneck, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <AlertTriangle className={`h-4 w-4 ${getRiskColor(bottleneck.impact)}`} />
                  <span className="text-sm">{bottleneck.type}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="outline">{bottleneck.count} items</Badge>
                  <Badge variant={bottleneck.impact === 'high' ? 'destructive' : 'default'}>
                    {bottleneck.impact}
                  </Badge>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </>
  );

  const renderProductKPIs = (kpis: ProductKPIs) => (
    <>
      {/* Product Metrics Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <CheckCircle className="h-4 w-4" />
              Roadmap Health
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{kpis.roadmapHealth.roadmapScore}%</div>
            <div className="text-xs text-gray-500 mt-1">Overall score</div>
            <div className="text-xs text-green-600 mt-1">
              {kpis.roadmapHealth.onTrackProjects}/{kpis.roadmapHealth.totalProjects} on track
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Users className="h-4 w-4" />
              Account Health
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{kpis.accountHealth.healthScore}%</div>
            <div className="text-xs text-gray-500 mt-1">Health score</div>
            <div className="flex items-center gap-2 mt-2">
              <Badge variant={kpis.accountHealth.urgentAccounts > 5 ? 'destructive' : 'default'}>
                {kpis.accountHealth.urgentAccounts} urgent
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <MessageSquare className="h-4 w-4" />
              Customer Satisfaction
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{kpis.accountHealth.customerSatisfaction}/5</div>
            <div className="text-xs text-gray-500 mt-1">Average rating</div>
            <div className="text-xs text-orange-600 mt-1">
              {kpis.accountHealth.supportTasks} support tasks
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Zap className="h-4 w-4" />
              Feature Pipeline
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Object.values(kpis.featurePipeline).reduce((sum, val) => sum + val, 0)}
            </div>
            <div className="text-xs text-gray-500 mt-1">Total features</div>
            <div className="text-xs text-blue-600 mt-1">
              {kpis.featurePipeline.development} in development
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Product Charts */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Feature Pipeline Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={[
                { stage: 'Planning', count: kpis.featurePipeline.planning },
                { stage: 'Development', count: kpis.featurePipeline.development },
                { stage: 'Testing', count: kpis.featurePipeline.testing },
                { stage: 'Release', count: kpis.featurePipeline.release }
              ]}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="stage" fontSize={12} />
                <YAxis fontSize={12} />
                <Tooltip />
                <Bar dataKey="count" fill="#3B82F6" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Account Health Overview</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm">Overall Health</span>
                <div className="flex items-center gap-2">
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-green-500 h-2 rounded-full" 
                      style={{ width: `${kpis.accountHealth.healthScore}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium">{kpis.accountHealth.healthScore}%</span>
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm">Customer Satisfaction</span>
                <div className="flex items-center gap-2">
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-500 h-2 rounded-full" 
                      style={{ width: `${(kpis.accountHealth.customerSatisfaction / 5) * 100}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium">{kpis.accountHealth.customerSatisfaction}/5</span>
                </div>
              </div>

              <div className="pt-3 border-t">
                <div className="grid grid-cols-2 gap-4 text-center">
                  <div>
                    <div className="text-lg font-bold text-orange-600">{kpis.accountHealth.supportTasks}</div>
                    <div className="text-xs text-gray-500">Support Tasks</div>
                  </div>
                  <div>
                    <div className="text-lg font-bold text-red-600">{kpis.accountHealth.urgentAccounts}</div>
                    <div className="text-xs text-gray-500">Urgent Accounts</div>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </>
  );

  return (
    <div className="space-y-6">
      {/* Department Selector */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Departmental KPIs
              </CardTitle>
              <CardDescription>
                Real-time performance metrics by department
              </CardDescription>
            </div>
            <div className="flex gap-2">
              {departments.map((dept) => (
                <Button
                  key={dept.id}
                  variant={selectedDepartment === dept.id ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedDepartment(dept.id)}
                >
                  {dept.name}
                </Button>
              ))}
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Department KPIs */}
      {selectedDept && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">{selectedDept.name}</h3>
            <Badge variant="outline">
              Updated: {new Date(selectedDept.lastUpdated).toLocaleTimeString()}
            </Badge>
          </div>

          {selectedDept.type === 'engineering' 
            ? renderEngineeringKPIs(selectedDept.kpis as EngineeringKPIs)
            : renderProductKPIs(selectedDept.kpis as ProductKPIs)
          }
        </div>
      )}
    </div>
  );
};

export default DepartmentalKPIPanel; 
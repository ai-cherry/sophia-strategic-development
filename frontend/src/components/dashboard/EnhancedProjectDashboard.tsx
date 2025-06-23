import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Alert, AlertDescription } from '../ui/alert';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';
import {
  Calendar,
  Clock,
  Users,
  Target,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  Circle,
  MoreVertical,
  Plus,
  Filter,
  FolderOpen,
  GitBranch,
  Activity,
  BarChart3,
  Zap,
  Flag,
  MessageSquare,
  FileText,
  ExternalLink,
  Sync,
  Bell,
  DollarSign
} from 'lucide-react';
import EnhancedUnifiedChatInterface from '../shared/EnhancedUnifiedChatInterface';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

// Simplified interfaces focused on executive needs
interface ExecutiveProject {
  id: string;
  name: string;
  status: 'on-track' | 'at-risk' | 'delayed' | 'completed';
  progress: number;
  budget: number;
  spent: number;
  endDate: string;
  owner: string;
  teamSize: number;
  toolUsed: 'asana' | 'linear' | 'notion' | 'multiple';
  lastUpdate: string;
  riskLevel: 'low' | 'medium' | 'high';
  keyMetrics: {
    tasksCompleted: number;
    totalTasks: number;
    milestonesHit: number;
    totalMilestones: number;
  };
}

interface ExecutiveMetrics {
  totalProjects: number;
  onTrackProjects: number;
  atRiskProjects: number;
  delayedProjects: number;
  totalBudget: number;
  spentBudget: number;
  teamUtilization: number;
  avgProjectHealth: number;
}

interface TeamToolUsage {
  tool: 'asana' | 'linear' | 'notion' | 'slack';
  projectCount: number;
  teamMembers: number;
  lastSync: string;
  health: 'healthy' | 'warning' | 'error';
}

// Add new interfaces for organizational intelligence
interface Department {
  id: string;
  name: string;
  head: string;
  teamSize: number;
  activeProjects: number;
  kpiScore: number;
  budget: number;
  spent: number;
  primaryTool: 'asana' | 'linear' | 'notion' | 'slack';
  kpis: {
    metric: string;
    target: number;
    current: number;
    trend: 'up' | 'down' | 'stable';
  }[];
}

interface CompanyOKR {
  id: string;
  title: string;
  quarter: string;
  owner: string;
  progress: number;
  status: 'on-track' | 'at-risk' | 'delayed' | 'completed';
  keyResults: {
    description: string;
    target: number;
    current: number;
    unit: string;
  }[];
  contributingDepartments: string[];
  contributingProjects: string[];
}

interface CrossDepartmentalProject {
  id: string;
  name: string;
  departments: string[];
  primaryDepartment: string;
  secondaryDepartments: string[];
  coordinationScore: number;
  riskLevel: 'low' | 'medium' | 'high';
  blockers: string[];
}

export const EnhancedProjectDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [timeFilter, setTimeFilter] = useState('current');
  const [loading, setLoading] = useState(false);
  const [projects, setProjects] = useState<ExecutiveProject[]>([]);
  const [metrics, setMetrics] = useState<ExecutiveMetrics | null>(null);
  const [toolUsage, setToolUsage] = useState<TeamToolUsage[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [companyOKRs, setCompanyOKRs] = useState<CompanyOKR[]>([]);
  const [crossDeptProjects, setCrossDeptProjects] = useState<CrossDepartmentalProject[]>([]);

  // Enhanced chat context for organizational intelligence
  const chatContext = {
    dashboardType: 'executive-project' as const,
    userId: 'executive',
    tenantId: 'payready',
    activeFilters: { timeFilter },
    focus: 'organizational-intelligence',
    capabilities: ['cross-departmental-analysis', 'kpi-tracking', 'okr-monitoring']
  };

  useEffect(() => {
    fetchExecutiveData();
    const interval = setInterval(fetchExecutiveData, 300000); // Refresh every 5 minutes
    return () => clearInterval(interval);
  }, [timeFilter]);

  const fetchExecutiveData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        fetchProjects(),
        fetchMetrics(),
        fetchToolUsage(),
        fetchDepartments(),
        fetchCompanyOKRs(),
        fetchCrossDepartmentalProjects()
      ]);
    } catch (error) {
      console.error('Failed to fetch executive data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchProjects = async () => {
    // Mock data focused on executive visibility
    const mockProjects: ExecutiveProject[] = [
      {
        id: 'proj_001',
        name: 'Sophia AI Infrastructure Modernization',
        status: 'on-track',
        progress: 65,
        budget: 150000,
        spent: 97500,
        endDate: '2024-08-15',
        owner: 'Mike Johnson',
        teamSize: 3,
        toolUsed: 'linear',
        lastUpdate: '2024-07-20T10:30:00Z',
        riskLevel: 'low',
        keyMetrics: {
          tasksCompleted: 23,
          totalTasks: 35,
          milestonesHit: 3,
          totalMilestones: 5
        }
      },
      {
        id: 'proj_002',
        name: 'NMHC Top 50 Integration',
        status: 'at-risk',
        progress: 40,
        budget: 200000,
        spent: 80000,
        endDate: '2024-09-30',
        owner: 'Sarah Smith',
        teamSize: 4,
        toolUsed: 'asana',
        lastUpdate: '2024-07-20T09:15:00Z',
        riskLevel: 'medium',
        keyMetrics: {
          tasksCompleted: 12,
          totalTasks: 28,
          milestonesHit: 1,
          totalMilestones: 4
        }
      },
      {
        id: 'proj_003',
        name: 'Q3 Strategic Planning',
        status: 'on-track',
        progress: 75,
        budget: 50000,
        spent: 37500,
        endDate: '2024-09-15',
        owner: 'Lynn Musil',
        teamSize: 5,
        toolUsed: 'notion',
        lastUpdate: '2024-07-20T11:00:00Z',
        riskLevel: 'low',
        keyMetrics: {
          tasksCompleted: 18,
          totalTasks: 24,
          milestonesHit: 4,
          totalMilestones: 5
        }
      },
      {
        id: 'proj_004',
        name: 'Customer Success Platform',
        status: 'delayed',
        progress: 25,
        budget: 120000,
        spent: 45000,
        endDate: '2024-08-30',
        owner: 'Emily Chen',
        teamSize: 2,
        toolUsed: 'multiple',
        lastUpdate: '2024-07-19T16:45:00Z',
        riskLevel: 'high',
        keyMetrics: {
          tasksCompleted: 8,
          totalTasks: 32,
          milestonesHit: 1,
          totalMilestones: 6
        }
      }
    ];
    setProjects(mockProjects);
  };

  const fetchMetrics = async () => {
    const mockMetrics: ExecutiveMetrics = {
      totalProjects: 4,
      onTrackProjects: 2,
      atRiskProjects: 1,
      delayedProjects: 1,
      totalBudget: 520000,
      spentBudget: 260000,
      teamUtilization: 85,
      avgProjectHealth: 72
    };
    setMetrics(mockMetrics);
  };

  const fetchToolUsage = async () => {
    const mockToolUsage: TeamToolUsage[] = [
      {
        tool: 'asana',
        projectCount: 1,
        teamMembers: 4,
        lastSync: '2024-07-20T09:15:00Z',
        health: 'warning'
      },
      {
        tool: 'linear',
        projectCount: 1,
        teamMembers: 3,
        lastSync: '2024-07-20T10:30:00Z',
        health: 'healthy'
      },
      {
        tool: 'notion',
        projectCount: 1,
        teamMembers: 5,
        lastSync: '2024-07-20T11:00:00Z',
        health: 'healthy'
      },
      {
        tool: 'slack',
        projectCount: 4,
        teamMembers: 8,
        lastSync: '2024-07-20T11:05:00Z',
        health: 'healthy'
      }
    ];
    setToolUsage(mockToolUsage);
  };

  const fetchDepartments = async () => {
    const mockDepartments: Department[] = [
      {
        id: 'dept_eng',
        name: 'Engineering',
        head: 'Mike Johnson',
        teamSize: 8,
        activeProjects: 3,
        kpiScore: 87,
        budget: 250000,
        spent: 162500,
        primaryTool: 'linear',
        kpis: [
          { metric: 'Sprint Velocity', target: 50, current: 53, trend: 'up' },
          { metric: 'Bug Resolution Time', target: 24, current: 18, trend: 'up' },
          { metric: 'Code Quality Score', target: 85, current: 89, trend: 'up' }
        ]
      },
      {
        id: 'dept_product',
        name: 'Product',
        head: 'Sarah Smith',
        teamSize: 5,
        activeProjects: 4,
        kpiScore: 78,
        budget: 180000,
        spent: 117000,
        primaryTool: 'asana',
        kpis: [
          { metric: 'Feature Delivery Rate', target: 12, current: 10, trend: 'down' },
          { metric: 'User Satisfaction', target: 90, current: 92, trend: 'up' },
          { metric: 'Time to Market', target: 30, current: 35, trend: 'down' }
        ]
      },
      {
        id: 'dept_strategy',
        name: 'Strategy',
        head: 'Lynn Musil',
        teamSize: 3,
        activeProjects: 2,
        kpiScore: 92,
        budget: 90000,
        spent: 67500,
        primaryTool: 'notion',
        kpis: [
          { metric: 'Strategic Initiative Progress', target: 80, current: 85, trend: 'up' },
          { metric: 'Market Analysis Completion', target: 100, current: 95, trend: 'stable' },
          { metric: 'Competitive Response Time', target: 48, current: 36, trend: 'up' }
        ]
      }
    ];
    setDepartments(mockDepartments);
  };

  const fetchCompanyOKRs = async () => {
    const mockOKRs: CompanyOKR[] = [
      {
        id: 'okr_q3_growth',
        title: 'Accelerate Customer Acquisition',
        quarter: 'Q3 2024',
        owner: 'Lynn Musil',
        progress: 72,
        status: 'on-track',
        keyResults: [
          { description: 'Increase MRR', target: 500000, current: 360000, unit: '$' },
          { description: 'New Enterprise Customers', target: 25, current: 18, unit: 'customers' },
          { description: 'Customer Acquisition Cost', target: 5000, current: 4200, unit: '$' }
        ],
        contributingDepartments: ['Product', 'Engineering', 'Strategy'],
        contributingProjects: ['proj_002', 'proj_003']
      },
      {
        id: 'okr_q3_platform',
        title: 'Platform Modernization',
        quarter: 'Q3 2024',
        owner: 'Mike Johnson',
        progress: 65,
        status: 'on-track',
        keyResults: [
          { description: 'Infrastructure Uptime', target: 99.9, current: 99.7, unit: '%' },
          { description: 'API Response Time', target: 200, current: 180, unit: 'ms' },
          { description: 'Security Compliance Score', target: 95, current: 92, unit: '%' }
        ],
        contributingDepartments: ['Engineering'],
        contributingProjects: ['proj_001']
      },
      {
        id: 'okr_q3_efficiency',
        title: 'Operational Excellence',
        quarter: 'Q3 2024',
        owner: 'Sarah Smith',
        progress: 58,
        status: 'at-risk',
        keyResults: [
          { description: 'Process Automation', target: 80, current: 45, unit: '%' },
          { description: 'Team Productivity Index', target: 90, current: 78, unit: 'score' },
          { description: 'Customer Support Response', target: 2, current: 4, unit: 'hours' }
        ],
        contributingDepartments: ['Product', 'Engineering'],
        contributingProjects: ['proj_004']
      }
    ];
    setCompanyOKRs(mockOKRs);
  };

  const fetchCrossDepartmentalProjects = async () => {
    const mockCrossProjects: CrossDepartmentalProject[] = [
      {
        id: 'proj_002',
        name: 'NMHC Top 50 Integration',
        departments: ['Product', 'Engineering', 'Strategy'],
        primaryDepartment: 'Product',
        secondaryDepartments: ['Engineering', 'Strategy'],
        coordinationScore: 78,
        riskLevel: 'medium',
        blockers: ['API dependencies', 'Resource allocation conflicts']
      },
      {
        id: 'proj_004',
        name: 'Customer Success Platform',
        departments: ['Product', 'Engineering'],
        primaryDepartment: 'Product',
        secondaryDepartments: ['Engineering'],
        coordinationScore: 65,
        riskLevel: 'high',
        blockers: ['Cross-team communication', 'Competing priorities']
      }
    ];
    setCrossDeptProjects(mockCrossProjects);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'on-track':
        return 'text-green-600 bg-green-50';
      case 'at-risk':
        return 'text-yellow-600 bg-yellow-50';
      case 'delayed':
        return 'text-red-600 bg-red-50';
      case 'completed':
        return 'text-blue-600 bg-blue-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'on-track':
        return <CheckCircle2 className="h-4 w-4" />;
      case 'at-risk':
      case 'delayed':
        return <AlertTriangle className="h-4 w-4" />;
      default:
        return <Activity className="h-4 w-4" />;
    }
  };

  const getRiskBadgeVariant = (risk: string): "default" | "secondary" | "destructive" | "outline" => {
    switch (risk) {
      case 'high':
        return 'destructive';
      case 'medium':
        return 'default';
      case 'low':
        return 'secondary';
      default:
        return 'outline';
    }
  };

  const getToolIcon = (tool: string) => {
    switch (tool) {
      case 'asana':
        return '🔺';
      case 'linear':
        return '⚡';
      case 'notion':
        return '📝';
      case 'slack':
        return '💬';
      case 'multiple':
        return '🔄';
      default:
        return '📊';
    }
  };

  const getHealthColor = (health: string) => {
    switch (health) {
      case 'healthy':
        return 'text-green-600';
      case 'warning':
        return 'text-yellow-600';
      case 'error':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return '↑';
      case 'down':
        return '↓';
      default:
        return '→';
    }
  };

  // Executive-focused data transformations
  const projectHealthData = projects.map((p) => ({
    name: p.name.split(' ').slice(0, 2).join(' '), // Shortened names
    progress: p.progress,
    budget: Math.round((p.spent / p.budget) * 100),
    risk: p.riskLevel === 'high' ? 100 : p.riskLevel === 'medium' ? 60 : 20
  }));

  const toolDistributionData = [
    { name: 'Asana', value: toolUsage.find(t => t.tool === 'asana')?.projectCount || 0, color: '#f06a6a' },
    { name: 'Linear', value: toolUsage.find(t => t.tool === 'linear')?.projectCount || 0, color: '#5e6ad2' },
    { name: 'Notion', value: toolUsage.find(t => t.tool === 'notion')?.projectCount || 0, color: '#37352f' },
    { name: 'Multiple', value: projects.filter((p) => p.toolUsed === 'multiple').length, color: '#0ea5e9' }
  ];

  const budgetTrendData = [
    { month: 'May', planned: 180, actual: 165 },
    { month: 'Jun', planned: 220, actual: 210 },
    { month: 'Jul', planned: 260, actual: 260 },
    { month: 'Aug', planned: 320, actual: 285 },
    { month: 'Sep', planned: 380, actual: 350 }
  ];

  if (!metrics) return <div>Loading...</div>;

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Executive Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Executive Project Overview</h1>
          <p className="text-gray-600 mt-1">Unified visibility across team tools and project status</p>
        </div>
        <div className="flex items-center gap-2">
          <Select value={timeFilter} onValueChange={setTimeFilter}>
            <SelectTrigger className="w-32">
              <SelectValue placeholder="Time Period" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="current">Current</SelectItem>
              <SelectItem value="quarter">This Quarter</SelectItem>
              <SelectItem value="year">This Year</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Executive KPI Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Project Health
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.avgProjectHealth}%</div>
            <p className="text-xs text-gray-500">
              {metrics.onTrackProjects} on track, {metrics.atRiskProjects} at risk
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
              <DollarSign className="h-4 w-4" />
              Budget Usage
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Math.round((metrics.spentBudget / metrics.totalBudget) * 100)}%
            </div>
            <p className="text-xs text-gray-500">
              ${(metrics.spentBudget / 1000).toFixed(0)}k of ${(metrics.totalBudget / 1000).toFixed(0)}k
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
              <Users className="h-4 w-4" />
              Team Utilization
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.teamUtilization}%</div>
            <p className="text-xs text-gray-500">Across all project tools</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              On-Time Delivery
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Math.round((metrics.onTrackProjects / metrics.totalProjects) * 100)}%
            </div>
            <p className="text-xs text-gray-500">Projects meeting deadlines</p>
          </CardContent>
        </Card>
      </div>

      {/* Main Executive Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Portfolio Overview</TabsTrigger>
          <TabsTrigger value="projects">Project Status</TabsTrigger>
          <TabsTrigger value="departments">Department KPIs</TabsTrigger>
          <TabsTrigger value="okrs">Company OKRs</TabsTrigger>
          <TabsTrigger value="tools">Tool Usage</TabsTrigger>
        </TabsList>

        {/* Portfolio Overview */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid gap-6 lg:grid-cols-2">
            {/* Project Health Overview */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Project Performance
                </CardTitle>
                <CardDescription>Progress vs Budget vs Risk across all projects</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={projectHealthData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="progress" fill="#82ca9d" name="Progress %" />
                    <Bar dataKey="budget" fill="#8884d8" name="Budget Used %" />
                    <Bar dataKey="risk" fill="#ff7c7c" name="Risk Level" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Tool Distribution */}
            <Card>
              <CardHeader>
                <CardTitle>Team Tool Usage</CardTitle>
                <CardDescription>Projects distributed across team tools</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={toolDistributionData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {toolDistributionData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
                <div className="grid grid-cols-2 gap-2 mt-4">
                  {toolDistributionData.map((item, index) => (
                    <div key={index} className="flex items-center gap-2">
                      <div 
                        className="w-3 h-3 rounded-full" 
                        style={{ backgroundColor: item.color }}
                      />
                      <span className="text-sm text-gray-600">
                        {item.name}: {item.value} projects
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Budget Trend */}
          <Card>
            <CardHeader>
              <CardTitle>Budget Trend</CardTitle>
              <CardDescription>Planned vs actual spending across all projects</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={budgetTrendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="planned" 
                    stroke="#8884d8" 
                    strokeWidth={2}
                    name="Planned ($k)"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="actual" 
                    stroke="#82ca9d" 
                    strokeWidth={2}
                    name="Actual ($k)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Project Status */}
        <TabsContent value="projects" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Project Status Overview</CardTitle>
              <CardDescription>Executive view of all active projects regardless of tool used</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Project</TableHead>
                    <TableHead>Owner</TableHead>
                    <TableHead>Tool Used</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Progress</TableHead>
                    <TableHead>Budget</TableHead>
                    <TableHead>Risk</TableHead>
                    <TableHead>Due Date</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {projects.map((project) => (
                    <TableRow key={project.id}>
                      <TableCell className="font-medium">{project.name}</TableCell>
                      <TableCell>{project.owner}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className="text-xs">
                          {getToolIcon(project.toolUsed)} {project.toolUsed}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className={`flex items-center gap-2 px-2 py-1 rounded-md ${getStatusColor(project.status)}`}>
                          {getStatusIcon(project.status)}
                          <span className="text-sm font-medium capitalize">
                            {project.status.replace('-', ' ')}
                          </span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="space-y-1">
                          <Progress value={project.progress} className="h-2 w-20" />
                          <span className="text-xs text-gray-500">{project.progress}%</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="text-sm">
                          <div>${(project.spent / 1000).toFixed(0)}k / ${(project.budget / 1000).toFixed(0)}k</div>
                          <div className="text-xs text-gray-500">
                            {Math.round((project.spent / project.budget) * 100)}% used
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant={getRiskBadgeVariant(project.riskLevel)}>
                          {project.riskLevel}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="text-sm">
                          {new Date(project.endDate).toLocaleDateString()}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Department KPIs */}
        <TabsContent value="departments" className="space-y-4">
          <div className="grid gap-4">
            {departments.map((dept) => (
              <Card key={dept.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-lg">{dept.name} Department</CardTitle>
                      <CardDescription>Led by {dept.head} • {dept.teamSize} team members</CardDescription>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold">{dept.kpiScore}%</div>
                      <div className="text-xs text-gray-500">KPI Score</div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <div className="text-sm text-gray-600">Active Projects</div>
                        <div className="text-lg font-semibold">{dept.activeProjects}</div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-600">Budget Usage</div>
                        <div className="text-lg font-semibold">
                          ${(dept.spent / 1000).toFixed(0)}k / ${(dept.budget / 1000).toFixed(0)}k
                        </div>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <div className="text-sm font-medium text-gray-700">Key Performance Indicators</div>
                      {dept.kpis.map((kpi, index) => (
                        <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-medium">{kpi.metric}</span>
                            <span className="text-lg">{getTrendIcon(kpi.trend)}</span>
                          </div>
                          <div className="text-sm">
                            <span className={kpi.current >= kpi.target ? 'text-green-600' : 'text-red-600'}>
                              {kpi.current}
                            </span>
                            <span className="text-gray-500"> / {kpi.target}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Company OKRs */}
        <TabsContent value="okrs" className="space-y-4">
          <div className="grid gap-4">
            {companyOKRs.map((okr) => (
              <Card key={okr.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-lg">{okr.title}</CardTitle>
                      <CardDescription>{okr.quarter} • Owner: {okr.owner}</CardDescription>
                    </div>
                    <div className={`flex items-center gap-2 px-3 py-1 rounded-md ${getStatusColor(okr.status)}`}>
                      {getStatusIcon(okr.status)}
                      <span className="text-sm font-medium">{okr.progress}%</span>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <Progress value={okr.progress} className="h-2" />
                    <div className="space-y-3">
                      {okr.keyResults.map((kr, index) => (
                        <div key={index} className="space-y-1">
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-medium">{kr.description}</span>
                            <span className="text-sm text-gray-600">
                              {kr.current} / {kr.target} {kr.unit}
                            </span>
                          </div>
                          <Progress 
                            value={Math.round((kr.current / kr.target) * 100)} 
                            className="h-1"
                          />
                        </div>
                      ))}
                    </div>
                    <div className="flex items-center gap-4 pt-2 border-t">
                      <div className="text-xs text-gray-600">
                        Contributing: {okr.contributingDepartments.join(', ')}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Tool Usage */}
        <TabsContent value="tools" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {toolUsage.map((tool) => (
              <Card key={tool.tool}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg flex items-center gap-2">
                      <span className="text-2xl">{getToolIcon(tool.tool)}</span>
                      {tool.tool.charAt(0).toUpperCase() + tool.tool.slice(1)}
                    </CardTitle>
                    <Badge 
                      variant={tool.health === 'healthy' ? 'secondary' : tool.health === 'warning' ? 'default' : 'destructive'}
                    >
                      {tool.health}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <div className="text-sm text-gray-600">Projects</div>
                        <div className="text-2xl font-bold">{tool.projectCount}</div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-600">Team Members</div>
                        <div className="text-2xl font-bold">{tool.teamMembers}</div>
                      </div>
                    </div>
                    <div className="pt-3 border-t">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Last Sync</span>
                        <span className={getHealthColor(tool.health)}>
                          {new Date(tool.lastSync).toLocaleString()}
                        </span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Cross-Departmental Projects */}
          <Card>
            <CardHeader>
              <CardTitle>Cross-Departmental Coordination</CardTitle>
              <CardDescription>Projects requiring multi-department collaboration</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {crossDeptProjects.map((project) => (
                  <div key={project.id} className="p-4 border rounded-lg space-y-3">
                    <div className="flex items-center justify-between">
                      <h4 className="font-medium">{project.name}</h4>
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-gray-600">Coordination Score:</span>
                        <span className="font-semibold">{project.coordinationScore}%</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <span className="text-gray-600">Departments:</span>
                      {project.departments.map((dept, index) => (
                        <Badge key={index} variant="outline">
                          {dept}
                        </Badge>
                      ))}
                    </div>
                    {project.blockers.length > 0 && (
                      <div className="space-y-1">
                        <span className="text-sm font-medium text-red-600">Blockers:</span>
                        <ul className="text-sm text-gray-600 list-disc list-inside">
                          {project.blockers.map((blocker, index) => (
                            <li key={index}>{blocker}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* AI Chat Interface */}
      <div className="fixed bottom-4 right-4 z-50">
        <EnhancedUnifiedChatInterface context={chatContext} />
      </div>
    </div>
  );
};

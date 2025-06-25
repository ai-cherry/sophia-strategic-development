import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Legend
} from 'recharts';
import {
  Calendar,
  Users,
  CheckCircle,
  AlertTriangle,
  Clock,
  TrendingUp,
  TrendingDown,
  Target,
  Activity,
  Filter,
  Search,
  RefreshCw,
  Download,
  Eye,
  BarChart3,
  PieChart as PieChartIcon
} from 'lucide-react';

// Types for Asana project data
interface AsanaProject {
  project_gid: string;
  project_name: string;
  health_score: number;
  completion_percentage: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  task_count: number;
  completed_task_count: number;
  overdue_tasks: number;
  team_name: string;
  owner_name: string;
  due_date?: string;
  created_at: string;
  ai_insights?: {
    summary?: string;
    risk_factors?: string[];
    recommendations?: string[];
  };
}

interface AsanaTask {
  task_gid: string;
  task_name: string;
  task_status: 'completed' | 'in_progress' | 'overdue' | 'due_soon';
  assignee_name?: string;
  project_name: string;
  due_date?: string;
  priority_level: 'low' | 'medium' | 'high';
  ai_urgency_score: number;
}

interface TeamProductivity {
  team_name: string;
  productivity_score: number;
  active_projects: number;
  completion_rate: number;
  team_velocity: number;
  member_count: number;
}

interface ProjectIntelligenceReport {
  generated_at: string;
  project_metrics: AsanaProject[];
  team_productivity: TeamProductivity[];
  summary: {
    overall_health_score: number;
    average_completion: number;
    total_projects: number;
    total_overdue_tasks: number;
    projects_needing_attention: Array<{
      name: string;
      health_score: number;
      risk_level: string;
    }>;
    key_insights: string[];
  };
}

// Risk level colors
const RISK_COLORS = {
  low: '#10b981',      // green
  medium: '#f59e0b',   // yellow
  high: '#ef4444',     // red
  critical: '#7c2d12'  // dark red
};

const AsanaProjectManagementDashboard: React.FC = () => {
  // State management
  const [intelligenceReport, setIntelligenceReport] = useState<ProjectIntelligenceReport | null>(null);
  const [selectedProject, setSelectedProject] = useState<AsanaProject | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  
  // Filters and search
  const [searchTerm, setSearchTerm] = useState('');
  const [teamFilter, setTeamFilter] = useState<string>('all');
  const [riskFilter, setRiskFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  
  // View settings
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [sortBy, setSortBy] = useState<'health_score' | 'completion' | 'due_date' | 'risk'>('health_score');

  // Fetch project intelligence data
  const fetchIntelligenceReport = useCallback(async () => {
    try {
      setRefreshing(true);
      const response = await fetch('/api/asana/intelligence-report', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch intelligence report: ${response.statusText}`);
      }

      const data = await response.json();
      setIntelligenceReport(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching intelligence report:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch intelligence report');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  // Initial data load
  useEffect(() => {
    fetchIntelligenceReport();
  }, [fetchIntelligenceReport]);

  // Filter and sort projects
  const filteredProjects = React.useMemo(() => {
    if (!intelligenceReport?.project_metrics) return [];

    let filtered = intelligenceReport.project_metrics.filter(project => {
      const matchesSearch = project.project_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           project.team_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           project.owner_name?.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesTeam = teamFilter === 'all' || project.team_name === teamFilter;
      const matchesRisk = riskFilter === 'all' || project.risk_level === riskFilter;
      
      let matchesStatus = true;
      if (statusFilter === 'completed') {
        matchesStatus = project.completion_percentage === 100;
      } else if (statusFilter === 'at_risk') {
        matchesStatus = project.risk_level === 'high' || project.risk_level === 'critical';
      } else if (statusFilter === 'on_track') {
        matchesStatus = project.health_score >= 0.7 && project.risk_level === 'low';
      }

      return matchesSearch && matchesTeam && matchesRisk && matchesStatus;
    });

    // Sort projects
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'health_score':
          return b.health_score - a.health_score;
        case 'completion':
          return b.completion_percentage - a.completion_percentage;
        case 'due_date':
          if (!a.due_date && !b.due_date) return 0;
          if (!a.due_date) return 1;
          if (!b.due_date) return -1;
          return new Date(a.due_date).getTime() - new Date(b.due_date).getTime();
        case 'risk':
          const riskOrder = { critical: 4, high: 3, medium: 2, low: 1 };
          return riskOrder[b.risk_level] - riskOrder[a.risk_level];
        default:
          return 0;
      }
    });

    return filtered;
  }, [intelligenceReport, searchTerm, teamFilter, riskFilter, statusFilter, sortBy]);

  // Get unique teams for filter
  const availableTeams = React.useMemo(() => {
    if (!intelligenceReport?.project_metrics) return [];
    const teams = new Set(intelligenceReport.project_metrics.map(p => p.team_name).filter(Boolean));
    return Array.from(teams).sort();
  }, [intelligenceReport]);

  // Health score color
  const getHealthScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    if (score >= 0.4) return 'text-orange-600';
    return 'text-red-600';
  };

  // Risk badge variant
  const getRiskBadgeVariant = (risk: string) => {
    switch (risk) {
      case 'low': return 'default';
      case 'medium': return 'secondary';
      case 'high': return 'destructive';
      case 'critical': return 'destructive';
      default: return 'default';
    }
  };

  // Project card component
  const ProjectCard: React.FC<{ project: AsanaProject }> = ({ project }) => (
    <Card 
      className="cursor-pointer hover:shadow-md transition-shadow"
      onClick={() => setSelectedProject(project)}
    >
      <CardHeader className="pb-3">
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <CardTitle className="text-lg font-semibold truncate">
              {project.project_name}
            </CardTitle>
            <CardDescription className="text-sm text-gray-600">
              {project.team_name} • {project.owner_name}
            </CardDescription>
          </div>
          <Badge variant={getRiskBadgeVariant(project.risk_level)}>
            {project.risk_level}
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="space-y-3">
          {/* Health Score */}
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium">Health Score</span>
            <span className={`text-sm font-bold ${getHealthScoreColor(project.health_score)}`}>
              {(project.health_score * 100).toFixed(0)}%
            </span>
          </div>
          
          {/* Progress */}
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span>Progress</span>
              <span>{project.completion_percentage.toFixed(0)}%</span>
            </div>
            <Progress value={project.completion_percentage} className="h-2" />
          </div>
          
          {/* Task Summary */}
          <div className="flex justify-between text-sm">
            <div className="flex items-center gap-1">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <span>{project.completed_task_count}/{project.task_count}</span>
            </div>
            {project.overdue_tasks > 0 && (
              <div className="flex items-center gap-1 text-red-600">
                <Clock className="h-4 w-4" />
                <span>{project.overdue_tasks} overdue</span>
              </div>
            )}
          </div>
          
          {/* Due Date */}
          {project.due_date && (
            <div className="flex items-center gap-1 text-sm text-gray-600">
              <Calendar className="h-4 w-4" />
              <span>Due: {new Date(project.due_date).toLocaleDateString()}</span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );

  // Team productivity chart data
  const teamProductivityData = React.useMemo(() => {
    if (!intelligenceReport?.team_productivity) return [];
    return intelligenceReport.team_productivity.map(team => ({
      name: team.team_name,
      productivity: Math.round(team.productivity_score * 100),
      velocity: team.team_velocity,
      completion_rate: Math.round(team.completion_rate),
      active_projects: team.active_projects
    }));
  }, [intelligenceReport]);

  // Risk distribution data
  const riskDistributionData = React.useMemo(() => {
    if (!intelligenceReport?.project_metrics) return [];
    
    const distribution = intelligenceReport.project_metrics.reduce((acc, project) => {
      acc[project.risk_level] = (acc[project.risk_level] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return Object.entries(distribution).map(([risk, count]) => ({
      name: risk,
      value: count,
      color: RISK_COLORS[risk as keyof typeof RISK_COLORS]
    }));
  }, [intelligenceReport]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-2" />
          <p>Loading Asana project intelligence...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>
          {error}
          <Button 
            variant="outline" 
            size="sm" 
            className="ml-2"
            onClick={fetchIntelligenceReport}
          >
            Retry
          </Button>
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Asana Project Intelligence</h1>
          <p className="text-gray-600">
            AI-powered project management insights and analytics
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={fetchIntelligenceReport}
            disabled={refreshing}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      {intelligenceReport?.summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Overall Health</p>
                  <p className={`text-2xl font-bold ${getHealthScoreColor(intelligenceReport.summary.overall_health_score)}`}>
                    {(intelligenceReport.summary.overall_health_score * 100).toFixed(0)}%
                  </p>
                </div>
                <Activity className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Projects</p>
                  <p className="text-2xl font-bold">{intelligenceReport.summary.total_projects}</p>
                </div>
                <Target className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Avg Completion</p>
                  <p className="text-2xl font-bold">{intelligenceReport.summary.average_completion.toFixed(0)}%</p>
                </div>
                <TrendingUp className="h-8 w-8 text-purple-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Overdue Tasks</p>
                  <p className="text-2xl font-bold text-red-600">{intelligenceReport.summary.total_overdue_tasks}</p>
                </div>
                <Clock className="h-8 w-8 text-red-600" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Content Tabs */}
      <Tabs defaultValue="projects" className="space-y-4">
        <TabsList>
          <TabsTrigger value="projects">Projects</TabsTrigger>
          <TabsTrigger value="teams">Team Analytics</TabsTrigger>
          <TabsTrigger value="insights">AI Insights</TabsTrigger>
          <TabsTrigger value="tasks">Task Management</TabsTrigger>
        </TabsList>

        {/* Projects Tab */}
        <TabsContent value="projects" className="space-y-4">
          {/* Filters */}
          <Card>
            <CardContent className="p-4">
              <div className="flex flex-wrap gap-4 items-center">
                <div className="flex-1 min-w-64">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="Search projects, teams, or owners..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>
                
                <Select value={teamFilter} onValueChange={setTeamFilter}>
                  <SelectTrigger className="w-48">
                    <SelectValue placeholder="Filter by team" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Teams</SelectItem>
                    {availableTeams.map(team => (
                      <SelectItem key={team} value={team}>{team}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>

                <Select value={riskFilter} onValueChange={setRiskFilter}>
                  <SelectTrigger className="w-32">
                    <SelectValue placeholder="Risk" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Risk</SelectItem>
                    <SelectItem value="low">Low</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                    <SelectItem value="critical">Critical</SelectItem>
                  </SelectContent>
                </Select>

                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger className="w-32">
                    <SelectValue placeholder="Status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Status</SelectItem>
                    <SelectItem value="on_track">On Track</SelectItem>
                    <SelectItem value="at_risk">At Risk</SelectItem>
                    <SelectItem value="completed">Completed</SelectItem>
                  </SelectContent>
                </Select>

                <Select value={sortBy} onValueChange={setSortBy as (value: string) => void}>
                  <SelectTrigger className="w-40">
                    <SelectValue placeholder="Sort by" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="health_score">Health Score</SelectItem>
                    <SelectItem value="completion">Completion</SelectItem>
                    <SelectItem value="due_date">Due Date</SelectItem>
                    <SelectItem value="risk">Risk Level</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Projects Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredProjects.map(project => (
              <ProjectCard key={project.project_gid} project={project} />
            ))}
          </div>

          {filteredProjects.length === 0 && (
            <Card>
              <CardContent className="p-8 text-center">
                <p className="text-gray-500">No projects match your current filters.</p>
                <Button 
                  variant="outline" 
                  className="mt-2"
                  onClick={() => {
                    setSearchTerm('');
                    setTeamFilter('all');
                    setRiskFilter('all');
                    setStatusFilter('all');
                  }}
                >
                  Clear Filters
                </Button>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Team Analytics Tab */}
        <TabsContent value="teams" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Team Productivity Chart */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Team Productivity Scores
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={teamProductivityData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="productivity" fill="#3b82f6" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Risk Distribution */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PieChartIcon className="h-5 w-5" />
                  Risk Distribution
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={riskDistributionData}
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name, value }) => `${name}: ${value}`}
                    >
                      {riskDistributionData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Team Details Table */}
          <Card>
            <CardHeader>
              <CardTitle>Team Performance Details</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-2">Team</th>
                      <th className="text-left p-2">Productivity Score</th>
                      <th className="text-left p-2">Active Projects</th>
                      <th className="text-left p-2">Completion Rate</th>
                      <th className="text-left p-2">Velocity</th>
                      <th className="text-left p-2">Members</th>
                    </tr>
                  </thead>
                  <tbody>
                    {intelligenceReport?.team_productivity.map(team => (
                      <tr key={team.team_name} className="border-b">
                        <td className="p-2 font-medium">{team.team_name}</td>
                        <td className="p-2">
                          <span className={getHealthScoreColor(team.productivity_score)}>
                            {(team.productivity_score * 100).toFixed(0)}%
                          </span>
                        </td>
                        <td className="p-2">{team.active_projects}</td>
                        <td className="p-2">{team.completion_rate.toFixed(1)}%</td>
                        <td className="p-2">{team.team_velocity.toFixed(1)}</td>
                        <td className="p-2">{team.member_count}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* AI Insights Tab */}
        <TabsContent value="insights" className="space-y-4">
          {/* Key Insights */}
          <Card>
            <CardHeader>
              <CardTitle>Key AI Insights</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {intelligenceReport?.summary.key_insights.map((insight, index) => (
                  <div key={index} className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                    <TrendingUp className="h-5 w-5 text-blue-600 mt-0.5" />
                    <p className="text-sm">{insight}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Projects Needing Attention */}
          {intelligenceReport?.summary.projects_needing_attention && 
           intelligenceReport.summary.projects_needing_attention.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5 text-orange-600" />
                  Projects Needing Attention
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {intelligenceReport.summary.projects_needing_attention.map((project, index) => (
                    <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                      <div>
                        <p className="font-medium">{project.name}</p>
                        <p className="text-sm text-gray-600">
                          Health: {(project.health_score * 100).toFixed(0)}%
                        </p>
                      </div>
                      <Badge variant={getRiskBadgeVariant(project.risk_level)}>
                        {project.risk_level}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Tasks Tab */}
        <TabsContent value="tasks" className="space-y-4">
          <Card>
            <CardContent className="p-8 text-center">
              <Clock className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <p className="text-gray-500 mb-2">Task management view coming soon</p>
              <p className="text-sm text-gray-400">
                This will show detailed task analytics, overdue items, and individual task insights.
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Project Detail Modal */}
      {selectedProject && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto m-4">
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="text-xl">{selectedProject.project_name}</CardTitle>
                  <CardDescription>
                    {selectedProject.team_name} • {selectedProject.owner_name}
                  </CardDescription>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setSelectedProject(null)}
                >
                  ×
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Project metrics */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Health Score</p>
                  <p className={`text-lg font-bold ${getHealthScoreColor(selectedProject.health_score)}`}>
                    {(selectedProject.health_score * 100).toFixed(0)}%
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Completion</p>
                  <p className="text-lg font-bold">{selectedProject.completion_percentage.toFixed(0)}%</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Tasks</p>
                  <p className="text-lg font-bold">
                    {selectedProject.completed_task_count}/{selectedProject.task_count}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Risk Level</p>
                  <Badge variant={getRiskBadgeVariant(selectedProject.risk_level)}>
                    {selectedProject.risk_level}
                  </Badge>
                </div>
              </div>

              {/* AI Insights */}
              {selectedProject.ai_insights && (
                <div className="space-y-3">
                  {selectedProject.ai_insights.summary && (
                    <div>
                      <p className="font-medium text-sm mb-2">AI Summary</p>
                      <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded">
                        {selectedProject.ai_insights.summary}
                      </p>
                    </div>
                  )}
                  
                  {selectedProject.ai_insights.risk_factors && selectedProject.ai_insights.risk_factors.length > 0 && (
                    <div>
                      <p className="font-medium text-sm mb-2">Risk Factors</p>
                      <ul className="space-y-1">
                        {selectedProject.ai_insights.risk_factors.map((factor, index) => (
                          <li key={index} className="text-sm text-red-700 flex items-start gap-2">
                            <AlertTriangle className="h-4 w-4 mt-0.5" />
                            {factor}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {selectedProject.ai_insights.recommendations && selectedProject.ai_insights.recommendations.length > 0 && (
                    <div>
                      <p className="font-medium text-sm mb-2">Recommendations</p>
                      <ul className="space-y-1">
                        {selectedProject.ai_insights.recommendations.map((rec, index) => (
                          <li key={index} className="text-sm text-green-700 flex items-start gap-2">
                            <CheckCircle className="h-4 w-4 mt-0.5" />
                            {rec}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* Action buttons */}
              <div className="flex gap-2 pt-4">
                <Button size="sm">
                  <Eye className="h-4 w-4 mr-2" />
                  View in Asana
                </Button>
                <Button variant="outline" size="sm">
                  <Users className="h-4 w-4 mr-2" />
                  View Team
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default AsanaProjectManagementDashboard; 
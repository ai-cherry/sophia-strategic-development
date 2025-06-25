import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Alert, AlertDescription } from '../ui/alert';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../ui/table';
import {
  Search,
  GitBranch,
  Calendar,
  Users,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Clock,
  Loader2,
  RefreshCw,
  Filter,
  BarChart3,
  Target,
  Zap
} from 'lucide-react';

interface LinearStats {
  total_issues: number;
  active_issues: number;
  completed_issues: number;
  projects: {
    [key: string]: {
      issue_count: number;
      completion_rate: number;
      avg_cycle_time: number;
    };
  };
  team_velocity: {
    issues_per_week: number;
    completion_trend: number;
  };
  priority_distribution: {
    urgent: number;
    high: number;
    medium: number;
    low: number;
  };
  last_sync: string | null;
}

interface LinearIssue {
  id: string;
  title: string;
  description: string;
  status: string;
  priority: string;
  project_name: string;
  assignee: string;
  created_at: string;
  updated_at: string;
  labels: string[];
  cycle_time_days?: number;
}

interface LinearInsight {
  id: string;
  type: string;
  title: string;
  description: string;
  confidence_score: number;
  business_impact: string;
  project_name: string;
  created_at: string;
  actionable: boolean;
}

export const LinearKnowledgeTab: React.FC = () => {
  const [stats, setStats] = useState<LinearStats | null>(null);
  const [issues, setIssues] = useState<LinearIssue[]>([]);
  const [insights, setInsights] = useState<LinearInsight[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<LinearIssue[]>([]);
  const [selectedView, setSelectedView] = useState<'overview' | 'issues' | 'insights'>('overview');
  const [selectedProject, setSelectedProject] = useState<string>('all');
  const [selectedPriority, setSelectedPriority] = useState<string>('all');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadLinearData();
  }, []);

  const loadLinearData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Load stats
      const statsResponse = await fetch('/api/v1/knowledge/linear/stats');
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStats(statsData);
      }

      // Load recent issues
      const issuesResponse = await fetch('/api/v1/knowledge/linear/issues?limit=50');
      if (issuesResponse.ok) {
        const issuesData = await issuesResponse.json();
        setIssues(issuesData.issues || []);
      }

      // Load insights
      const insightsResponse = await fetch('/api/v1/knowledge/linear/insights');
      if (insightsResponse.ok) {
        const insightsData = await insightsResponse.json();
        setInsights(insightsData.insights || []);
      }

    } catch (err: any) {
      setError(err.message || 'Failed to load Linear data');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    setLoading(true);
    try {
      const params = new URLSearchParams({
        query: searchQuery,
        project: selectedProject !== 'all' ? selectedProject : '',
        priority: selectedPriority !== 'all' ? selectedPriority : '',
        limit: '20'
      });

      const response = await fetch(`/api/v1/knowledge/linear/search?${params}`);
      if (response.ok) {
        const data = await response.json();
        setSearchResults(data.results || []);
      }
    } catch (err: any) {
      setError(err.message || 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/knowledge/linear/sync', {
        method: 'POST'
      });
      
      if (response.ok) {
        await loadLinearData();
      } else {
        throw new Error('Sync failed');
      }
    } catch (err: any) {
      setError(err.message || 'Sync failed');
    } finally {
      setLoading(false);
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'urgent': return <AlertCircle className="h-4 w-4 text-red-500" />;
      case 'high': return <TrendingUp className="h-4 w-4 text-orange-500" />;
      case 'medium': return <Target className="h-4 w-4 text-yellow-500" />;
      case 'low': return <Clock className="h-4 w-4 text-green-500" />;
      default: return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'todo': return 'bg-gray-100 text-gray-800';
      case 'in progress': return 'bg-blue-100 text-blue-800';
      case 'in review': return 'bg-yellow-100 text-yellow-800';
      case 'done': return 'bg-green-100 text-green-800';
      case 'canceled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with sync button */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">Linear Development Tracking</h3>
          <p className="text-sm text-muted-foreground">
            Project management and development workflow insights
          </p>
        </div>
        <Button onClick={handleSync} disabled={loading} variant="outline">
          {loading ? (
            <Loader2 className="h-4 w-4 animate-spin mr-2" />
          ) : (
            <RefreshCw className="h-4 w-4 mr-2" />
          )}
          Sync Linear Data
        </Button>
      </div>

      {/* View selector */}
      <div className="flex space-x-1 bg-muted p-1 rounded-lg">
        <Button
          variant={selectedView === 'overview' ? 'default' : 'ghost'}
          size="sm"
          onClick={() => setSelectedView('overview')}
          className="flex-1"
        >
          <BarChart3 className="h-4 w-4 mr-2" />
          Overview
        </Button>
        <Button
          variant={selectedView === 'issues' ? 'default' : 'ghost'}
          size="sm"
          onClick={() => setSelectedView('issues')}
          className="flex-1"
        >
          <GitBranch className="h-4 w-4 mr-2" />
          Issues
        </Button>
        <Button
          variant={selectedView === 'insights' ? 'default' : 'ghost'}
          size="sm"
          onClick={() => setSelectedView('insights')}
          className="flex-1"
        >
          <Zap className="h-4 w-4 mr-2" />
          Insights
        </Button>
      </div>

      {/* Overview View */}
      {selectedView === 'overview' && stats && (
        <div className="space-y-6">
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <GitBranch className="h-5 w-5 text-blue-500" />
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Total Issues</p>
                    <p className="text-2xl font-bold">{stats.total_issues}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <Clock className="h-5 w-5 text-yellow-500" />
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Active Issues</p>
                    <p className="text-2xl font-bold">{stats.active_issues}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Completed</p>
                    <p className="text-2xl font-bold">{stats.completed_issues}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <TrendingUp className="h-5 w-5 text-purple-500" />
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Weekly Velocity</p>
                    <p className="text-2xl font-bold">{stats.team_velocity.issues_per_week}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Priority Distribution */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Target className="h-5 w-5" />
                <span>Priority Distribution</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {Object.entries(stats.priority_distribution).map(([priority, count]) => (
                  <div key={priority} className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2 w-20">
                      {getPriorityIcon(priority)}
                      <span className="text-sm font-medium capitalize">{priority}</span>
                    </div>
                    <div className="flex-1">
                      <Progress 
                        value={(count / stats.total_issues) * 100} 
                        className="h-2"
                      />
                    </div>
                    <span className="text-sm text-muted-foreground w-12 text-right">{count}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Project Performance */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Users className="h-5 w-5" />
                <span>Project Performance</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {Object.entries(stats.projects).map(([projectName, projectStats]) => (
                  <div key={projectName} className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">{projectName}</h4>
                      <Badge variant="outline">
                        {projectStats.issue_count} issues
                      </Badge>
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Completion Rate:</span>
                        <span className="ml-2 font-medium">
                          {(projectStats.completion_rate * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Avg Cycle Time:</span>
                        <span className="ml-2 font-medium">
                          {projectStats.avg_cycle_time.toFixed(1)} days
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Issues View */}
      {selectedView === 'issues' && (
        <div className="space-y-6">
          {/* Search and Filters */}
          <Card>
            <CardContent className="p-6">
              <div className="flex space-x-4">
                <div className="flex-1">
                  <Input
                    placeholder="Search Linear issues..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  />
                </div>
                <select
                  value={selectedProject}
                  onChange={(e) => setSelectedProject(e.target.value)}
                  className="px-3 py-2 border rounded-md"
                >
                  <option value="all">All Projects</option>
                  {stats && Object.keys(stats.projects).map(project => (
                    <option key={project} value={project}>{project}</option>
                  ))}
                </select>
                <select
                  value={selectedPriority}
                  onChange={(e) => setSelectedPriority(e.target.value)}
                  className="px-3 py-2 border rounded-md"
                >
                  <option value="all">All Priorities</option>
                  <option value="urgent">Urgent</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
                <Button onClick={handleSearch} disabled={loading}>
                  {loading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Search className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Issues Table */}
          <Card>
            <CardHeader>
              <CardTitle>
                {searchResults.length > 0 ? 'Search Results' : 'Recent Issues'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Issue</TableHead>
                    <TableHead>Project</TableHead>
                    <TableHead>Priority</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Assignee</TableHead>
                    <TableHead>Updated</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {(searchResults.length > 0 ? searchResults : issues).map((issue) => (
                    <TableRow key={issue.id}>
                      <TableCell>
                        <div>
                          <p className="font-medium">{issue.title}</p>
                          <p className="text-sm text-muted-foreground">
                            {issue.description.substring(0, 100)}...
                          </p>
                          <div className="flex space-x-1 mt-1">
                            {issue.labels.map((label) => (
                              <Badge key={label} variant="secondary" className="text-xs">
                                {label}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>{issue.project_name}</TableCell>
                      <TableCell>
                        <div className="flex items-center space-x-1">
                          {getPriorityIcon(issue.priority)}
                          <span className="capitalize">{issue.priority}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge className={getStatusColor(issue.status)}>
                          {issue.status}
                        </Badge>
                      </TableCell>
                      <TableCell>{issue.assignee}</TableCell>
                      <TableCell>
                        {new Date(issue.updated_at).toLocaleDateString()}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Insights View */}
      {selectedView === 'insights' && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Zap className="h-5 w-5" />
                <span>Development Insights</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {insights.map((insight) => (
                  <div key={insight.id} className="p-4 border rounded-lg">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h4 className="font-medium">{insight.title}</h4>
                          <Badge variant="outline">{insight.type}</Badge>
                          {insight.actionable && (
                            <Badge variant="secondary">Actionable</Badge>
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground mb-2">
                          {insight.description}
                        </p>
                        <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                          <span>Project: {insight.project_name}</span>
                          <span>Impact: {insight.business_impact}</span>
                          <span>Confidence: {(insight.confidence_score * 100).toFixed(0)}%</span>
                          <span>{new Date(insight.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default LinearKnowledgeTab; 
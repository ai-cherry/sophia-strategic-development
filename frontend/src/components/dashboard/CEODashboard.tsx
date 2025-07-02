import React, { useState, useEffect, useRef } from 'react';
import { 
  Card, 
  CardContent, 
  CardHeader, 
  CardTitle,
  Button,
  Input,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
  Badge,
  Alert,
  AlertDescription,
  Progress,
  Avatar,
  AvatarFallback,
  AvatarImage
} from '@/components/ui';
import { 
  MessageCircle, 
  Search, 
  TrendingUp, 
  AlertTriangle, 
  Users, 
  Target,
  Calendar,
  DollarSign,
  Activity,
  BarChart3,
  PieChart,
  LineChart,
  Send,
  Loader2,
  RefreshCw,
  Bell,
  Settings,
  Filter,
  Download,
  Share2,
  Maximize2
} from 'lucide-react';
import { Line, Bar, Pie, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

// Types
interface CEOInsight {
  title: string;
  summary: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  category: string;
  timestamp: string;
  confidence_score: number;
  recommendations: string[];
}

interface ProjectSummary {
  project_id: string;
  project_name: string;
  platform: 'Linear' | 'Asana' | 'Notion';
  health_score: number;
  completion_percentage: number;
  team_members: string[];
  risk_factors: string[];
  last_updated: string;
}

interface SalesMetrics {
  total_pipeline_value: number;
  active_deals: number;
  high_probability_deals: number;
  win_rate: number;
  recent_calls_analyzed: number;
}

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: string;
  query_type?: string;
  insights?: any[];
  visualizations?: any;
}

const CEODashboard: React.FC = () => {
  // State management
  const [activeTab, setActiveTab] = useState('overview');
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [insights, setInsights] = useState<CEOInsight[]>([]);
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [salesMetrics, setSalesMetrics] = useState<SalesMetrics | null>(null);
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());
  
  // Refs
  const chatEndRef = useRef<HTMLDivElement>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  // Auto-scroll chat to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  // Initialize dashboard
  useEffect(() => {
    loadDashboardSummary();
    loadProjectManagement();
    loadSalesCoaching();
    
    // Set up auto-refresh every 5 minutes
    const interval = setInterval(() => {
      refreshDashboard();
    }, 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, []);

  // API Functions
  const loadDashboardSummary = async () => {
    try {
      const response = await fetch('/api/v1/ceo/dashboard/summary');
      const data = await response.json();
      setDashboardData(data);
      setInsights(data.recent_insights || []);
    } catch (error) {
      console.error('Failed to load dashboard summary:', error);
    }
  };

  const loadProjectManagement = async () => {
    try {
      const response = await fetch('/api/v1/ceo/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          platforms: ['Linear', 'Asana', 'Notion'],
          include_health_metrics: true,
          include_risk_assessment: true
        })
      });
      const data = await response.json();
      if (data.success) {
        setProjects(data.projects || []);
      }
    } catch (error) {
      console.error('Failed to load project management data:', error);
    }
  };

  const loadSalesCoaching = async () => {
    try {
      const response = await fetch('/api/v1/ceo/sales-coaching', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          include_call_analysis: true,
          include_hubspot_data: true,
          include_slack_activity: true
        })
      });
      const data = await response.json();
      if (data.success) {
        setSalesMetrics(data.sales_metrics);
      }
    } catch (error) {
      console.error('Failed to load sales coaching data:', error);
    }
  };

  const refreshDashboard = async () => {
    setIsLoading(true);
    try {
      await Promise.all([
        loadDashboardSummary(),
        loadProjectManagement(),
        loadSalesCoaching()
      ]);
      setLastRefresh(new Date());
      
      // Trigger backend refresh
      await fetch('/api/v1/ceo/insights/refresh', { method: 'POST' });
    } catch (error) {
      console.error('Failed to refresh dashboard:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Chat Functions
  const sendChatMessage = async () => {
    if (!chatInput.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: chatInput,
      timestamp: new Date().toISOString()
    };

    setChatMessages(prev => [...prev, userMessage]);
    setChatInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/v1/ceo/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: chatInput,
          include_recommendations: true,
          include_visualizations: true
        })
      });

      const data = await response.json();

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: data.response,
        timestamp: data.timestamp,
        query_type: data.query_type,
        insights: data.insights,
        visualizations: data.visualizations
      };

      setChatMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'I apologize, but I encountered an error processing your request. Please try again.',
        timestamp: new Date().toISOString()
      };
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const startStreamingChat = async () => {
    if (!chatInput.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: chatInput,
      timestamp: new Date().toISOString()
    };

    setChatMessages(prev => [...prev, userMessage]);
    const query = chatInput;
    setChatInput('');

    // Create streaming response placeholder
    const streamingMessage: ChatMessage = {
      id: (Date.now() + 1).toString(),
      type: 'assistant',
      content: '',
      timestamp: new Date().toISOString()
    };

    setChatMessages(prev => [...prev, streamingMessage]);

    try {
      const eventSource = new EventSource(
        `/api/v1/ceo/chat/stream?query=${encodeURIComponent(query)}`
      );
      eventSourceRef.current = eventSource;

      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'chunk') {
          setChatMessages(prev => 
            prev.map(msg => 
              msg.id === streamingMessage.id 
                ? { ...msg, content: msg.content + ' ' + data.content }
                : msg
            )
          );
        } else if (data.type === 'data') {
          setChatMessages(prev => 
            prev.map(msg => 
              msg.id === streamingMessage.id 
                ? { 
                    ...msg, 
                    insights: data.result.insights,
                    visualizations: data.result.visualizations,
                    query_type: data.result.query_type
                  }
                : msg
            )
          );
        } else if (data.type === 'end') {
          eventSource.close();
        } else if (data.type === 'error') {
          setChatMessages(prev => 
            prev.map(msg => 
              msg.id === streamingMessage.id 
                ? { ...msg, content: data.message }
                : msg
            )
          );
          eventSource.close();
        }
      };

      eventSource.onerror = () => {
        eventSource.close();
      };

    } catch (error) {
      console.error('Streaming chat error:', error);
    }
  };

  // Chart configurations
  const getProjectHealthChart = () => {
    if (!projects.length) return null;

    const healthData = {
      labels: ['Critical (<50)', 'At Risk (50-70)', 'Moderate (70-85)', 'Healthy (85+)'],
      datasets: [{
        data: [
          projects.filter(p => p.health_score < 50).length,
          projects.filter(p => p.health_score >= 50 && p.health_score < 70).length,
          projects.filter(p => p.health_score >= 70 && p.health_score < 85).length,
          projects.filter(p => p.health_score >= 85).length,
        ],
        backgroundColor: ['#ef4444', '#f97316', '#eab308', '#22c55e'],
        borderWidth: 0
      }]
    };

    return (
      <Doughnut 
        data={healthData} 
        options={{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom' as const,
            },
            title: {
              display: true,
              text: 'Project Health Distribution'
            }
          }
        }}
      />
    );
  };

  const getPlatformBreakdownChart = () => {
    if (!projects.length) return null;

    const platformData = {
      labels: ['Linear', 'Asana', 'Notion'],
      datasets: [{
        data: [
          projects.filter(p => p.platform === 'Linear').length,
          projects.filter(p => p.platform === 'Asana').length,
          projects.filter(p => p.platform === 'Notion').length,
        ],
        backgroundColor: ['#3b82f6', '#8b5cf6', '#06b6d4'],
        borderWidth: 0
      }]
    };

    return (
      <Pie 
        data={platformData} 
        options={{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom' as const,
            },
            title: {
              display: true,
              text: 'Projects by Platform'
            }
          }
        }}
      />
    );
  };

  const getSalesMetricsChart = () => {
    if (!salesMetrics) return null;

    const salesData = {
      labels: ['Pipeline Value', 'Active Deals', 'High Probability', 'Recent Calls'],
      datasets: [{
        label: 'Sales Metrics',
        data: [
          salesMetrics.total_pipeline_value / 1000, // Convert to thousands
          salesMetrics.active_deals,
          salesMetrics.high_probability_deals,
          salesMetrics.recent_calls_analyzed
        ],
        backgroundColor: ['#22c55e', '#3b82f6', '#f59e0b', '#8b5cf6'],
        borderRadius: 4
      }]
    };

    return (
      <Bar 
        data={salesData} 
        options={{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            },
            title: {
              display: true,
              text: 'Sales Performance Overview'
            }
          },
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }}
      />
    );
  };

  // Helper functions
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-300';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'low': return 'bg-green-100 text-green-800 border-green-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getHealthScoreColor = (score: number) => {
    if (score >= 85) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    if (score >= 50) return 'text-orange-600';
    return 'text-red-600';
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">CEO Dashboard</h1>
            <p className="text-gray-600 mt-1">
              Last updated: {formatDate(lastRefresh.toISOString())}
            </p>
          </div>
          
          <div className="flex items-center space-x-4">
            <Button
              onClick={refreshDashboard}
              disabled={isLoading}
              variant="outline"
              size="sm"
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <RefreshCw className="h-4 w-4 mr-2" />
              )}
              Refresh
            </Button>
            
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            
            <Button variant="outline" size="sm">
              <Settings className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Critical Alerts */}
        {dashboardData?.critical_alerts?.length > 0 && (
          <Alert className="mt-4 border-red-200 bg-red-50">
            <AlertTriangle className="h-4 w-4 text-red-600" />
            <AlertDescription className="text-red-800">
              <strong>{dashboardData.critical_alerts.length} Critical Alert(s):</strong>
              {dashboardData.critical_alerts.map((alert: any, index: number) => (
                <span key={index} className="ml-2">
                  {alert.title}
                  {index < dashboardData.critical_alerts.length - 1 && ', '}
                </span>
              ))}
            </AlertDescription>
          </Alert>
        )}
      </div>

      {/* Main Dashboard */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4 lg:w-[600px]">
          <TabsTrigger value="overview" className="flex items-center space-x-2">
            <BarChart3 className="h-4 w-4" />
            <span>Overview</span>
          </TabsTrigger>
          <TabsTrigger value="chat" className="flex items-center space-x-2">
            <MessageCircle className="h-4 w-4" />
            <span>AI Chat</span>
          </TabsTrigger>
          <TabsTrigger value="projects" className="flex items-center space-x-2">
            <Target className="h-4 w-4" />
            <span>Projects</span>
          </TabsTrigger>
          <TabsTrigger value="sales" className="flex items-center space-x-2">
            <TrendingUp className="h-4 w-4" />
            <span>Sales</span>
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          {/* Key Metrics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="bg-gradient-to-r from-blue-500 to-blue-600 text-white">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-blue-100">Total Projects</p>
                    <p className="text-3xl font-bold">{projects.length}</p>
                  </div>
                  <Target className="h-8 w-8 text-blue-200" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-r from-green-500 to-green-600 text-white">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-green-100">Pipeline Value</p>
                    <p className="text-3xl font-bold">
                      {salesMetrics ? formatCurrency(salesMetrics.total_pipeline_value) : '$0'}
                    </p>
                  </div>
                  <DollarSign className="h-8 w-8 text-green-200" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-r from-purple-500 to-purple-600 text-white">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-purple-100">Active Deals</p>
                    <p className="text-3xl font-bold">
                      {salesMetrics?.active_deals || 0}
                    </p>
                  </div>
                  <Activity className="h-8 w-8 text-purple-200" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-r from-orange-500 to-orange-600 text-white">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-orange-100">Team Members</p>
                    <p className="text-3xl font-bold">
                      {new Set(projects.flatMap(p => p.team_members)).size}
                    </p>
                  </div>
                  <Users className="h-8 w-8 text-orange-200" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Project Health</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  {getProjectHealthChart()}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Platform Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  {getPlatformBreakdownChart()}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Sales Metrics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  {getSalesMetricsChart()}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Insights */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Bell className="h-5 w-5" />
                <span>Recent Insights</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {insights.map((insight, index) => (
                  <div key={index} className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg">
                    <Badge className={getPriorityColor(insight.priority)}>
                      {insight.priority}
                    </Badge>
                    <div className="flex-1">
                      <h4 className="font-semibold text-gray-900">{insight.title}</h4>
                      <p className="text-gray-600 mt-1">{insight.summary}</p>
                      <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                        <span>{insight.category}</span>
                        <span>•</span>
                        <span>{formatDate(insight.timestamp)}</span>
                        <span>•</span>
                        <span>Confidence: {Math.round(insight.confidence_score * 100)}%</span>
                      </div>
                    </div>
                  </div>
                ))}
                
                {insights.length === 0 && (
                  <p className="text-gray-500 text-center py-8">
                    No recent insights available. Data is being processed...
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Chat Tab */}
        <TabsContent value="chat" className="space-y-6">
          <Card className="h-[600px] flex flex-col">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <MessageCircle className="h-5 w-5" />
                <span>AI Business Intelligence Chat</span>
              </CardTitle>
            </CardHeader>
            
            <CardContent className="flex-1 flex flex-col">
              {/* Chat Messages */}
              <div className="flex-1 overflow-y-auto space-y-4 mb-4 p-4 bg-gray-50 rounded-lg">
                {chatMessages.length === 0 && (
                  <div className="text-center text-gray-500 py-8">
                    <MessageCircle className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                    <p>Ask me anything about your business...</p>
                    <div className="mt-4 space-y-2 text-sm">
                      <p className="font-medium">Try asking:</p>
                      <ul className="space-y-1">
                        <li>• "What's the health of our current projects?"</li>
                        <li>• "How is our sales pipeline performing?"</li>
                        <li>• "Which deals need immediate attention?"</li>
                        <li>• "What are the biggest risks to our projects?"</li>
                      </ul>
                    </div>
                  </div>
                )}
                
                {chatMessages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] p-4 rounded-lg ${
                        message.type === 'user'
                          ? 'bg-blue-600 text-white'
                          : 'bg-white text-gray-900 border'
                      }`}
                    >
                      <p className="whitespace-pre-wrap">{message.content}</p>
                      
                      {message.insights && message.insights.length > 0 && (
                        <div className="mt-4 space-y-2">
                          <p className="font-semibold text-sm">Key Insights:</p>
                          {message.insights.map((insight, index) => (
                            <div key={index} className="p-2 bg-gray-100 rounded text-sm">
                              <p className="font-medium">{insight.title}</p>
                              <p className="text-gray-600">{JSON.stringify(insight.data)}</p>
                            </div>
                          ))}
                        </div>
                      )}
                      
                      <p className="text-xs mt-2 opacity-70">
                        {formatDate(message.timestamp)}
                        {message.query_type && (
                          <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-800 rounded">
                            {message.query_type}
                          </span>
                        )}
                      </p>
                    </div>
                  </div>
                ))}
                
                <div ref={chatEndRef} />
              </div>
              
              {/* Chat Input */}
              <div className="flex space-x-2">
                <Input
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder="Ask about projects, sales, team performance..."
                  onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && sendChatMessage()}
                  disabled={isLoading}
                  className="flex-1"
                />
                <Button
                  onClick={sendChatMessage}
                  disabled={isLoading || !chatInput.trim()}
                  size="sm"
                >
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Projects Tab */}
        <TabsContent value="projects" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Project Summary */}
            <Card>
              <CardHeader>
                <CardTitle>Project Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Average Health Score</span>
                      <span className="font-semibold">
                        {projects.length > 0 
                          ? Math.round(projects.reduce((sum, p) => sum + p.health_score, 0) / projects.length)
                          : 0}%
                      </span>
                    </div>
                    <Progress 
                      value={projects.length > 0 
                        ? projects.reduce((sum, p) => sum + p.health_score, 0) / projects.length
                        : 0} 
                      className="mt-2"
                    />
                  </div>
                  
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                      <p className="text-2xl font-bold text-green-600">
                        {projects.filter(p => p.health_score >= 85).length}
                      </p>
                      <p className="text-xs text-gray-600">Healthy</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-yellow-600">
                        {projects.filter(p => p.health_score >= 50 && p.health_score < 85).length}
                      </p>
                      <p className="text-xs text-gray-600">At Risk</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-red-600">
                        {projects.filter(p => p.health_score < 50).length}
                      </p>
                      <p className="text-xs text-gray-600">Critical</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Platform Breakdown */}
            <Card>
              <CardHeader>
                <CardTitle>Platform Breakdown</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {['Linear', 'Asana', 'Notion'].map(platform => {
                    const count = projects.filter(p => p.platform === platform).length;
                    const percentage = projects.length > 0 ? (count / projects.length) * 100 : 0;
                    
                    return (
                      <div key={platform}>
                        <div className="flex justify-between items-center">
                          <span className="text-sm font-medium">{platform}</span>
                          <span className="text-sm text-gray-600">{count} projects</span>
                        </div>
                        <Progress value={percentage} className="mt-1" />
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>

            {/* Team Workload */}
            <Card>
              <CardHeader>
                <CardTitle>Team Workload</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {Array.from(new Set(projects.flatMap(p => p.team_members)))
                    .slice(0, 5)
                    .map(member => {
                      const memberProjects = projects.filter(p => p.team_members.includes(member));
                      const avgHealth = memberProjects.length > 0 
                        ? memberProjects.reduce((sum, p) => sum + p.health_score, 0) / memberProjects.length
                        : 0;
                      
                      return (
                        <div key={member} className="flex items-center space-x-3">
                          <Avatar className="h-8 w-8">
                            <AvatarFallback className="text-xs">
                              {member.split(' ').map(n => n[0]).join('').toUpperCase()}
                            </AvatarFallback>
                          </Avatar>
                          <div className="flex-1">
                            <p className="text-sm font-medium">{member}</p>
                            <p className="text-xs text-gray-600">
                              {memberProjects.length} projects • {Math.round(avgHealth)}% avg health
                            </p>
                          </div>
                        </div>
                      );
                    })}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Project List */}
          <Card>
            <CardHeader>
              <CardTitle>All Projects</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {projects.map((project) => (
                  <div key={project.project_id} className="p-4 border rounded-lg hover:bg-gray-50">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3">
                          <h4 className="font-semibold text-gray-900">{project.project_name}</h4>
                          <Badge variant="outline">{project.platform}</Badge>
                          <span className={`text-sm font-medium ${getHealthScoreColor(project.health_score)}`}>
                            {project.health_score}% Health
                          </span>
                        </div>
                        
                        <div className="mt-2 flex items-center space-x-4 text-sm text-gray-600">
                          <span>{project.completion_percentage}% Complete</span>
                          <span>•</span>
                          <span>{project.team_members.length} team members</span>
                          <span>•</span>
                          <span>Updated {formatDate(project.last_updated)}</span>
                        </div>
                        
                        {project.risk_factors.length > 0 && (
                          <div className="mt-2">
                            <p className="text-sm text-red-600 font-medium">Risks:</p>
                            <ul className="text-sm text-red-600 list-disc list-inside">
                              {project.risk_factors.slice(0, 2).map((risk, index) => (
                                <li key={index}>{risk}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                      
                      <div className="text-right">
                        <Progress value={project.completion_percentage} className="w-24 mb-2" />
                        <div className="flex space-x-1">
                          {project.team_members.slice(0, 3).map((member, index) => (
                            <Avatar key={index} className="h-6 w-6">
                              <AvatarFallback className="text-xs">
                                {member.split(' ').map(n => n[0]).join('').toUpperCase()}
                              </AvatarFallback>
                            </Avatar>
                          ))}
                          {project.team_members.length > 3 && (
                            <div className="h-6 w-6 bg-gray-200 rounded-full flex items-center justify-center">
                              <span className="text-xs text-gray-600">+{project.team_members.length - 3}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                
                {projects.length === 0 && (
                  <p className="text-gray-500 text-center py-8">
                    No projects found. Data is being synchronized...
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Sales Tab */}
        <TabsContent value="sales" className="space-y-6">
          {/* Sales Metrics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Pipeline Value</p>
                    <p className="text-2xl font-bold text-green-600">
                      {salesMetrics ? formatCurrency(salesMetrics.total_pipeline_value) : '$0'}
                    </p>
                  </div>
                  <DollarSign className="h-8 w-8 text-green-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Active Deals</p>
                    <p className="text-2xl font-bold text-blue-600">
                      {salesMetrics?.active_deals || 0}
                    </p>
                  </div>
                  <Target className="h-8 w-8 text-blue-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">High Probability</p>
                    <p className="text-2xl font-bold text-purple-600">
                      {salesMetrics?.high_probability_deals || 0}
                    </p>
                  </div>
                  <TrendingUp className="h-8 w-8 text-purple-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Win Rate</p>
                    <p className="text-2xl font-bold text-orange-600">
                      {salesMetrics ? Math.round(salesMetrics.win_rate * 100) : 0}%
                    </p>
                  </div>
                  <Activity className="h-8 w-8 text-orange-500" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sales Analytics */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Sales Performance</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  {getSalesMetricsChart()}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Recent Call Analysis</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="text-center">
                    <p className="text-3xl font-bold text-blue-600">
                      {salesMetrics?.recent_calls_analyzed || 0}
                    </p>
                    <p className="text-sm text-gray-600">Calls Analyzed (Last 7 Days)</p>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Positive Sentiment</span>
                      <span className="text-sm font-medium text-green-600">75%</span>
                    </div>
                    <Progress value={75} className="h-2" />
                    
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Neutral Sentiment</span>
                      <span className="text-sm font-medium text-gray-600">20%</span>
                    </div>
                    <Progress value={20} className="h-2" />
                    
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Negative Sentiment</span>
                      <span className="text-sm font-medium text-red-600">5%</span>
                    </div>
                    <Progress value={5} className="h-2" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sales Coaching Insights */}
          <Card>
            <CardHeader>
              <CardTitle>AI Sales Coaching Insights</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Alert className="border-blue-200 bg-blue-50">
                  <TrendingUp className="h-4 w-4 text-blue-600" />
                  <AlertDescription className="text-blue-800">
                    <strong>Top Opportunity:</strong> Focus on enterprise deals in Q4. 
                    3 high-value prospects showing strong buying signals based on recent Gong call analysis.
                  </AlertDescription>
                </Alert>
                
                <Alert className="border-yellow-200 bg-yellow-50">
                  <AlertTriangle className="h-4 w-4 text-yellow-600" />
                  <AlertDescription className="text-yellow-800">
                    <strong>Risk Alert:</strong> 2 deals worth $150K+ have stalled for 14+ days. 
                    Recommend immediate intervention and re-engagement strategy.
                  </AlertDescription>
                </Alert>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 bg-green-50 rounded-lg">
                    <h4 className="font-semibold text-green-800">Best Practices Identified</h4>
                    <ul className="mt-2 text-sm text-green-700 space-y-1">
                      <li>• Discovery calls with 3+ stakeholders show 40% higher close rate</li>
                      <li>• Technical demos scheduled within 5 days improve conversion by 25%</li>
                      <li>• Follow-up within 24 hours increases engagement by 60%</li>
                    </ul>
                  </div>
                  
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <h4 className="font-semibold text-blue-800">Recommended Actions</h4>
                    <ul className="mt-2 text-sm text-blue-700 space-y-1">
                      <li>• Schedule coaching session with Sarah (3 stalled deals)</li>
                      <li>• Review objection handling for pricing concerns</li>
                      <li>• Implement new qualification framework for enterprise deals</li>
                    </ul>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default CEODashboard; 
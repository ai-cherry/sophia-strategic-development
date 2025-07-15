import React, { useState, useEffect, useCallback } from 'react';
import { 
  Card, 
  CardContent, 
  CardHeader, 
  CardTitle,
  CardDescription 
} from '@/components/ui/card';
import { 
  Tabs, 
  TabsContent, 
  TabsList, 
  TabsTrigger 
} from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
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
  Cell
} from 'recharts';
import { 
  TrendingUp, 
  TrendingDown, 
  Search, 
  MessageSquare,
  Video,
  Twitter,
  RefreshCw,
  Zap,
  Target
} from 'lucide-react';

// Import strategic project management panels
import StrategicOverviewPanel from './panels/StrategicOverviewPanel';
import DepartmentalKPIPanel from './panels/DepartmentalKPIPanel';
import CrossPlatformIntelligencePanel from './panels/CrossPlatformIntelligencePanel';
import UserManagementPanel from './panels/UserManagementPanel';

// Mock data for charts
const revenueData = [
  { month: 'Jan', revenue: 3200000, growth: 15 },
  { month: 'Feb', revenue: 3500000, growth: 18 },
  { month: 'Mar', revenue: 3800000, growth: 22 },
  { month: 'Apr', revenue: 4100000, growth: 25 },
  { month: 'May', revenue: 4200000, growth: 23 },
  { month: 'Jun', revenue: 4500000, growth: 28 },
];

const performanceData = [
  { name: 'Chat Latency', value: 145, target: 180, unit: 'ms' },
  { name: 'Search Accuracy', value: 92, target: 88, unit: '%' },
  { name: 'Query Volume', value: 2150, target: 2000, unit: 'qps' },
  { name: 'Uptime', value: 99.99, target: 99.9, unit: '%' },
];

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

interface ChatMessage {
  id: string;
  user: string;
  message: string;
  response: string;
  latency: number;
  mode: string;
  timestamp: string;
  trends?: any[];
  videos?: any[];
}

export default function UnifiedDashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [strategicSubTab, setStrategicSubTab] = useState('overview');
  const [searchQuery, setSearchQuery] = useState('');
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [isPolling, setIsPolling] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [performanceMetrics, setPerformanceMetrics] = useState(performanceData);

  // Simulate 5s polling for real-time updates
  useEffect(() => {
    if (!isPolling) return;

    const pollInterval = setInterval(() => {
      // Simulate fetching new data
      fetchLatestMetrics();
      setLastUpdate(new Date());
    }, 5000);

    return () => clearInterval(pollInterval);
  }, [isPolling]);

  const fetchLatestMetrics = useCallback(async () => {
    // In production, this would fetch from the API
    // Simulate slight variations in metrics
    setPerformanceMetrics(prev => prev.map(metric => ({
      ...metric,
      value: metric.value + (Math.random() - 0.5) * 2
    })));
  }, []);

  const handleSearch = useCallback(async () => {
    // Simulate Weaviate search with snarky response
    const mockResponse: ChatMessage = {
      id: Date.now().toString(),
      user: 'ceo_user',
      message: searchQuery,
      response: searchQuery.toLowerCase().includes('revenue') 
        ? "Oh, revenue AGAIN? Fine... Q3 is up 23% YoY to $4.2M. Happy now? 🙄"
        : "Let me search that for you... because apparently Google is too hard to use.",
      latency: 142,
      mode: 'snarky',
      timestamp: new Date().toISOString(),
      trends: [
        { text: "Tech revenue growth hitting record highs #earnings", relevance: 0.95 }
      ],
      videos: [
        { title: "Revenue Analysis Masterclass", duration: "12:34", source: "youtube" }
      ]
    };

    setChatMessages(prev => [mockResponse, ...prev].slice(0, 10));
  }, [searchQuery]);

  return (
    <div className="p-6 space-y-6 bg-gray-50 dark:bg-gray-900 min-h-screen">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Sophia AI Command Center
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Real-time Business Intelligence & Strategic Project Management
          </p>
        </div>
        <div className="flex items-center gap-4">
          <Badge variant={isPolling ? "default" : "secondary"}>
            {isPolling ? "Live" : "Paused"}
          </Badge>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsPolling(!isPolling)}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isPolling ? 'animate-spin' : ''}`} />
            {isPolling ? 'Pause' : 'Resume'}
          </Button>
          <div className="text-sm text-gray-500">
            Last update: {lastUpdate.toLocaleTimeString()}
          </div>
        </div>
      </div>

      {/* Main Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="strategic">Strategic PM</TabsTrigger>
          <TabsTrigger value="users">User Management</TabsTrigger>
          <TabsTrigger value="chat">Chat Analytics</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="search">AI Search</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {performanceMetrics.map((metric, index) => (
              <Card key={metric.name}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    {metric.name}
                  </CardTitle>
                  <Zap className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {metric.value.toFixed(metric.unit === '%' ? 2 : 0)}{metric.unit}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Target: {metric.target}{metric.unit}
                  </p>
                  <div className="mt-2">
                    {metric.value >= metric.target ? (
                      <Badge variant="default" className="text-xs">
                        <TrendingUp className="h-3 w-3 mr-1" />
                        On Target
                      </Badge>
                    ) : (
                      <Badge variant="destructive" className="text-xs">
                        <TrendingDown className="h-3 w-3 mr-1" />
                        Below Target
                      </Badge>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Revenue Chart */}
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Revenue Growth Trend</CardTitle>
                <CardDescription>
                  Monthly revenue with growth percentage
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={revenueData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis yAxisId="left" />
                    <YAxis yAxisId="right" orientation="right" />
                    <Tooltip formatter={(value, name) => [
                      name === 'revenue' ? `$${(value as number).toLocaleString()}` : `${value}%`,
                      name === 'revenue' ? 'Revenue' : 'Growth %'
                    ]} />
                    <Legend />
                    <Bar yAxisId="left" dataKey="revenue" fill="#8884d8" name="Monthly Revenue" />
                    <Line yAxisId="right" type="monotone" dataKey="growth" stroke="#82ca9d" name="Growth %" />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>System Health Overview</CardTitle>
                <CardDescription>
                  Real-time system performance metrics
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={performanceMetrics}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={(entry) => `${entry.name}: ${entry.value.toFixed(1)}${entry.unit}`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {performanceMetrics.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Strategic Project Management Tab */}
        <TabsContent value="strategic" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="h-5 w-5" />
                    Strategic Project Management
                  </CardTitle>
                  <CardDescription>
                    Unified view across Notion OKRs, Linear Engineering, and Asana Product Management
                  </CardDescription>
                </div>
                <div className="flex gap-2">
                  <Button
                    variant={strategicSubTab === 'overview' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setStrategicSubTab('overview')}
                  >
                    Strategic Overview
                  </Button>
                  <Button
                    variant={strategicSubTab === 'kpis' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setStrategicSubTab('kpis')}
                  >
                    Departmental KPIs
                  </Button>
                  <Button
                    variant={strategicSubTab === 'intelligence' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setStrategicSubTab('intelligence')}
                  >
                    Cross-Platform Intelligence
                  </Button>
                </div>
              </div>
            </CardHeader>
          </Card>

          {/* Strategic Project Management Sub-panels */}
          {strategicSubTab === 'overview' && <StrategicOverviewPanel />}
          {strategicSubTab === 'kpis' && <DepartmentalKPIPanel />}
          {strategicSubTab === 'intelligence' && <CrossPlatformIntelligencePanel />}
        </TabsContent>

        {/* User Management Tab */}
        <TabsContent value="users" className="space-y-4">
          <UserManagementPanel />
        </TabsContent>

        {/* Chat Analytics Tab */}
        <TabsContent value="chat" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Chat Interactions</CardTitle>
              <CardDescription>
                Real-time chat with snarky AI responses
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {chatMessages.map((msg) => (
                  <div key={msg.id} className="border rounded-lg p-4 space-y-2">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <p className="text-sm font-medium">User: {msg.message}</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                          AI: {msg.response}
                        </p>
                      </div>
                      <div className="text-right space-y-1">
                        <Badge variant={msg.latency < 180 ? "default" : "destructive"}>
                          {msg.latency}ms
                        </Badge>
                        <Badge variant="outline">{msg.mode}</Badge>
                      </div>
                    </div>
                    {msg.trends && msg.trends.length > 0 && (
                      <div className="flex items-center gap-2 text-xs text-gray-500">
                        <Twitter className="h-3 w-3" />
                        {msg.trends[0].text}
                      </div>
                    )}
                    {msg.videos && msg.videos.length > 0 && (
                      <div className="flex items-center gap-2 text-xs text-gray-500">
                        <Video className="h-3 w-3" />
                        {msg.videos[0].title}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Performance Tab */}
        <TabsContent value="performance" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Performance Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={performanceMetrics}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={(entry) => `${entry.name}: ${entry.value}${entry.unit}`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {performanceMetrics.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Target vs Actual</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={performanceMetrics}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="value" fill="#8884d8" name="Actual" />
                    <Bar dataKey="target" fill="#82ca9d" name="Target" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* AI Search Tab */}
        <TabsContent value="search" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Weaviate AI Search</CardTitle>
              <CardDescription>
                Search with snarky AI responses and real-time trends
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2">
                <Input
                  placeholder="Ask about revenue trends..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                />
                <Button onClick={handleSearch}>
                  <Search className="h-4 w-4 mr-2" />
                  Search
                </Button>
              </div>
              
              <div className="mt-4 text-sm text-gray-500">
                Try: "Revenue trends?", "What are Q3 sales?", "Show me growth patterns"
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
} 
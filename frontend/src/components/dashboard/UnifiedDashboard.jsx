import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  DollarSign, 
  Users, 
  Activity, 
  CheckCircle,
  Upload,
  RefreshCw,
  BarChart3,
  Settings,
  Bell
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { api } from '../../services/apiClient';
import MCPIntegrationService from '../../services/mcpIntegration';

// Enhanced KPI Card Component
const UnifiedKPICard = ({ title, value, change, changeType, icon: Icon, target }) => {
  const trendColor = changeType === 'increase' ? 'text-green-500' : 
                    changeType === 'decrease' ? 'text-red-500' : 'text-gray-500';
  const TrendIcon = changeType === 'increase' ? TrendingUp : 
                   changeType === 'decrease' ? TrendingDown : Minus;

  const formatValue = (val) => {
    if (typeof val === 'number') {
      if (val >= 1000000) return `$${(val / 1000000).toFixed(1)}M`;
      if (val >= 1000) return `${(val / 1000).toFixed(0)}K`;
      return val.toLocaleString();
    }
    return val;
  };

  return (
    <Card className="hover:shadow-lg transition-all duration-300 border-gray-200 hover:border-purple-300">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-gray-600">{title}</CardTitle>
        {Icon && <Icon className="h-4 w-4 text-gray-400" />}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-gray-900">{formatValue(value)}</div>
        <div className="flex items-center space-x-1 text-xs text-gray-500">
          <TrendIcon className={`h-4 w-4 ${trendColor}`} />
          <span className={trendColor}>{change}</span>
          <span>from last month</span>
        </div>
        {target && (
          <div className="mt-2">
            <div className="flex justify-between text-xs text-gray-500 mb-1">
              <span>Target: {formatValue(target)}</span>
              <span>{Math.round((Number(value) / target) * 100)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-1.5">
              <div 
                className="bg-purple-600 h-1.5 rounded-full transition-all duration-500"
                style={{ width: `${Math.min((Number(value) / target) * 100, 100)}%` }}
              />
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// Agno Performance Component
const AgnoPerformanceCard = ({ metrics, loading, error }) => {
  const agnoDetails = metrics?.summary?.call_analysis || {};
  const agnoLastUpdated = metrics?.last_updated || '';

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Activity className="h-5 w-5" />
          <span>Agno Agent Performance</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="text-gray-400">Loading Agno performance metrics...</div>
        ) : error ? (
          <div className="text-red-500">{error}</div>
        ) : (
          <div>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div>
                <div className="text-xs text-gray-500">Avg Instantiation</div>
                <div className="text-lg font-bold">
                  {agnoDetails.avg_instantiation_us ? `${agnoDetails.avg_instantiation_us}μs` : '—'}
                </div>
              </div>
              <div>
                <div className="text-xs text-gray-500">Pool Size</div>
                <div className="text-lg font-bold">
                  {agnoDetails.pool_size ?? '—'} / {agnoDetails.pool_max ?? '—'}
                </div>
              </div>
              <div>
                <div className="text-xs text-gray-500">Instantiation Samples</div>
                <div className="text-lg font-bold">{agnoDetails.instantiation_samples ?? '—'}</div>
              </div>
              <div className="col-span-2 md:col-span-3">
                <div className="text-xs text-gray-500">Last Updated</div>
                <div className="text-sm font-medium">{agnoLastUpdated}</div>
              </div>
            </div>
            <div className="mt-4 text-xs text-gray-400 p-3 bg-gray-50 rounded-lg">
              <span>Agno-powered agent instantiation is up to 5000x faster and 50x more memory efficient than legacy agents.</span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// LLM Cost Analysis Component
const LLMCostAnalysis = ({ data }) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <BarChart3 className="h-5 w-5" />
          <span>LLM Cost Analysis</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip formatter={(value) => [`$${value}`, 'Cost']} />
            <Legend />
            <Bar dataKey="cost" fill="#8B5CF6" />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

// Knowledge Management Component
const KnowledgeManagement = ({ jobs }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [syncing, setSyncing] = useState(null);

  const handleFileUpload = async () => {
    if (selectedFile) {
      try {
        setUploading(true);
        await api.knowledge.uploadFile(selectedFile);
        console.log('File uploaded successfully:', selectedFile.name);
        setSelectedFile(null);
      } catch (error) {
        console.error('File upload failed:', error);
      } finally {
        setUploading(false);
      }
    }
  };

  const handleSync = async (source) => {
    try {
      setSyncing(source);
      await api.knowledge.syncSource(source);
      console.log('Sync completed for:', source);
    } catch (error) {
      console.error('Sync failed for', source, ':', error);
    } finally {
      setSyncing(null);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Success': return 'bg-green-100 text-green-800';
      case 'Processing': return 'bg-blue-100 text-blue-800';
      case 'Failed': return 'bg-red-100 text-red-800';
      case 'Queued': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="grid gap-8 md:grid-cols-3">
      {/* Control Panel */}
      <div className="md:col-span-1 space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Upload className="h-5 w-5" />
              <span>Manual Ingestion</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input 
              type="file" 
              onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
            />
            <Button 
              className="w-full" 
              onClick={handleFileUpload}
              disabled={!selectedFile || uploading}
            >
              {uploading ? 'Uploading...' : 'Upload and Ingest'}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <RefreshCw className="h-5 w-5" />
              <span>Data Source Sync</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button 
              variant="outline" 
              className="w-full justify-start"
              onClick={() => handleSync('gong')}
              disabled={syncing === 'gong'}
            >
              {syncing === 'gong' ? 'Syncing...' : 'Sync Gong Calls'}
            </Button>
            <Button 
              variant="outline" 
              className="w-full justify-start"
              onClick={() => handleSync('hubspot')}
              disabled={syncing === 'hubspot'}
            >
              {syncing === 'hubspot' ? 'Syncing...' : 'Sync HubSpot CRM'}
            </Button>
            <Button 
              variant="outline" 
              className="w-full justify-start"
              onClick={() => handleSync('snowflake')}
              disabled={syncing === 'snowflake'}
            >
              {syncing === 'snowflake' ? 'Syncing...' : 'Sync Snowflake Tables'}
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Ingestion Status */}
      <div className="md:col-span-2">
        <Card>
          <CardHeader>
            <CardTitle>Recent Ingestion Jobs</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Source</TableHead>
                  <TableHead>Document</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Timestamp</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {jobs.map((job) => (
                  <TableRow key={job.id}>
                    <TableCell>{job.source}</TableCell>
                    <TableCell className="font-medium">{job.document}</TableCell>
                    <TableCell>
                      <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(job.status)}`}>
                        {job.status}
                      </span>
                    </TableCell>
                    <TableCell>{job.timestamp}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// Executive Chat Interface Component
const ExecutiveChatInterface = () => {
  const [chatInput, setChatInput] = useState('');
  const [messages, setMessages] = useState([]);

  const handleSendMessage = () => {
    if (chatInput.trim()) {
      setMessages(prev => [...prev, { role: 'user', content: chatInput }]);
      // Simulate AI response
      setTimeout(() => {
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: `I understand you're asking about: "${chatInput}". Let me analyze the data and provide insights.` 
        }]);
      }, 1000);
      setChatInput('');
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Activity className="h-5 w-5" />
          <span>Executive Assistant</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="h-64 bg-gray-50 rounded-lg p-4 overflow-y-auto">
          {messages.length === 0 ? (
            <div className="text-gray-500 text-center py-8">
              Ask me anything about your business metrics, team performance, or strategic insights.
            </div>
          ) : (
            <div className="space-y-3">
              {messages.map((message, index) => (
                <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    message.role === 'user' 
                      ? 'bg-purple-600 text-white' 
                      : 'bg-gray-200 text-gray-800'
                  }`}>
                    {message.content}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        <div className="flex space-x-2">
          <Input 
            placeholder="e.g., 'Summarize the top 5 deals from last week.'"
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          />
          <Button onClick={handleSendMessage}>
            Send
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

// Main Unified Dashboard Component
const UnifiedDashboard = () => {
  const [activeTab, setActiveTab] = useState('executive');
  const [agnoMetrics, setAgnoMetrics] = useState(null);
  const [agnoLoading, setAgnoLoading] = useState(true);
  const [agnoError, setAgnoError] = useState(null);
  
  // MCP Integration State
  const [mcpService] = useState(() => new MCPIntegrationService());
  const [mcpConnected, setMcpConnected] = useState(false);
  const [mcpServices, setMcpServices] = useState(new Set());

  // Mock data
  const kpiData = [
    { title: 'Monthly Recurring Revenue', value: 2100000, change: '+3.2%', changeType: 'increase', icon: DollarSign, target: 2500000 },
    { title: 'Active Agents', value: '48', change: '+5', changeType: 'increase', icon: Users },
    { title: 'Agent Success Rate', value: '94.2%', change: '-0.5%', changeType: 'decrease', icon: CheckCircle },
    { title: 'Total API Calls', value: '1.2B', change: '+12%', changeType: 'increase', icon: Activity },
  ];

  const llmCostData = [
    { name: 'GPT-4o', cost: 4200 },
    { name: 'Claude 3 Opus', cost: 5500 },
    { name: 'Gemini 1.5 Pro', cost: 3100 },
    { name: 'Llama 3', cost: 1800 },
  ];

  const ingestionJobs = [
    { id: 'job_123', source: 'Gong Sync', document: 'Call with Acme Corp', status: 'Success', timestamp: '2024-07-21 10:00 AM' },
    { id: 'job_124', source: 'File Upload', document: 'Q3_Financials.pdf', status: 'Processing', timestamp: '2024-07-21 10:05 AM' },
    { id: 'job_125', source: 'HubSpot Sync', document: 'New Contacts Q3', status: 'Queued', timestamp: '2024-07-21 10:06 AM' },
    { id: 'job_122', source: 'File Upload', document: 'competitor_analysis.docx', status: 'Failed', timestamp: '2024-07-21 09:55 AM' },
  ];

  useEffect(() => {
    // Initialize MCP Integration
    const initializeMCP = async () => {
      try {
        await mcpService.initialize();
        setMcpConnected(mcpService.isConnected);
        setMcpServices(mcpService.availableServices);
        console.log('MCP Integration initialized:', mcpService.availableServices.size, 'services');
      } catch (error) {
        console.error('MCP initialization failed:', error);
      }
    };

    // Load Agno metrics from API
    const fetchAgnoMetrics = async () => {
      try {
        setAgnoLoading(true);
        const data = await api.agno.getPerformanceMetrics();
        setAgnoMetrics(data);
      } catch (error) {
        console.error('Failed to load Agno metrics:', error);
        setAgnoError('Failed to load Agno metrics');
      } finally {
        setAgnoLoading(false);
      }
    };

    // Initialize both MCP and fetch metrics
    initializeMCP();
    fetchAgnoMetrics();
  }, [mcpService]);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-blue-500 rounded-lg flex items-center justify-center">
                <span className="text-xl text-white">👑</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Sophia AI Dashboard</h1>
                <p className="text-sm text-gray-500">Unified Executive Command Center</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <Button variant="outline" size="sm">
                <Settings className="h-4 w-4 mr-2" />
                Settings
              </Button>
              <Button variant="outline" size="sm">
                <Bell className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="executive">Executive Overview</TabsTrigger>
            <TabsTrigger value="knowledge">Knowledge Management</TabsTrigger>
            <TabsTrigger value="interaction">AI Interaction</TabsTrigger>
          </TabsList>

          {/* Executive Overview Tab */}
          <TabsContent value="executive" className="space-y-6">
            {/* KPI Cards */}
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
              {kpiData.map((kpi, index) => (
                <UnifiedKPICard key={index} {...kpi} />
              ))}
            </div>

            {/* Charts and Analytics */}
            <div className="grid gap-6 lg:grid-cols-2">
              <LLMCostAnalysis data={llmCostData} />
              <AgnoPerformanceCard 
                metrics={agnoMetrics} 
                loading={agnoLoading} 
                error={agnoError} 
              />
            </div>
          </TabsContent>

          {/* Knowledge Management Tab */}
          <TabsContent value="knowledge">
            <KnowledgeManagement jobs={ingestionJobs} />
          </TabsContent>

          {/* AI Interaction Tab */}
          <TabsContent value="interaction">
            <ExecutiveChatInterface />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default UnifiedDashboard;


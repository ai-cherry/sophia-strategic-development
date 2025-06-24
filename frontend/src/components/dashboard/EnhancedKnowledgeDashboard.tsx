import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Alert, AlertDescription } from '../ui/alert';
import { Progress } from '../ui/progress';
import { Badge } from '../ui/badge';
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
  Upload,
  FileText,
  Brain,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Loader2,
  Database,
  FileUp,
  Link,
  RefreshCw,
  FolderOpen,
  FileCode,
  FileSpreadsheet,
  FilePlus,
  Users,
  MessageSquare
} from 'lucide-react';
import EnhancedUnifiedChatInterface from '../shared/EnhancedUnifiedChatInterface';
import FoundationalKnowledgeTab from './FoundationalKnowledgeTab';
import SlackKnowledgeTab from './SlackKnowledgeTab';

interface IngestionJob {
  id: string;
  source: string;
  document: string;
  status: 'processing' | 'success' | 'failed' | 'queued';
  progress?: number;
  timestamp: string;
  size?: string;
  type?: string;
  error?: string;
}

interface KnowledgeStats {
  totalDocuments: number;
  totalSize: string;
  recentIngestions: number;
  activeProcessing: number;
  searchQueries: number;
  avgQueryTime: number;
}

interface DataSource {
  id: string;
  name: string;
  type: 'gong' | 'hubspot' | 'snowflake' | 'file' | 'api';
  status: 'connected' | 'disconnected' | 'syncing';
  lastSync: string;
  documentCount: number;
  nextSync?: string;
}

export const EnhancedKnowledgeDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [ingestionJobs, setIngestionJobs] = useState<IngestionJob[]>([]);
  const [dataSources, setDataSources] = useState<DataSource[]>([]);
  const [stats, setStats] = useState<KnowledgeStats | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [syncing, setSyncing] = useState<string | null>(null);

  // Chat context for knowledge dashboard
  const chatContext = {
    dashboardType: 'knowledge' as const,
    userId: 'knowledge-admin',
    tenantId: 'payready',
    activeFilters: {}
  };

  // Load dashboard data
  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      // Fetch stats
      const statsResponse = await fetch('/api/v1/knowledge/stats');
      if (statsResponse.ok) {
        setStats(await statsResponse.json());
      }
      
      // Fetch ingestion jobs
      const jobsResponse = await fetch('/api/v1/knowledge/ingestion-jobs');
      if (jobsResponse.ok) {
        setIngestionJobs(await jobsResponse.json());
      }
      
      // Fetch data sources
      const sourcesResponse = await fetch('/api/v1/knowledge/data-sources');
      if (sourcesResponse.ok) {
        setDataSources(await sourcesResponse.json());
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async () => {
    if (!selectedFile) return;
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    try {
      const response = await fetch('/api/v1/knowledge/upload', {
        method: 'POST',
        body: formData
      });
      
      if (response.ok) {
        setSelectedFile(null);
        fetchDashboardData(); // Refresh data
      }
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };

  const handleDataSourceSync = async (sourceId: string) => {
    setSyncing(sourceId);
    try {
      const response = await fetch(`/api/v1/knowledge/sync/${sourceId}`, {
        method: 'POST'
      });
      
      if (response.ok) {
        fetchDashboardData(); // Refresh data
      }
    } catch (error) {
      console.error('Sync failed:', error);
    } finally {
      setSyncing(null);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
      case 'connected':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'failed':
      case 'disconnected':
        return <XCircle className="h-4 w-4 text-red-600" />;
      case 'processing':
      case 'syncing':
        return <Loader2 className="h-4 w-4 text-blue-600 animate-spin" />;
      case 'queued':
        return <Clock className="h-4 w-4 text-yellow-600" />;
      default:
        return <AlertCircle className="h-4 w-4 text-gray-600" />;
    }
  };

  const getFileIcon = (type?: string) => {
    switch (type) {
      case 'pdf':
      case 'doc':
      case 'docx':
        return <FileText className="h-4 w-4" />;
      case 'csv':
      case 'xlsx':
        return <FileSpreadsheet className="h-4 w-4" />;
      case 'json':
      case 'xml':
        return <FileCode className="h-4 w-4" />;
      default:
        return <FolderOpen className="h-4 w-4" />;
    }
  };

  // Mock data for demo
  const mockIngestionJobs: IngestionJob[] = [
    {
      id: 'job_001',
      source: 'Gong Sync',
      document: 'Sales Call - Acme Corp Q2 Review',
      status: 'success',
      timestamp: '2024-07-21 10:00 AM',
      size: '1.2 MB',
      type: 'audio'
    },
    {
      id: 'job_002',
      source: 'File Upload',
      document: 'Q3_Financial_Report.pdf',
      status: 'processing',
      progress: 65,
      timestamp: '2024-07-21 10:05 AM',
      size: '3.4 MB',
      type: 'pdf'
    },
    {
      id: 'job_003',
      source: 'HubSpot Sync',
      document: 'New Contacts - July 2024',
      status: 'queued',
      timestamp: '2024-07-21 10:06 AM',
      size: '512 KB',
      type: 'csv'
    },
    {
      id: 'job_004',
      source: 'Foundational Sync',
      document: 'Employee Directory Update',
      status: 'success',
      timestamp: '2024-07-21 09:45 AM',
      size: '2.1 MB',
      type: 'database'
    },
    {
      id: 'job_005',
      source: 'Slack Sync',
      document: 'Team Conversations - Last 24h',
      status: 'processing',
      progress: 78,
      timestamp: '2024-07-21 10:10 AM',
      size: '5.3 MB',
      type: 'chat'
    }
  ];

  const mockDataSources: DataSource[] = [
    {
      id: 'gong',
      name: 'Gong.io',
      type: 'gong',
      status: 'connected',
      lastSync: '10 minutes ago',
      documentCount: 1234,
      nextSync: 'in 20 minutes'
    },
    {
      id: 'hubspot',
      name: 'HubSpot CRM',
      type: 'hubspot',
      status: 'connected',
      lastSync: '1 hour ago',
      documentCount: 5678,
      nextSync: 'in 30 minutes'
    },
    {
      id: 'snowflake',
      name: 'Snowflake Analytics',
      type: 'snowflake',
      status: 'connected',
      lastSync: '2 hours ago',
      documentCount: 890,
      nextSync: 'in 4 hours'
    },
    {
      id: 'foundational',
      name: 'Pay Ready Foundation',
      type: 'api',
      status: 'connected',
      lastSync: '30 minutes ago',
      documentCount: 2456,
      nextSync: 'Daily at 2 AM'
    },
    {
      id: 'slack',
      name: 'Slack Workspace',
      type: 'api',
      status: 'connected',
      lastSync: '5 minutes ago',
      documentCount: 8934,
      nextSync: 'Every 15 minutes'
    }
  ];

  const mockStats: KnowledgeStats = {
    totalDocuments: 18192, // Updated to include foundational + slack
    totalSize: '67.3 GB', // Updated size
    recentIngestions: 234, // Updated count
    activeProcessing: 5, // Updated count
    searchQueries: 6789, // Updated count
    avgQueryTime: 98 // Improved performance
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Knowledge Management</h1>
        <p className="text-gray-600 mt-1">Comprehensive knowledge base with foundational data and team insights</p>
      </div>

      {/* Enhanced Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Total Documents</CardTitle>
          </CardHeader>
          <CardContent className="">
            <div className="text-2xl font-bold">{mockStats.totalDocuments.toLocaleString()}</div>
            <p className="text-xs text-gray-500">Including foundational data</p>
          </CardContent>
        </Card>
        
        <Card className="">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Storage Used</CardTitle>
          </CardHeader>
          <CardContent className="">
            <div className="text-2xl font-bold">{mockStats.totalSize}</div>
            <p className="text-xs text-gray-500">Vector + document storage</p>
          </CardContent>
        </Card>
        
        <Card className="">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Recent Ingestions</CardTitle>
          </CardHeader>
          <CardContent className="">
            <div className="text-2xl font-bold">{mockStats.recentIngestions}</div>
            <p className="text-xs text-gray-500">Last 24 hours</p>
          </CardContent>
        </Card>
        
        <Card className="">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Avg Query Time</CardTitle>
          </CardHeader>
          <CardContent className="">
            <div className="text-2xl font-bold">{mockStats.avgQueryTime}ms</div>
            <p className="text-xs text-gray-500">p95 response time</p>
          </CardContent>
        </Card>
      </div>

      {/* Enhanced Main Content with New Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="sources">Data Sources</TabsTrigger>
          <TabsTrigger value="ingestion">Ingestion</TabsTrigger>
          <TabsTrigger value="foundational">
            <Users className="h-4 w-4 mr-2" />
            Foundational
          </TabsTrigger>
          <TabsTrigger value="slack">
            <MessageSquare className="h-4 w-4 mr-2" />
            Slack Knowledge
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab - Enhanced */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-6 lg:grid-cols-2">
            {/* Recent Ingestion Jobs */}
            <Card className="">
              <CardHeader className="">
                <CardTitle>Recent Ingestion Activity</CardTitle>
                <CardDescription>Latest document processing across all sources</CardDescription>
              </CardHeader>
              <CardContent className="">
                <div className="space-y-3">
                  {mockIngestionJobs.slice(0, 5).map((job) => (
                    <div key={job.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-3">
                        {getStatusIcon(job.status)}
                        <div>
                          <p className="font-medium text-sm">{job.document}</p>
                          <p className="text-xs text-gray-500">{job.source} • {job.timestamp}</p>
                        </div>
                      </div>
                      {job.progress && (
                        <div className="w-24">
                          <Progress className="" value={job.progress} className="h-2" />
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Enhanced Quick Actions */}
            <Card className="">
              <CardHeader className="">
                <CardTitle>Quick Actions</CardTitle>
                <CardDescription>Knowledge management operations</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* File Upload */}
                <div className="space-y-2">
                  <label className="text-sm font-medium">Upload Document</label>
                  <div className="flex gap-2">
                    <Input
                      type="file"
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSelectedFile(e.target.files?.[0] || null)}
                      className="flex-1"
                    />
                    <Button className="" variant="default" size="default" onClick={handleFileUpload} disabled={!selectedFile}>
                      <Upload className="h-4 w-4 mr-2" />
                      Upload
                    </Button>
                  </div>
                </div>

                {/* Enhanced Data Source Actions */}
                <div className="space-y-2">
                  <label className="text-sm font-medium">Sync Data Sources</label>
                  <div className="grid grid-cols-2 gap-2">
                    {mockDataSources.map((source) => (
                      <Button
                        key={source.id}
                        variant="outline"
                        size="sm"
                        onClick={() => handleDataSourceSync(source.id)}
                        disabled={syncing === source.id || source.status === 'disconnected'}
                        className="justify-start"
                      >
                        {syncing === source.id ? (
                          <Loader2 className="h-3 w-3 mr-2 animate-spin" />
                        ) : (
                          <RefreshCw className="h-3 w-3 mr-2" />
                        )}
                        {source.name}
                      </Button>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Enhanced Data Sources Tab */}
        <TabsContent value="sources" className="space-y-4">
          <Card className="">
            <CardHeader className="">
              <CardTitle>Connected Data Sources</CardTitle>
              <CardDescription>Manage your comprehensive knowledge base integrations</CardDescription>
            </CardHeader>
            <CardContent className="">
              <Table className="">
                <TableHeader className="">
                  <TableRow className="">
                    <TableHead>Source</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Documents</TableHead>
                    <TableHead>Last Sync</TableHead>
                    <TableHead>Next Sync</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody className="">
                  {mockDataSources.map((source) => (
                    <TableRow key={source.id}>
                      <TableCell className="font-medium">
                        <div className="flex items-center gap-2">
                          <Database className="h-4 w-4" />
                          {source.name}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">{source.type}</Badge>
                      </TableCell>
                      <TableCell className="">
                        <div className="flex items-center gap-2">
                          {getStatusIcon(source.status)}
                          <Badge
                            variant={
                              source.status === 'connected' ? 'default' :
                              source.status === 'syncing' ? 'secondary' :
                              'destructive'
                            }
                          >
                            {source.status}
                          </Badge>
                        </div>
                      </TableCell>
                      <TableCell>{source.documentCount.toLocaleString()}</TableCell>
                      <TableCell>{source.lastSync}</TableCell>
                      <TableCell>{source.nextSync || '-'}</TableCell>
                      <TableCell className="">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDataSourceSync(source.id)}
                          disabled={syncing === source.id || source.status === 'disconnected'}
                        >
                          {syncing === source.id ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          ) : (
                            'Sync Now'
                          )}
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Enhanced Ingestion Tab */}
        <TabsContent value="ingestion" className="space-y-4">
          <Card className="">
            <CardHeader className="">
              <CardTitle>Ingestion History</CardTitle>
              <CardDescription>Complete history of document processing across all sources</CardDescription>
            </CardHeader>
            <CardContent className="">
              <Table className="">
                <TableHeader className="">
                  <TableRow className="">
                    <TableHead>Document</TableHead>
                    <TableHead>Source</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Size</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Progress</TableHead>
                    <TableHead>Timestamp</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody className="">
                  {mockIngestionJobs.map((job) => (
                    <TableRow key={job.id}>
                      <TableCell className="font-medium">
                        <div className="flex items-center gap-2">
                          {getFileIcon(job.type)}
                          {job.document}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">{job.source}</Badge>
                      </TableCell>
                      <TableCell>{job.type}</TableCell>
                      <TableCell>{job.size}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {getStatusIcon(job.status)}
                          <span className="capitalize">{job.status}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        {job.progress ? (
                          <div className="w-full">
                            <Progress value={job.progress} className="h-2" />
                            <span className="text-xs text-gray-500">{job.progress}%</span>
                          </div>
                        ) : (
                          '-'
                        )}
                      </TableCell>
                      <TableCell>{job.timestamp}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* New Foundational Knowledge Tab */}
        <TabsContent value="foundational" className="space-y-4">
          <FoundationalKnowledgeTab />
        </TabsContent>

        {/* New Slack Knowledge Tab */}
        <TabsContent value="slack" className="space-y-4">
          <SlackKnowledgeTab />
        </TabsContent>
      </Tabs>

      {/* Enhanced Universal Chat Interface */}
      <div className="mt-8">
        <EnhancedUnifiedChatInterface
          context={chatContext}
          height="600px"
          title="Knowledge Base Assistant"
          placeholder="Search across all knowledge sources: foundational data, Gong calls, Slack conversations, documents..."
        />
      </div>
    </div>
  );
};

export default EnhancedKnowledgeDashboard;

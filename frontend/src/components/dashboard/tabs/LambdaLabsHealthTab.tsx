import React, { useState, useEffect } from 'react';
// NOTE: Monitoring 48+ MCP servers dynamically loaded from backend
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Activity, Server, Cpu, HardDrive, MemoryStick, Network, RefreshCw, AlertTriangle, CheckCircle, XCircle, Clock, Zap, Database, GitBranch, Monitor } from 'lucide-react';
import { Line, Doughnut } from 'react-chartjs-2';
import apiClient from '../../../services/apiClient';

// Types
interface LambdaLabsInstance {
  id: string;
  name: string;
  ip: string;
  gpu_type: string;
  status: 'healthy' | 'degraded' | 'unhealthy';
  cpu_usage: number;
  memory_usage: number;
  gpu_usage: number;
  disk_usage: number;
  network_in: number;
  network_out: number;
  uptime: string;
  last_seen: string;
  services_count: number;
  containers_running: number;
  containers_total: number;
  temperature: number;
  power_consumption: number;
}

interface MCPServer {
  id: string;
  name: string;
  port: number;
  status: 'healthy' | 'degraded' | 'unhealthy' | 'unreachable';
  response_time: number;
  last_check: string;
  error_rate: number;
  requests_per_minute: number;
  memory_usage: number;
  cpu_usage: number;
  version: string;
  instance_id: string;
  tools_count: number;
  active_connections: number;
}

interface HealthMetrics {
  overall_health: number;
  instances: LambdaLabsInstance[];
  mcp_servers: MCPServer[];
  alerts: Array<{
    id: string;
    severity: 'critical' | 'warning' | 'info';
    title: string;
    message: string;
    timestamp: string;
    instance?: string;
    server?: string;
  }>;
  performance_trends: {
    labels: string[];
    cpu: number[];
    memory: number[];
    gpu: number[];
  };
}

// Status Components
const StatusBadge: React.FC<{ status: string; size?: 'sm' | 'md' }> = ({ status, size = 'sm' }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'bg-green-500';
      case 'degraded': return 'bg-yellow-500';
      case 'unhealthy': return 'bg-red-500';
      case 'unreachable': return 'bg-gray-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return <CheckCircle className="h-3 w-3" />;
      case 'degraded': return <AlertTriangle className="h-3 w-3" />;
      case 'unhealthy': return <XCircle className="h-3 w-3" />;
      case 'unreachable': return <Clock className="h-3 w-3" />;
      default: return <Clock className="h-3 w-3" />;
    }
  };

  return (
    <Badge variant="outline" className={`flex items-center gap-1 ${size === 'md' ? 'px-3 py-1' : 'px-2 py-0.5'}`}>
      <div className={`w-2 h-2 rounded-full ${getStatusColor(status)}`} />
      {getStatusIcon(status)}
      <span className="capitalize">{status}</span>
    </Badge>
  );
};

// Resource Usage Component
const ResourceUsage: React.FC<{ label: string; value: number; icon: React.ElementType; color?: string }> = ({
  label, value, icon: Icon, color = 'blue'
}) => {
  const getColor = (value: number, color: string) => {
    if (value > 85) return 'bg-red-500';
    if (value > 70) return 'bg-yellow-500';
    return `bg-${color}-500`;
  };

  return (
    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
      <div className="flex items-center gap-2">
        <Icon className="h-4 w-4 text-gray-600" />
        <span className="text-sm font-medium">{label}</span>
      </div>
      <div className="flex items-center gap-2 min-w-[100px]">
        <Progress value={value} className="w-16 h-2" />
        <span className="text-sm font-semibold">{value}%</span>
      </div>
    </div>
  );
};

// Main Component
const LambdaLabsHealthTab: React.FC = () => {
  const [healthData, setHealthData] = useState<HealthMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [lastRefresh, setLastRefresh] = useState(new Date());
  const [selectedInstance, setSelectedInstance] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Fetch health data
  const fetchHealthData = async () => {
    setIsLoading(true);
    try {
      const response = await apiClient.get('/api/v1/lambda-labs/health');
      setHealthData(response.data);
      setLastRefresh(new Date());
    } catch (error) {
      console.error('Failed to fetch Lambda Labs health data:', error);
      // Mock data for development
      setHealthData({
        overall_health: 87,
        instances: [
          {
            id: 'platform-prod',
            name: 'sophia-platform-prod',
            ip: '146.235.200.1',
            gpu_type: 'GPU 1x A10',
            status: 'healthy',
            cpu_usage: 45,
            memory_usage: 67,
            gpu_usage: 23,
            disk_usage: 34,
            network_in: 12.5,
            network_out: 8.3,
            uptime: '15d 6h 23m',
            last_seen: '2025-07-05T11:00:00Z',
            services_count: 8,
            containers_running: 12,
            containers_total: 15,
            temperature: 65,
            power_consumption: 280
          },
          {
            id: 'mcp-prod',
            name: 'sophia-mcp-prod',
            ip: '165.1.69.44',
            gpu_type: 'GPU 1x A10',
            status: 'healthy',
            cpu_usage: 32,
            memory_usage: 54,
            gpu_usage: 78,
            disk_usage: 28,
            network_in: 8.7,
            network_out: 15.2,
            uptime: '12d 14h 56m',
            last_seen: '2025-07-05T11:01:00Z',
            services_count: 11,
            containers_running: 8,
            containers_total: 8,
            temperature: 72,
            power_consumption: 315
          },
          {
            id: 'ai-prod',
            name: 'sophia-ai-prod',
            ip: '137.131.6.213',
            gpu_type: 'GPU 1x A100',
            status: 'degraded',
            cpu_usage: 78,
            memory_usage: 89,
            gpu_usage: 92,
            disk_usage: 56,
            network_in: 25.4,
            network_out: 31.8,
            uptime: '8d 2h 15m',
            last_seen: '2025-07-05T10:58:00Z',
            services_count: 6,
            containers_running: 15,
            containers_total: 18,
            temperature: 84,
            power_consumption: 420
          }
        ],
        mcp_servers: [
          {
            id: 'ai-memory',
            name: 'ai-memory-mcp',
            port: 9001,
            status: 'healthy',
            response_time: 45,
            last_check: '2025-07-05T11:00:30Z',
            error_rate: 0.2,
            requests_per_minute: 150,
            memory_usage: 32,
            cpu_usage: 15,
            version: '1.2.3',
            instance_id: 'mcp-prod',
            tools_count: 8,
            active_connections: 12
          },
          {
            id: 'codacy',
            name: 'codacy-mcp',
            port: 3008,
            status: 'healthy',
            response_time: 23,
            last_check: '2025-07-05T11:00:25Z',
            error_rate: 0.1,
            requests_per_minute: 85,
            memory_usage: 28,
            cpu_usage: 12,
            version: '2.1.0',
            instance_id: 'mcp-prod',
            tools_count: 6,
            active_connections: 8
          },
          {
            id: 'linear',
            name: 'linear-mcp',
            port: 9004,
            status: 'healthy',
            response_time: 67,
            last_check: '2025-07-05T11:00:20Z',
            error_rate: 0.3,
            requests_per_minute: 42,
            memory_usage: 24,
            cpu_usage: 8,
            version: '1.5.2',
            instance_id: 'mcp-prod',
            tools_count: 12,
            active_connections: 6
          },
          {
            id: 'ELIMINATED-admin',
            name: 'ELIMINATED-admin-mcp',
            port: 9020,
            status: 'degraded',
            response_time: 234,
            last_check: '2025-07-05T11:00:15Z',
            error_rate: 2.1,
            requests_per_minute: 28,
            memory_usage: 45,
            cpu_usage: 34,
            version: '1.8.1',
            instance_id: 'ai-prod',
            tools_count: 15,
            active_connections: 4
          },
          {
            id: 'github',
            name: 'github-mcp',
            port: 9003,
            status: 'unhealthy',
            response_time: 0,
            last_check: '2025-07-05T10:55:10Z',
            error_rate: 100,
            requests_per_minute: 0,
            memory_usage: 0,
            cpu_usage: 0,
            version: '1.1.5',
            instance_id: 'platform-prod',
            tools_count: 0,
            active_connections: 0
          }
        ],
        alerts: [
          {
            id: 'alert-1',
            severity: 'critical',
            title: 'GitHub MCP Server Down',
            message: 'GitHub MCP server has been unreachable for 5 minutes',
            timestamp: '2025-07-05T10:55:10Z',
            instance: 'platform-prod',
            server: 'github-mcp'
          },
          {
            id: 'alert-2',
            severity: 'warning',
            title: 'High GPU Usage',
            message: 'sophia-ai-prod GPU usage at 92%',
            timestamp: '2025-07-05T10:58:00Z',
            instance: 'ai-prod'
          },
          {
            id: 'alert-3',
            severity: 'warning',
            title: 'ELIMINATED Admin Slow Response',
            message: 'Response time degraded to 234ms (target: <100ms)',
            timestamp: '2025-07-05T10:59:45Z',
            server: 'ELIMINATED-admin-mcp'
          }
        ],
        performance_trends: {
          labels: ['10:50', '10:55', '11:00', '11:05', '11:10'],
          cpu: [42, 45, 48, 52, 51],
          memory: [65, 67, 70, 71, 68],
          gpu: [75, 78, 82, 85, 79]
        }
      });
    }
    setIsLoading(false);
  };

  useEffect(() => {
    fetchHealthData();
  }, []);

  // Auto-refresh effect
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(fetchHealthData, 30000); // 30 seconds
    return () => clearInterval(interval);
  }, [autoRefresh]);

  if (!healthData) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <Activity className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-500" />
          <p className="text-gray-600">Loading Lambda Labs health data...</p>
        </div>
      </div>
    );
  }

  const healthyInstances = healthData.instances.filter(i => i.status === 'healthy').length;
  const healthyServers = healthData.mcp_servers.filter(s => s.status === 'healthy').length;
  const criticalAlerts = healthData.alerts.filter(a => a.severity === 'critical').length;

  return (
    <div className="space-y-6">
      {/* Header with Controls */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Lambda Labs Health Monitor</h2>
          <p className="text-sm text-gray-500">
            Last updated: {lastRefresh.toLocaleTimeString()} • Overall Health: {healthData.overall_health}%
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setAutoRefresh(!autoRefresh)}
          >
            <Activity className={`h-4 w-4 mr-2 ${autoRefresh ? 'animate-pulse' : ''}`} />
            Auto-refresh {autoRefresh ? 'ON' : 'OFF'}
          </Button>
          <Button
            onClick={fetchHealthData}
            disabled={isLoading}
            variant="outline"
            size="sm"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Health Overview KPIs */}
      <div className="grid gap-6 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Overall Health</CardTitle>
            <Monitor className="h-4 w-4 text-gray-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">{healthData.overall_health}%</div>
            <Progress value={healthData.overall_health} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Instances</CardTitle>
            <Server className="h-4 w-4 text-gray-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">
              {healthyInstances}/{healthData.instances.length}
            </div>
            <p className="text-xs text-green-500">Healthy</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">MCP Servers</CardTitle>
            <Database className="h-4 w-4 text-gray-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">
              {healthyServers}/{healthData.mcp_servers.length}
            </div>
            <p className="text-xs text-green-500">Operational</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Critical Alerts</CardTitle>
            <AlertTriangle className="h-4 w-4 text-gray-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{criticalAlerts}</div>
            <p className="text-xs text-red-500">Require attention</p>
          </CardContent>
        </Card>
      </div>

      {/* Alerts Section */}
      {healthData.alerts.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">Active Alerts</h3>
          {healthData.alerts.map((alert) => (
            <Alert key={alert.id} variant={alert.severity === 'critical' ? 'destructive' : 'default'}>
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                <div className="flex items-center justify-between">
                  <div>
                    <strong>{alert.title}</strong>
                    <p className="text-sm mt-1">{alert.message}</p>
                    {(alert.instance || alert.server) && (
                      <p className="text-xs text-gray-500 mt-1">
                        {alert.instance && `Instance: ${alert.instance}`}
                        {alert.instance && alert.server && ' • '}
                        {alert.server && `Server: ${alert.server}`}
                      </p>
                    )}
                  </div>
                  <div className="text-right">
                    <Badge variant={alert.severity === 'critical' ? 'destructive' : 'secondary'}>
                      {alert.severity}
                    </Badge>
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(alert.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              </AlertDescription>
            </Alert>
          ))}
        </div>
      )}

      {/* Lambda Labs Instances */}
      <div className="grid gap-6 lg:grid-cols-2 xl:grid-cols-3">
        {healthData.instances.map((instance) => (
          <Card key={instance.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-base">{instance.name}</CardTitle>
                <StatusBadge status={instance.status} size="md" />
              </div>
              <div className="flex items-center justify-between text-sm text-gray-500">
                <span>{instance.ip}</span>
                <span>{instance.gpu_type}</span>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <ResourceUsage label="CPU" value={instance.cpu_usage} icon={Cpu} color="blue" />
              <ResourceUsage label="Memory" value={instance.memory_usage} icon={MemoryStick} color="green" />
              <ResourceUsage label="GPU" value={instance.gpu_usage} icon={Zap} color="purple" />
              <ResourceUsage label="Disk" value={instance.disk_usage} icon={HardDrive} color="orange" />

              <div className="grid grid-cols-2 gap-2 pt-2 border-t">
                <div className="text-center">
                  <p className="text-sm font-medium">{instance.containers_running}</p>
                  <p className="text-xs text-gray-500">Containers</p>
                </div>
                <div className="text-center">
                  <p className="text-sm font-medium">{instance.services_count}</p>
                  <p className="text-xs text-gray-500">Services</p>
                </div>
                <div className="text-center">
                  <p className="text-sm font-medium">{instance.temperature}°C</p>
                  <p className="text-xs text-gray-500">Temperature</p>
                </div>
                <div className="text-center">
                  <p className="text-sm font-medium">{instance.power_consumption}W</p>
                  <p className="text-xs text-gray-500">Power</p>
                </div>
              </div>

              <div className="text-xs text-gray-500 pt-2 border-t">
                <p>Uptime: {instance.uptime}</p>
                <p>Last seen: {new Date(instance.last_seen).toLocaleString()}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* MCP Servers Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Database />
            <span>MCP Servers Status</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Server</TableHead>
                <TableHead>Instance</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Response Time</TableHead>
                <TableHead>Error Rate</TableHead>
                <TableHead>RPM</TableHead>
                <TableHead>Memory</TableHead>
                <TableHead>Tools</TableHead>
                <TableHead>Connections</TableHead>
                <TableHead>Version</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {healthData.mcp_servers.map((server) => (
                <TableRow key={server.id}>
                  <TableCell className="font-medium">
                    <div>
                      <p>{server.name}</p>
                      <p className="text-xs text-gray-500">:{server.port}</p>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{server.instance_id}</Badge>
                  </TableCell>
                  <TableCell>
                    <StatusBadge status={server.status} />
                  </TableCell>
                  <TableCell>
                    <span className={server.response_time > 100 ? 'text-yellow-600' : server.response_time > 200 ? 'text-red-600' : 'text-green-600'}>
                      {server.response_time}ms
                    </span>
                  </TableCell>
                  <TableCell>
                    <span className={server.error_rate > 1 ? 'text-red-600' : server.error_rate > 0.5 ? 'text-yellow-600' : 'text-green-600'}>
                      {server.error_rate}%
                    </span>
                  </TableCell>
                  <TableCell>{server.requests_per_minute}</TableCell>
                  <TableCell>
                    <Progress value={server.memory_usage} className="w-16 h-2" />
                    <span className="text-xs ml-1">{server.memory_usage}%</span>
                  </TableCell>
                  <TableCell>{server.tools_count}</TableCell>
                  <TableCell>{server.active_connections}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{server.version}</Badge>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Performance Trends */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Resource Usage Trends (Last Hour)</CardTitle>
          </CardHeader>
          <CardContent>
            <Line
              data={{
                labels: healthData.performance_trends.labels,
                datasets: [
                  {
                    label: 'CPU %',
                    data: healthData.performance_trends.cpu,
                    borderColor: '#3B82F6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4
                  },
                  {
                    label: 'Memory %',
                    data: healthData.performance_trends.memory,
                    borderColor: '#10B981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4
                  },
                  {
                    label: 'GPU %',
                    data: healthData.performance_trends.gpu,
                    borderColor: '#8B5CF6',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    tension: 0.4
                  }
                ]
              }}
              options={{
                responsive: true,
                plugins: {
                  legend: { position: 'top' }
                },
                scales: {
                  y: { beginAtZero: true, max: 100 }
                }
              }}
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>MCP Server Status Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <Doughnut
              data={{
                labels: ['Healthy', 'Degraded', 'Unhealthy', 'Unreachable'],
                datasets: [{
                  data: [
                    healthData.mcp_servers.filter(s => s.status === 'healthy').length,
                    healthData.mcp_servers.filter(s => s.status === 'degraded').length,
                    healthData.mcp_servers.filter(s => s.status === 'unhealthy').length,
                    healthData.mcp_servers.filter(s => s.status === 'unreachable').length
                  ],
                  backgroundColor: ['#10B981', '#F59E0B', '#EF4444', '#6B7280']
                }]
              }}
              options={{
                responsive: true,
                plugins: {
                  legend: { position: 'right' }
                }
              }}
            />
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default LambdaLabsHealthTab;

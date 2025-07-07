import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Server, GitBranch, DollarSign, Activity, CheckCircle, Clock, AlertTriangle } from 'lucide-react';
import { useOptimizedQuery } from '@/hooks/useDataFetching';

interface DeploymentStatusData {
  infrastructure_ready: boolean;
  services_deployed: number;
  total_services: number;
  readiness_percentage: number;
  last_deployment: string;
  deployment_health: number;
  cost_metrics: {
    monthly_savings: number;
    cost_reduction_percentage: number;
    gpu_memory_increase: string;
    infrastructure_cost: number;
  };
  service_health: Array<{
    name: string;
    status: string;
    uptime: string;
  }>;
}

const ProductionDeploymentTab: React.FC = () => {
  const { data: deploymentData, isLoading } = useOptimizedQuery<DeploymentStatusData>(
    ['deploymentStatus'],
    '/api/v1/deployment/status',
    { refetchInterval: 60000 }
  );

  const { data: timelineData } = useOptimizedQuery(
    ['deploymentTimeline'],
    '/api/v1/deployment/timeline',
    { refetchInterval: 120000 }
  );

  if (isLoading || !deploymentData) {
    return <div>Loading deployment status...</div>;
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'restarting': return <Clock className="h-4 w-4 text-yellow-500" />;
      default: return <AlertTriangle className="h-4 w-4 text-red-500" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Deployment Overview Cards */}
      <div className="grid gap-6 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Deployment Health</CardTitle>
            <Activity className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{deploymentData.deployment_health}%</div>
            <Progress value={deploymentData.deployment_health} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Services Ready</CardTitle>
            <Server className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {deploymentData.services_deployed}/{deploymentData.total_services}
            </div>
            <p className="text-xs text-gray-600">
              {deploymentData.readiness_percentage}% ready
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Cost Savings</CardTitle>
            <DollarSign className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${deploymentData.cost_metrics.monthly_savings}
            </div>
            <p className="text-xs text-green-600">
              {deploymentData.cost_metrics.cost_reduction_percentage}% reduction
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">GPU Memory</CardTitle>
            <GitBranch className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {deploymentData.cost_metrics.gpu_memory_increase}
            </div>
            <p className="text-xs text-purple-600">Performance increase</p>
          </CardContent>
        </Card>
      </div>

      {/* Service Health Matrix */}
      <Card>
        <CardHeader>
          <CardTitle>Service Health Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            {deploymentData.service_health.map((service) => (
              <div key={service.name} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center gap-3">
                  {getStatusIcon(service.status)}
                  <div>
                    <div className="font-medium">{service.name}</div>
                    <div className="text-sm text-gray-500">Uptime: {service.uptime}</div>
                  </div>
                </div>
                <Badge variant={service.status === 'healthy' ? 'default' : 'secondary'}>
                  {service.status}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Deployment Timeline */}
      {timelineData && (
        <Card>
          <CardHeader>
            <CardTitle>Deployment Timeline</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {timelineData.phases.map((phase, index) => (
                <div key={phase.name} className="flex items-center gap-4">
                  <div className={`w-4 h-4 rounded-full ${
                    phase.status === 'completed' ? 'bg-green-500' :
                    phase.status === 'in_progress' ? 'bg-blue-500' : 'bg-gray-300'
                  }`} />
                  <div className="flex-1">
                    <div className="font-medium">{phase.name}</div>
                    <div className="text-sm text-gray-500">Duration: {phase.duration}</div>
                  </div>
                  <Badge variant={
                    phase.status === 'completed' ? 'default' :
                    phase.status === 'in_progress' ? 'secondary' : 'outline'
                  }>
                    {phase.status.replace('_', ' ')}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default ProductionDeploymentTab;

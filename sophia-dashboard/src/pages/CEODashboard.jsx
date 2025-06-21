// src/pages/CEODashboard.jsx
import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, TrendingDown, Minus, DollarSign, Users, Activity, CheckCircle } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { fetchAgnoPerformanceMetrics } from '@/services/apiClient';

// --- AI-Generated Component: KpiCardV1 ---
// This component would normally be in its own file (`/components/generated/KpiCardV1.jsx`),
// but is embedded here to bypass file creation issues.
const KpiCardV1 = ({ title, value, change, changeType, icon: Icon }) => {
  const trendColor = changeType === 'increase' ? 'text-green-500' : 'text-red-500';
  const TrendIcon = changeType === 'increase' ? TrendingUp : changeType === 'decrease' ? TrendingDown : Minus;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-gray-500">{title}</CardTitle>
        {Icon && <Icon className="h-4 w-4 text-gray-400" />}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-gray-800">{value}</div>
        <p className="text-xs text-gray-500 flex items-center">
          <TrendIcon className={`h-4 w-4 mr-1 ${trendColor}`} />
          <span className={`${trendColor} mr-1`}>{change}</span>
          from last month
        </p>
      </CardContent>
    </Card>
  );
};
// --- End AI-Generated Component ---

// Mock Data for the new component
const kpiData = [
  { title: 'Monthly Recurring Revenue', value: '$2.1M', change: '+3.2%', changeType: 'increase', icon: DollarSign },
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

const CEODashboard = () => {
  // State for Agno performance metrics
  const [agnoMetrics, setAgnoMetrics] = useState(null);
  const [agnoLoading, setAgnoLoading] = useState(true);
  const [agnoError, setAgnoError] = useState(null);

  useEffect(() => {
    let mounted = true;
    setAgnoLoading(true);
    fetchAgnoPerformanceMetrics()
      .then((data) => {
        if (mounted) {
          setAgnoMetrics(data);
          setAgnoLoading(false);
        }
      })
      .catch((err) => {
        if (mounted) {
          setAgnoError('Failed to load Agno metrics');
          setAgnoLoading(false);
        }
      });
    return () => { mounted = false; };
  }, []);

  // Compute KPI and details from live data or fallback
  let agnoKpi = {
    title: 'Agno Agent Instantiation',
    value: agnoMetrics?.summary?.call_analysis?.avg_instantiation_us
      ? `${agnoMetrics.summary.call_analysis.avg_instantiation_us}μs`
      : '—',
    change: '-99.9%',
    changeType: 'increase',
    icon: Activity,
  };
  let agnoDetails = agnoMetrics?.summary?.call_analysis || {};
  let agnoLastUpdated = agnoMetrics?.last_updated || '';

  return (
    <div className="p-4 md:p-8 bg-gray-50 min-h-screen">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800">CEO Command Center</h1>
        <p className="text-gray-600">Unified view of business performance and AI operations.</p>
      </header>

      {/* KPI Cards - NOW USING THE NEW AI-GENERATED COMPONENT */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
        {kpiData.map((kpi, index) => (
          <KpiCardV1
            key={index}
            title={kpi.title}
            value={kpi.value}
            change={kpi.change}
            changeType={kpi.changeType}
            icon={kpi.icon}
          />
        ))}
        {/* Agno Performance KPI */}
        <KpiCardV1
          title={agnoKpi.title}
          value={agnoLoading ? 'Loading...' : agnoKpi.value}
          change={agnoKpi.change}
          changeType={agnoKpi.changeType}
          icon={agnoKpi.icon}
        />
      </div>

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">AI Operations Overview</TabsTrigger>
          <TabsTrigger value="interaction">Agent Interaction</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>LLM Cost Analysis</CardTitle>
            </CardHeader>
            <CardContent className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={llmCostData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="cost" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Agno Performance Metrics Section */}
          <Card>
            <CardHeader>
              <CardTitle>Agno Agent Performance</CardTitle>
            </CardHeader>
            <CardContent>
              {agnoLoading ? (
                <div className="text-gray-400">Loading Agno performance metrics...</div>
              ) : agnoError ? (
                <div className="text-red-500">{agnoError}</div>
              ) : (
                <div>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <div>
                      <div className="text-xs text-gray-500">Avg Instantiation</div>
                      <div className="text-lg font-bold">{agnoDetails.avg_instantiation_us ? `${agnoDetails.avg_instantiation_us}μs` : '—'}</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">Pool Size</div>
                      <div className="text-lg font-bold">{agnoDetails.pool_size ?? '—'} / {agnoDetails.pool_max ?? '—'}</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">Instantiation Samples</div>
                      <div className="text-lg font-bold">{agnoDetails.instantiation_samples ?? '—'}</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">Last Updated</div>
                      <div className="text-lg font-bold">{agnoLastUpdated}</div>
                    </div>
                  </div>
                  <div className="mt-4 text-xs text-gray-400">
                    <span>Agno-powered agent instantiation is up to 5000x faster and 50x more memory efficient than legacy agents.</span>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Interaction Tab */}
        <TabsContent value="interaction" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Interact with Executive Agent</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Ask a question or delegate a task to the primary executive agent.
              </p>
              <div className="flex space-x-2">
                <Input placeholder="e.g., 'Summarize the top 5 deals from last week.'" />
                <Button>Submit Task</Button>
              </div>
              <div className="mt-4 p-4 border rounded-lg bg-gray-50 min-h-[100px]">
                <p className="text-sm text-gray-500">Agent response will appear here...</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default CEODashboard;

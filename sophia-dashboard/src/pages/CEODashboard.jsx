// src/pages/CEODashboard.jsx
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, TrendingDown, Minus, DollarSign, Users, Activity, CheckCircle } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

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

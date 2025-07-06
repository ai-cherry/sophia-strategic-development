import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Progress } from "@/components/ui/progress"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { MessageCircle, Search, TrendingUp, AlertTriangle, Users, Target, Calendar, DollarSign, Activity, BarChart3, PieChart, LineChart, Send, Loader2, RefreshCw, Settings, Bell, Download, Share2, Maximize2, BrainCircuit, Database, GitBranch, Briefcase } from 'lucide-react';
import { Line, Bar, Pie, Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Title, Tooltip, Legend, Filler } from 'chart.js';
import apiClient from '../../services/apiClient';
import EnhancedUnifiedChat from "@/components/shared/EnhancedUnifiedChat";
import { CacheMonitoringWidget } from './CacheMonitoringWidget';
import WorkflowDesignerTab from './tabs/WorkflowDesignerTab';
import LambdaLabsHealthTab from './tabs/LambdaLabsHealthTab';
import { useOptimizedQuery } from "@/hooks/useDataFetching";
import { FullDashboardSkeleton, DataFetchError } from "@/components/shared/StatefulComponents";
import { DashboardData } from "@/types";
import KPICards from "./KPICards";
import SalesRevenueChart from "./SalesRevenueChart";
import DealStageDistribution from "./DealStageDistribution";
import ActivityFeed from "./ActivityFeed";
import HealthMonitoringTab from "./tabs/HealthMonitoringTab";
import DataFlowTab from "./tabs/DataFlowTab";
import AsanaProjectTab from "./tabs/AsanaProjectTab";

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Title, Tooltip, Legend, Filler);

// --- Reusable Components ---
const UnifiedKPICard = ({ title, value, change, changeType, icon: Icon }) => (
    <Card className="hover:shadow-lg transition-all duration-300">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">{title}</CardTitle>
            <Icon className="h-4 w-4 text-gray-400" />
        </CardHeader>
        <CardContent>
            <div className="text-2xl font-bold text-gray-900">{value}</div>
            {change && <p className={`text-xs ${changeType === 'increase' ? 'text-green-500' : 'text-red-500'}`}>{change}</p>}
        </CardContent>
    </Card>
);

const UnifiedDashboard = () => {
    const { data: dashboardData, isLoading, error, refetch } = useOptimizedQuery<DashboardData>(
        ['dashboardData'],
        '/api/v1/dashboard/main'
    );

    if (isLoading) {
        return <FullDashboardSkeleton />;
    }

    if (error) {
        return (
            <div className="p-8">
                <DataFetchError error={error} onRetry={refetch} />
            </div>
        );
    }

    // Fallback for safety, though react-query's `error` state should catch this.
    if (!dashboardData) {
        return <div className="p-8">No dashboard data available.</div>;
    }

    return (
        <div className="min-h-screen bg-gray-50/50">
            <main className="p-4 sm:p-6 lg:p-8">
                <Tabs defaultValue="overview">
                    <div className="flex justify-between items-center mb-4">
                        <TabsList>
                            <TabsTrigger value="overview">Overview</TabsTrigger>
                            <TabsTrigger value="health">System Health</TabsTrigger>
                            <TabsTrigger value="data-flow">Data Flow</TabsTrigger>
                            <TabsTrigger value="projects">Projects</TabsTrigger>
                        </TabsList>
                        <Button variant="outline" size="sm" onClick={() => refetch()}>
                            <RefreshCw className="h-4 w-4 mr-2" />
                            Refresh Data
                        </Button>
                    </div>
                    <TabsContent value="overview">
                        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                            <KPICards kpiData={dashboardData.kpis} />
                        </div>
                        <div className="grid gap-6 mt-6 grid-cols-1 lg:grid-cols-5">
                            <div className="lg:col-span-3">
                                <SalesRevenueChart salesData={dashboardData.sales_revenue} />
                            </div>
                            <div className="lg:col-span-2">
                                <DealStageDistribution dealData={dashboardData.deal_stages} />
                            </div>
                        </div>
                         <div className="mt-6">
                            <ActivityFeed activities={dashboardData.activity_feed} />
                        </div>
                    </TabsContent>
                    <TabsContent value="health">
                        <HealthMonitoringTab />
                    </TabsContent>
                    <TabsContent value="data-flow">
                        <DataFlowTab />
                    </TabsContent>
                    <TabsContent value="projects">
                        <AsanaProjectTab />
                    </TabsContent>
                </Tabs>
                <div className="mt-8">
                  <EnhancedUnifiedChat />
                </div>
            </main>
        </div>
    );
};

export default UnifiedDashboard;

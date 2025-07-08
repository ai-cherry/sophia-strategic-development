import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  DollarSign,
  CreditCard,
  Users,
  Activity,
} from "lucide-react";
import { MainNav } from "./components/main-nav";
import { Search } from "./components/search";
import TeamSwitcher from "./components/team-switcher";
import { UserNav } from "./components/user-nav";
import { useOptimizedQuery } from "@/hooks/useDataFetching";
import LambdaLabsHealthTab from "./tabs/LambdaLabsHealthTab";
import DataFlowTab from "./tabs/DataFlowTab";
import AsanaProjectTab from "./tabs/AsanaProjectTab";
import AIMemoryHealthTab from "./tabs/AIMemoryHealthTab";
import ProductionDeploymentTab from "./tabs/ProductionDeploymentTab";
import SalesRevenueChart from "./SalesRevenueChart";
import DealStageDistribution from "./DealStageDistribution";
import ActivityFeed from "./ActivityFeed";
import { DashboardData } from "@/types";
import EnhancedUnifiedChat from "@/components/shared/EnhancedUnifiedChat";


export default function DashboardPage() {
    const { data: dashboardData, isLoading: isDashboardLoading } = useOptimizedQuery<DashboardData>(
        ['dashboardData'],
        '/api/v1/dashboard/main'
    );

    const { data: unifiedHealth, isLoading: isHealthLoading } = useOptimizedQuery(
        ['unifiedHealth'],
        '/api/v1/unified/health',
        { refetchInterval: 30000 }
    );

    if (isDashboardLoading || isHealthLoading || !dashboardData) {
        return (
            <div className="flex items-center justify-center h-screen bg-gray-950">
                <div className="text-gray-400">Loading dashboard...</div>
            </div>
        );
    }

    const kpis = [
        {
            title: "Total Revenue",
            value: `$${dashboardData.kpis.totalRevenue.toLocaleString()}`,
            change: `+${dashboardData.kpis.revenueChange}% from last month`,
            changeType: "increase",
            icon: DollarSign,
        },
        {
            title: "Active Deals",
            value: `+${dashboardData.kpis.activeDeals}`,
            change: `+${dashboardData.kpis.dealsChange}% from last month`,
            changeType: "increase",
            icon: CreditCard,
        },
        {
            title: "New Clients",
            value: `+${dashboardData.kpis.newClients}`,
            change: "+20.1% from last month",
            changeType: "increase",
            icon: Users,
        },
        {
            title: "System Health",
            value: `${unifiedHealth?.overall_health || 0}%`,
            change: "+5% from last hour",
            changeType: "increase",
            icon: Activity,
        },
    ];

    return (
        <>
            <div className="md:hidden">
                <img
                    src="/examples/dashboard-light.png"
                    width={1280}
                    height={866}
                    alt="Dashboard"
                    className="block dark:hidden"
                />
                <img
                    src="/examples/dashboard-dark.png"
                    width={1280}
                    height={866}
                    alt="Dashboard"
                    className="hidden dark:block"
                />
            </div>
            <div className="hidden flex-col md:flex">
                <div className="border-b">
                    <div className="flex h-16 items-center px-4">
                        <TeamSwitcher />
                        <MainNav className="mx-6" />
                        <div className="ml-auto flex items-center space-x-4">
                            <Search />
                            <UserNav />
                        </div>
                    </div>
                </div>
                <div className="flex-1 space-y-4 p-8 pt-6">
                    <div className="flex items-center justify-between space-y-2">
                        <h2 className="text-3xl font-bold tracking-tight">
                            Sophia AI Executive Dashboard
                        </h2>
                        <div className="flex items-center space-x-2">
                            <Button>Download</Button>
                        </div>
                    </div>
                    <Tabs defaultValue="overview" className="space-y-4">
                        <TabsList>
                            <TabsTrigger value="overview">Executive Overview</TabsTrigger>
                            <TabsTrigger value="health">Infrastructure Health</TabsTrigger>
                            <TabsTrigger value="ai-memory">AI Memory</TabsTrigger>
                            <TabsTrigger value="deployment">Deployment</TabsTrigger>
                            <TabsTrigger value="data-flow">Data Flow</TabsTrigger>
                            <TabsTrigger value="projects">Projects</TabsTrigger>
                        </TabsList>
                        <TabsContent value="overview" className="space-y-4">
                            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                                {kpis.map((kpi) => (
                                    <Card key={kpi.title}>
                                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                            <CardTitle className="text-sm font-medium">
                                                {kpi.title}
                                            </CardTitle>
                                            <kpi.icon className="h-4 w-4 text-muted-foreground" />
                                        </CardHeader>
                                        <CardContent>
                                            <div className="text-2xl font-bold">{kpi.value}</div>
                                            <p
                                                className={`text-xs ${
                                                    kpi.changeType === "increase"
                                                        ? "text-green-600"
                                                        : "text-red-600"
                                                }`}
                                            >
                                                {kpi.change}
                                            </p>
                                        </CardContent>
                                    </Card>
                                ))}
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
                        <TabsContent value="health" className="space-y-4">
                            <LambdaLabsHealthTab />
                        </TabsContent>
                        <TabsContent value="ai-memory">
                            <AIMemoryHealthTab />
                        </TabsContent>
                        <TabsContent value="deployment">
                            <ProductionDeploymentTab />
                        </TabsContent>
                        <TabsContent value="data-flow" className="space-y-4">
                            <DataFlowTab />
                        </TabsContent>
                        <TabsContent value="projects" className="space-y-4">
                            <AsanaProjectTab />
                        </TabsContent>
                    </Tabs>
                </div>
            </div>
            <div className="mt-8">
                <EnhancedUnifiedChat />
            </div>
        </>
    );
}

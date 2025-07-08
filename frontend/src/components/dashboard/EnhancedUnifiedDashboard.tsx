import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { cn } from "@/lib/utils"
import { format } from "date-fns"
import type { DateRange } from "react-day-picker"
import {
  DollarSign,
  CreditCard,
  Users,
  Activity,
  CalendarIcon,
  Download,
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

export default function EnhancedUnifiedDashboard() {
    const [date, setDate] = React.useState<DateRange | undefined>({
        from: new Date(2025, 0, 1),
        to: new Date(),
    });

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
        <div className="min-h-screen bg-gray-950 text-gray-50">
            {/* Navigation Bar */}
            <div className="border-b border-gray-800">
                <div className="flex h-16 items-center px-4 bg-gray-900">
                    <TeamSwitcher />
                    <MainNav className="mx-6" />
                    <div className="ml-auto flex items-center space-x-4">
                        <Search />
                        <UserNav />
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
                {/* Header */}
                <div className="flex items-center justify-between space-y-2">
                    <h2 className="text-3xl font-bold tracking-tight text-gray-50">
                        Sophia AI Executive Dashboard
                    </h2>
                    <div className="flex items-center space-x-2">
                        <Popover>
                            <PopoverTrigger asChild>
                                <Button
                                    id="date"
                                    variant="outline"
                                    className={cn(
                                        "w-[240px] justify-start text-left font-normal bg-gray-900 border-gray-700 hover:bg-gray-800 text-gray-50",
                                        !date && "text-gray-400",
                                    )}
                                >
                                    <CalendarIcon className="mr-2 h-4 w-4" />
                                    {date?.from ? (
                                        date.to ? (
                                            <>
                                                {format(date.from, "LLL dd, y")} - {format(date.to, "LLL dd, y")}
                                            </>
                                        ) : (
                                            format(date.from, "LLL dd, y")
                                        )
                                    ) : (
                                        <span>Pick a date</span>
                                    )}
                                </Button>
                            </PopoverTrigger>
                            <PopoverContent className="w-auto p-0" align="end">
                                <Calendar
                                    initialFocus
                                    mode="range"
                                    defaultMonth={date?.from}
                                    selected={date}
                                    onSelect={setDate}
                                    numberOfMonths={2}
                                />
                            </PopoverContent>
                        </Popover>
                        <Button size="sm" className="bg-gray-50 text-gray-900 hover:bg-gray-200">
                            <Download className="mr-2 h-4 w-4" />
                            Download
                        </Button>
                    </div>
                </div>

                {/* Tabs */}
                <Tabs defaultValue="overview" className="space-y-4">
                    <TabsList className="bg-gray-900 border-gray-800">
                        <TabsTrigger value="overview">Executive Overview</TabsTrigger>
                        <TabsTrigger value="health">Infrastructure Health</TabsTrigger>
                        <TabsTrigger value="ai-memory">AI Memory</TabsTrigger>
                        <TabsTrigger value="deployment">Deployment</TabsTrigger>
                        <TabsTrigger value="data-flow">Data Flow</TabsTrigger>
                        <TabsTrigger value="projects">Projects</TabsTrigger>
                    </TabsList>

                    <TabsContent value="overview" className="space-y-4">
                        {/* KPI Cards */}
                        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                            {kpis.map((kpi) => (
                                <Card key={kpi.title} className="bg-gray-900 border-gray-800">
                                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                        <CardTitle className="text-sm font-medium text-gray-300">
                                            {kpi.title}
                                        </CardTitle>
                                        <kpi.icon className="h-4 w-4 text-gray-400" />
                                    </CardHeader>
                                    <CardContent>
                                        <div className="text-2xl font-bold text-gray-50">{kpi.value}</div>
                                        <p className={`text-xs ${
                                            kpi.changeType === "increase"
                                                ? "text-emerald-500"
                                                : "text-red-500"
                                        }`}>
                                            {kpi.change}
                                        </p>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>

                        {/* Charts */}
                        <div className="grid gap-6 mt-6 grid-cols-1 lg:grid-cols-5">
                            <div className="lg:col-span-3">
                                <Card className="bg-gray-900 border-gray-800">
                                    <CardHeader>
                                        <CardTitle className="text-gray-50">Sales Revenue</CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <SalesRevenueChart salesData={dashboardData.sales_revenue} />
                                    </CardContent>
                                </Card>
                            </div>
                            <div className="lg:col-span-2">
                                <Card className="bg-gray-900 border-gray-800">
                                    <CardHeader>
                                        <CardTitle className="text-gray-50">Deal Distribution</CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <DealStageDistribution dealData={dashboardData.deal_stages} />
                                    </CardContent>
                                </Card>
                            </div>
                        </div>

                        {/* Activity Feed */}
                        <Card className="bg-gray-900 border-gray-800">
                            <CardHeader>
                                <CardTitle className="text-gray-50">Recent Activity</CardTitle>
                                <p className="text-sm text-gray-400">
                                    Real-time updates from your business systems
                                </p>
                            </CardHeader>
                            <CardContent>
                                <ActivityFeed activities={dashboardData.activity_feed} />
                            </CardContent>
                        </Card>
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

            {/* Enhanced Chat Interface */}
            <div className="fixed bottom-4 right-4 z-50">
                <EnhancedUnifiedChat />
            </div>
        </div>
    );
}

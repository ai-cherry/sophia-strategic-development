import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle, Button, Input, Tabs, TabsContent, TabsList, TabsTrigger, Badge, Alert, AlertDescription, Progress, Avatar, AvatarFallback, Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui';
import { MessageCircle, Search, TrendingUp, AlertTriangle, Users, Target, Calendar, DollarSign, Activity, BarChart3, PieChart, LineChart, Send, Loader2, RefreshCw, Settings, Bell, Download, Share2, Maximize2, BrainCircuit, Database, GitBranch, Briefcase } from 'lucide-react';
import { Line, Bar, Pie, Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Title, Tooltip, Legend, Filler } from 'chart.js';
import apiClient from '../../services/apiClient';
import EnhancedUnifiedChat from '../shared/EnhancedUnifiedChat';

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
    // --- State Management ---
    const [activeTab, setActiveTab] = useState('unified_overview');
    const [isLoading, setIsLoading] = useState(false);
    const [lastRefresh, setLastRefresh] = useState(new Date());
    const [data, setData] = useState({
        ceo: null,
        projects: [],
        knowledge: null,
        sales: null,
        llm: null,
    });

    // --- Data Fetching ---
    const fetchDataForTab = async (tab) => {
        setIsLoading(true);
        try {
            let response;
            switch (tab) {
                case 'unified_overview':
                    response = await apiClient.get('/api/v1/unified/dashboard/summary');
                    setData(prev => ({ ...prev, ceo: response.data }));
                    break;
                case 'projects':
                     response = await apiClient.get('/api/v1/projects'); // Mocked for now
                     setData(prev => ({ ...prev, projects: response.data.projects }));
                    break;
                case 'knowledge':
                     response = await apiClient.get('/api/v1/knowledge/stats'); // Mocked
                     setData(prev => ({ ...prev, knowledge: response.data }));
                    break;
                 case 'sales':
                     response = await apiClient.get('/api/v1/sales/summary'); // Mocked
                     setData(prev => ({ ...prev, sales: response.data }));
                    break;
                case 'llm_metrics':
                    response = await apiClient.get('/api/v1/llm/stats');
                    setData(prev => ({ ...prev, llm: response.data }));
                    break;
            }
        } catch (error) {
            console.error(`Failed to fetch data for tab ${tab}:`, error);
        }
        setIsLoading(false);
    };

    useEffect(() => {
        fetchDataForTab(activeTab);
    }, [activeTab]);

    const handleRefresh = () => {
        setLastRefresh(new Date());
        fetchDataForTab(activeTab);
    };

    // --- Render Functions for Tabs ---

    const renderUnifiedOverview = () => (
        <div className="space-y-6">
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                <UnifiedKPICard title="Project Health" value={`${data.ceo?.project_health || 72}%`} change="+2%" changeType="increase" icon={Target} />
                <UnifiedKPICard title="Budget Usage" value={`${data.ceo?.budget_usage || 50}%`} change="-5%" changeType="decrease" icon={DollarSign} />
                <UnifiedKPICard title="Team Utilization" value={`${data.ceo?.team_utilization || 85}%`} change="+3%" changeType="increase" icon={Users} />
                <UnifiedKPICard title="On-Time Delivery" value={`${data.ceo?.on_time_delivery || 67}%`} change="-1%" changeType="decrease" icon={Calendar} />
            </div>
            {/* Add more Unified-specific charts and components here */}
        </div>
    );

    const renderProjects = () => (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                    <Briefcase />
                    <span>Cross-Platform Project & OKR Hub</span>
                </CardTitle>
            </CardHeader>
            <CardContent>
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Project</TableHead>
                            <TableHead>Platform</TableHead>
                            <TableHead>Health</TableHead>
                            <TableHead>Progress</TableHead>
                            <TableHead>Team</TableHead>
                            <TableHead>OKR Alignment</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {data.projects && data.projects.map(p => (
                            <TableRow key={p.id}>
                                <TableCell className="font-medium">{p.name}</TableCell>
                                <TableCell><Badge variant="outline" className="flex items-center w-min"><GitBranch className="h-3 w-3 mr-1" />{p.platform}</Badge></TableCell>
                                <TableCell className={p.health_score > 80 ? 'text-green-500' : p.health_score > 60 ? 'text-yellow-500' : 'text-red-500'}>{p.health_score}%</TableCell>
                                <TableCell><Progress value={p.completion_percentage} className="w-full" /></TableCell>
                                <TableCell>{p.team_members.join(', ')}</TableCell>
                                <TableCell><Badge>{p.okr_alignment}</Badge></TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </CardContent>
        </Card>
    );

    const renderKnowledge = () => (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
                <Card>
                    <CardHeader><CardTitle>Data Ingestion Status</CardTitle></CardHeader>
                    <CardContent>
                        {/* Placeholder for Ingestion Status Table */}
                        <p>Real-time ingestion job status will be displayed here.</p>
                    </CardContent>
                </Card>
                 <Card>
                    <CardHeader><CardTitle>AI Learning & Growth</CardTitle></CardHeader>
                    <CardContent>
                        {/* Placeholder for AI learning metrics */}
                        <p>Metrics on AI concept growth and accuracy will be shown here.</p>
                    </CardContent>
                </Card>
            </div>
            <div className="space-y-6">
                <Card>
                    <CardHeader><CardTitle>Data Sources</CardTitle></CardHeader>
                    <CardContent className="space-y-2">
                        <Button variant="outline" className="w-full justify-start">Sync Gong</Button>
                        <Button variant="outline" className="w-full justify-start">Sync HubSpot</Button>
                        <Button variant="outline" className="w-full justify-start">Sync Snowflake</Button>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader><CardTitle>Manual Upload</CardTitle></CardHeader>
                    <CardContent>
                        <Input type="file" />
                        <Button className="w-full mt-2">Upload and Ingest</Button>
                    </CardContent>
                </Card>
            </div>
        </div>
    );

    const renderSales = () => (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
             <UnifiedKPICard title="Pipeline Value" value={`$${(data.sales?.pipeline_value / 1000000).toFixed(1)}M`} change="+15%" changeType="increase" icon={DollarSign} />
             <UnifiedKPICard title="Active Deals" value={data.sales?.active_deals || 0} change="+10" changeType="increase" icon={Briefcase} />
             <UnifiedKPICard title="Win Rate" value={`${data.sales?.win_rate || 0}%`} change="+2%" changeType="increase" icon={TrendingUp} />
             <UnifiedKPICard title="Calls Analyzed" value={data.sales?.calls_analyzed || 0} icon={Activity} />
        </div>
    );

    const renderLLMMetrics = () => (
        <div className="space-y-6">
            {/* Cost Alerts Section */}
            {data.llm?.alerts && data.llm.alerts.length > 0 && (
                <div className="space-y-4">
                    {data.llm.alerts.map((alert, index) => (
                        <Alert key={index} variant={alert.severity === 'critical' ? 'destructive' : 'default'}>
                            <AlertTriangle className="h-4 w-4" />
                            <AlertDescription>
                                <div className="flex items-center justify-between">
                                    <div>
                                        <strong>{alert.title}</strong>
                                        <p className="text-sm mt-1">{alert.message}</p>
                                    </div>
                                    <div className="text-right">
                                        <Badge variant={alert.severity === 'critical' ? 'destructive' : 'secondary'}>
                                            {alert.severity}
                                        </Badge>
                                        <p className="text-xs text-gray-500 mt-1">{alert.timestamp}</p>
                                    </div>
                                </div>
                            </AlertDescription>
                        </Alert>
                    ))}
                </div>
            )}

            {/* Budget Status Card */}
            <Card className={data.llm?.budget_status?.is_over_budget ? 'border-red-500' : ''}>
                <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                        <span className="flex items-center space-x-2">
                            <DollarSign />
                            <span>Budget Status</span>
                        </span>
                        {data.llm?.budget_status?.is_over_budget && (
                            <Badge variant="destructive">Over Budget</Badge>
                        )}
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid gap-4 md:grid-cols-3">
                        <div>
                            <p className="text-sm text-gray-500">Daily Budget</p>
                            <p className="text-xl font-bold">${data.llm?.budget_status?.daily_budget || 100}</p>
                            <Progress 
                                value={(data.llm?.daily_cost / data.llm?.budget_status?.daily_budget) * 100 || 0} 
                                className={`mt-2 ${(data.llm?.daily_cost / data.llm?.budget_status?.daily_budget) > 0.8 ? 'bg-red-100' : ''}`}
                            />
                            <p className="text-xs text-gray-500 mt-1">
                                ${data.llm?.daily_cost || 0} / ${data.llm?.budget_status?.daily_budget || 100} used
                            </p>
                        </div>
                        <div>
                            <p className="text-sm text-gray-500">Monthly Budget</p>
                            <p className="text-xl font-bold">${data.llm?.budget_status?.monthly_budget || 3000}</p>
                            <Progress 
                                value={(data.llm?.monthly_cost / data.llm?.budget_status?.monthly_budget) * 100 || 0} 
                                className={`mt-2 ${(data.llm?.monthly_cost / data.llm?.budget_status?.monthly_budget) > 0.8 ? 'bg-red-100' : ''}`}
                            />
                            <p className="text-xs text-gray-500 mt-1">
                                ${data.llm?.monthly_cost || 0} / ${data.llm?.budget_status?.monthly_budget || 3000} used
                            </p>
                        </div>
                        <div>
                            <p className="text-sm text-gray-500">Projected Monthly</p>
                            <p className="text-xl font-bold ${data.llm?.budget_status?.projected_monthly > data.llm?.budget_status?.monthly_budget ? 'text-red-600' : ''}">
                                ${data.llm?.budget_status?.projected_monthly || 0}
                            </p>
                            <p className="text-xs text-gray-500 mt-1">
                                Based on current usage rate
                            </p>
                            {data.llm?.budget_status?.projected_monthly > data.llm?.budget_status?.monthly_budget && (
                                <p className="text-xs text-red-600 mt-1">
                                    ⚠️ Exceeds budget by ${(data.llm?.budget_status?.projected_monthly - data.llm?.budget_status?.monthly_budget).toFixed(2)}
                                </p>
                            )}
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* LLM Cost Overview */}
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                <UnifiedKPICard
                    title="Total LLM Cost (Today)"
                    value={`$${data.llm?.daily_cost || 0}`}
                    change={`${data.llm?.cost_change || 0}%`}
                    changeType={data.llm?.cost_change > 0 ? 'increase' : 'decrease'}
                    icon={DollarSign}
                />
                <UnifiedKPICard
                    title="Requests (24h)"
                    value={data.llm?.daily_requests || 0}
                    change={`${data.llm?.request_change || 0}%`}
                    changeType="increase"
                    icon={Activity}
                />
                <UnifiedKPICard
                    title="Avg Response Time"
                    value={`${data.llm?.avg_response_time || 0}ms`}
                    change={`${data.llm?.response_time_change || 0}%`}
                    changeType={data.llm?.response_time_change < 0 ? 'increase' : 'decrease'}
                    icon={Activity}
                />
                <UnifiedKPICard
                    title="Cache Hit Rate"
                    value={`${data.llm?.cache_hit_rate || 0}%`}
                    change={`+${data.llm?.cache_improvement || 0}%`}
                    changeType="increase"
                    icon={Database}
                />
            </div>

            {/* Provider Breakdown */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                        <BrainCircuit />
                        <span>LLM Provider Usage</span>
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Provider</TableHead>
                                <TableHead>Model</TableHead>
                                <TableHead>Requests</TableHead>
                                <TableHead>Cost</TableHead>
                                <TableHead>Avg Latency</TableHead>
                                <TableHead>Task Type</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {data.llm?.providers && data.llm.providers.map(p => (
                                <TableRow key={`${p.provider}-${p.model}`}>
                                    <TableCell>
                                        <Badge variant={p.provider === 'snowflake' ? 'default' : 'secondary'}>
                                            {p.provider}
                                        </Badge>
                                    </TableCell>
                                    <TableCell className="font-medium">{p.model}</TableCell>
                                    <TableCell>{p.requests.toLocaleString()}</TableCell>
                                    <TableCell>${p.cost.toFixed(3)}</TableCell>
                                    <TableCell>{p.avg_latency}ms</TableCell>
                                    <TableCell>
                                        <Badge variant="outline">{p.primary_task_type}</Badge>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>

            {/* Cost by Task Type */}
            <div className="grid gap-6 md:grid-cols-2">
                <Card>
                    <CardHeader>
                        <CardTitle>Cost by Task Type</CardTitle>
                    </CardHeader>
                    <CardContent>
                        {data.llm?.task_costs && (
                            <Doughnut
                                data={{
                                    labels: Object.keys(data.llm.task_costs),
                                    datasets: [{
                                        data: Object.values(data.llm.task_costs),
                                        backgroundColor: [
                                            '#3B82F6', '#10B981', '#F59E0B',
                                            '#EF4444', '#8B5CF6', '#EC4899'
                                        ]
                                    }]
                                }}
                                options={{
                                    responsive: true,
                                    plugins: {
                                        legend: { position: 'right' }
                                    }
                                }}
                            />
                        )}
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Request Volume Trend (7 Days)</CardTitle>
                    </CardHeader>
                    <CardContent>
                        {data.llm?.request_trend && (
                            <Line
                                data={{
                                    labels: data.llm.request_trend.labels,
                                    datasets: [{
                                        label: 'Requests',
                                        data: data.llm.request_trend.values,
                                        borderColor: '#3B82F6',
                                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                                        tension: 0.4
                                    }]
                                }}
                                options={{
                                    responsive: true,
                                    plugins: {
                                        legend: { display: false }
                                    },
                                    scales: {
                                        y: { beginAtZero: true }
                                    }
                                }}
                            />
                        )}
                    </CardContent>
                </Card>
            </div>

            {/* Snowflake Data Locality Savings */}
            <Card>
                <CardHeader>
                    <CardTitle>Snowflake Data Locality Savings</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid gap-4 md:grid-cols-3">
                        <div className="text-center">
                            <p className="text-2xl font-bold text-green-600">
                                ${data.llm?.snowflake_savings || 0}
                            </p>
                            <p className="text-sm text-gray-500">Cost Saved (Month)</p>
                        </div>
                        <div className="text-center">
                            <p className="text-2xl font-bold text-blue-600">
                                {data.llm?.data_movement_avoided || 0} GB
                            </p>
                            <p className="text-sm text-gray-500">Data Movement Avoided</p>
                        </div>
                        <div className="text-center">
                            <p className="text-2xl font-bold text-purple-600">
                                {data.llm?.snowflake_percentage || 0}%
                            </p>
                            <p className="text-sm text-gray-500">Queries Handled by Snowflake</p>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );

    // --- Main Component Return ---
    return (
        <div className="min-h-screen bg-gray-50 p-4 sm:p-6 lg:p-8">
            <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
                <div>
                    <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Unified Intelligence Dashboard</h1>
                    <p className="text-sm text-gray-500 mt-1">
                      The single source of truth for Sophia AI. Last updated: {lastRefresh.toLocaleTimeString()}
                    </p>
                </div>
                <div className="flex items-center space-x-2">
                    <Button onClick={handleRefresh} disabled={isLoading} variant="outline" size="sm">
                        <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                        Refresh
                    </Button>
                    <Button variant="outline" size="sm"><Settings className="h-4 w-4" /></Button>
                </div>
            </div>

            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                <TabsList className="grid w-full grid-cols-2 sm:grid-cols-3 md:grid-cols-5">
                    <TabsTrigger value="unified_overview">Unified Overview</TabsTrigger>
                    <TabsTrigger value="projects">Projects & OKRs</TabsTrigger>
                    <TabsTrigger value="knowledge">Knowledge AI</TabsTrigger>
                    <TabsTrigger value="sales">Sales Intelligence</TabsTrigger>
                    <TabsTrigger value="llm_metrics">LLM Metrics</TabsTrigger>
                    <TabsTrigger value="unified_chat">Unified Chat</TabsTrigger>
                </TabsList>

                <TabsContent value="unified_overview" className="mt-6">{renderUnifiedOverview()}</TabsContent>
                <TabsContent value="projects" className="mt-6">{renderProjects()}</TabsContent>
                <TabsContent value="knowledge" className="mt-6">{renderKnowledge()}</TabsContent>
                <TabsContent value="sales" className="mt-6">{renderSales()}</TabsContent>
                <TabsContent value="llm_metrics" className="mt-6">{renderLLMMetrics()}</TabsContent>
                <TabsContent value="unified_chat" className="mt-6">
                    <EnhancedUnifiedChat initialContext={activeTab} />
                </TabsContent>
            </Tabs>
        </div>
    );
};

export default UnifiedDashboard;

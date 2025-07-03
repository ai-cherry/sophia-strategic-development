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
                    <TabsTrigger value="unified_chat">Unified Chat</TabsTrigger>
                </TabsList>

                <TabsContent value="unified_overview" className="mt-6">{renderUnifiedOverview()}</TabsContent>
                <TabsContent value="projects" className="mt-6">{renderProjects()}</TabsContent>
                <TabsContent value="knowledge" className="mt-6">{renderKnowledge()}</TabsContent>
                <TabsContent value="sales" className="mt-6">{renderSales()}</TabsContent>
                <TabsContent value="unified_chat" className="mt-6">
                    <EnhancedUnifiedChat initialContext={activeTab} />
                </TabsContent>
            </Tabs>
        </div>
    );
};

export default UnifiedDashboard; 
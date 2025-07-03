import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle, Button, Input, Tabs, TabsContent, TabsList, TabsTrigger, Badge, Alert, AlertDescription, Progress, Avatar, AvatarFallback } from '@/components/ui';
import { MessageCircle, Search, TrendingUp, AlertTriangle, Users, Target, Calendar, DollarSign, Activity, BarChart3, PieChart, LineChart, Send, Loader2, RefreshCw, Settings, Bell, Download, Share2, Maximize2 } from 'lucide-react';
import { Line, Bar, Pie, Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Title, Tooltip, Legend, Filler } from 'chart.js';
import apiClient from '../../services/apiClient';
import EnhancedUnifiedChat from '../shared/EnhancedUnifiedChat';

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Title, Tooltip, Legend, Filler);

// --- Reusable Components ---
const UnifiedKPICard = ({ title, value, change, changeType, icon: Icon, target }) => (
    <Card className="hover:shadow-lg transition-all duration-300">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">{title}</CardTitle>
            <Icon className="h-4 w-4 text-gray-400" />
        </CardHeader>
        <CardContent>
            <div className="text-2xl font-bold text-gray-900">{value}</div>
            <p className={`text-xs ${changeType === 'increase' ? 'text-green-500' : 'text-red-500'}`}>{change} from last month</p>
        </CardContent>
    </Card>
);

const UnifiedDashboard = () => {
    // --- State Management ---
    const [activeTab, setActiveTab] = useState('ceo_overview');
    const [isLoading, setIsLoading] = useState(false);
    const [lastRefresh, setLastRefresh] = useState(new Date());

    // Data states for each tab
    const [ceoData, setCeoData] = useState(null);
    const [projectData, setProjectData] = useState(null);
    const [salesData, setSalesData] = useState(null);
    const [knowledgeData, setKnowledgeData] = useState(null);
    const [chatMessages, setChatMessages] = useState([]);
    const [chatInput, setChatInput] = useState('');

    const chatEndRef = useRef(null);

    // --- Data Fetching ---
    const fetchDataForTab = async (tab) => {
        setIsLoading(true);
        try {
            let response;
            switch (tab) {
                case 'ceo_overview':
                    response = await apiClient.get('/api/v1/ceo/dashboard/summary');
                    setCeoData(response.data);
                    break;
                // Add cases for other tabs here
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
    
    // --- Chat Logic ---
    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [chatMessages]);

    const handleChatSend = async () => {
        if (!chatInput.trim()) return;
        const userMessage = { type: 'user', content: chatInput, timestamp: new Date().toISOString() };
        setChatMessages(prev => [...prev, userMessage]);
        setIsLoading(true);
        
        try {
            const res = await apiClient.post('/api/v1/ceo/chat', { message: chatInput });
            const assistantMessage = { type: 'assistant', ...res.data };
            setChatMessages(prev => [...prev, assistantMessage]);
        } catch (error) {
            const errorMessage = { type: 'assistant', content: 'Sorry, I encountered an error.', timestamp: new Date().toISOString() };
            setChatMessages(prev => [...prev, errorMessage]);
        }
        
        setChatInput('');
        setIsLoading(false);
    };

    // --- Render Functions for Tabs ---

    const renderCEOOverview = () => (
        <div className="space-y-6">
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                <UnifiedKPICard title="Total Revenue" value={ceoData?.total_revenue || '$0'} change="+5.2%" changeType="increase" icon={DollarSign} />
                <UnifiedKPICard title="Active Deals" value={ceoData?.active_deals || '0'} change="+12" changeType="increase" icon={Activity} />
                <UnifiedKPICard title="Team Performance" value={`${ceoData?.team_performance || '0'}%`} change="-1.2%" changeType="decrease" icon={Users} />
                <UnifiedKPICard title="Customer Satisfaction" value={`${ceoData?.customer_satisfaction || '0'}/5`} change="+0.1" changeType="increase" icon={TrendingUp} />
            </div>
            {/* Add charts and other components here */}
        </div>
    );
    
    const renderChat = () => (
        <EnhancedUnifiedChat initialContext="business_intelligence" />
    );

    // --- Main Component Return ---
    return (
        <div className="min-h-screen bg-gray-50 p-4 sm:p-6 lg:p-8">
            <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
                <div>
                    <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Unified Intelligence Dashboard</h1>
                    <p className="text-sm text-gray-500 mt-1">
                      Last updated: {lastRefresh.toLocaleTimeString()}
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
                    <TabsTrigger value="ceo_overview">CEO Overview</TabsTrigger>
                    <TabsTrigger value="projects">Projects & OKRs</TabsTrigger>
                    <TabsTrigger value="knowledge">Knowledge AI</TabsTrigger>
                    <TabsTrigger value="sales">Sales Intelligence</TabsTrigger>
                    <TabsTrigger value="chat">AI Chat</TabsTrigger>
                </TabsList>

                <TabsContent value="ceo_overview" className="mt-6">{renderCEOOverview()}</TabsContent>
                <TabsContent value="projects" className="mt-6"><p className="text-center py-16 text-gray-500">Project management data coming soon...</p></TabsContent>
                <TabsContent value="knowledge" className="mt-6"><p className="text-center py-16 text-gray-500">Knowledge AI interface coming soon...</p></TabsContent>
                <TabsContent value="sales" className="mt-6"><p className="text-center py-16 text-gray-500">Sales intelligence coming soon...</p></TabsContent>
                <TabsContent value="chat" className="mt-6">{renderChat()}</TabsContent>
            </Tabs>
        </div>
    );
};

export default UnifiedDashboard; 
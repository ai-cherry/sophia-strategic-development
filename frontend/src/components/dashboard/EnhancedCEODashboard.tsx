import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  DollarSign, 
  Users, 
  Activity, 
  Target, 
  Briefcase,
  AlertTriangle,
  CheckCircle2,
  BarChart3,
  PieChart,
  LineChart
} from 'lucide-react';
import { Button } from '../ui/button';
import { Alert, AlertDescription } from '../ui/alert';
import { Progress } from '../ui/progress';
import EnhancedUnifiedChatInterface from '../shared/EnhancedUnifiedChatInterface';
import {
  BarChart,
  Bar,
  Line,
  LineChart as RechartsLineChart,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart
} from 'recharts';

// KPI Card Component
interface KPICardProps {
  title: string;
  value: string;
  change: string;
  changeType: 'increase' | 'decrease' | 'neutral';
  icon: React.ElementType;
  prefix?: string;
  suffix?: string;
}

const KPICard: React.FC<KPICardProps> = ({ 
  title, 
  value, 
  change, 
  changeType, 
  icon: Icon,
  prefix = '',
  suffix = ''
}) => {
  const trendColor = 
    changeType === 'increase' ? 'text-green-600' : 
    changeType === 'decrease' ? 'text-red-600' : 
    'text-gray-600';
  
  const TrendIcon = 
    changeType === 'increase' ? TrendingUp : 
    changeType === 'decrease' ? TrendingDown : 
    Minus;

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-gray-600">{title}</CardTitle>
        <Icon className="h-4 w-4 text-gray-400" />
      </CardHeader>
      <CardContent className="">
        <div className="text-2xl font-bold text-gray-900">
          {prefix}{value}{suffix}
        </div>
        <p className="text-xs text-gray-500 flex items-center mt-1">
          <TrendIcon className={`h-3 w-3 mr-1 ${trendColor}`} />
          <span className={trendColor}>{change}</span>
        </p>
      </CardContent>
    </Card>
  );
};

// Main Dashboard Component
export const EnhancedCEODashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [selectedTimeRange, setSelectedTimeRange] = useState('30d');
  const [refreshInterval, setRefreshInterval] = useState(300000); // 5 minutes

  // Chat context for CEO dashboard
  const chatContext = {
    dashboardType: 'ceo' as const,
    userId: 'ceo-user', // This should come from auth context
    tenantId: 'payready',
    activeFilters: { timeRange: selectedTimeRange }
  };

  // Load dashboard data
  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, refreshInterval);
    return () => clearInterval(interval);
  }, [selectedTimeRange, refreshInterval]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/v1/dashboard/ceo?timeRange=${selectedTimeRange}`);
      if (!response.ok) throw new Error('Failed to fetch dashboard data');
      const data = await response.json();
      setDashboardData(data);
      setError(null);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Mock data (replace with real data from API)
  const kpiData = [
    { 
      title: 'Monthly Recurring Revenue', 
      value: '$2.4M', 
      change: '+5.2%', 
      changeType: 'increase' as const, 
      icon: DollarSign,
      prefix: ''
    },
    { 
      title: 'Customer Acquisition', 
      value: '156', 
      change: '+12 from last month', 
      changeType: 'increase' as const, 
      icon: Users 
    },
    { 
      title: 'Net Revenue Retention', 
      value: '112%', 
      change: '+2.5%', 
      changeType: 'increase' as const, 
      icon: Target,
      suffix: ''
    },
    { 
      title: 'Sales Pipeline', 
      value: '$8.3M', 
      change: '+18%', 
      changeType: 'increase' as const, 
      icon: Briefcase,
      prefix: ''
    },
  ];

  const revenueData = [
    { month: 'Jan', revenue: 1800000, target: 1700000 },
    { month: 'Feb', revenue: 1950000, target: 1850000 },
    { month: 'Mar', revenue: 2100000, target: 2000000 },
    { month: 'Apr', revenue: 2250000, target: 2150000 },
    { month: 'May', revenue: 2400000, target: 2300000 },
    { month: 'Jun', revenue: 2550000, target: 2450000 }
  ];

  const competitorData = [
    { name: 'EliseAI', marketShare: 28, growth: 15 },
    { name: 'Pay Ready', marketShare: 22, growth: 25 },
    { name: 'Hunter Warfield', marketShare: 18, growth: 8 },
    { name: 'Others', marketShare: 32, growth: 10 }
  ];

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#6B7280'];

  const teamPerformanceData = [
    { team: 'Sales', efficiency: 94, target: 90 },
    { team: 'Engineering', efficiency: 88, target: 85 },
    { team: 'Customer Success', efficiency: 96, target: 95 },
    { team: 'Marketing', efficiency: 82, target: 80 },
    { team: 'Operations', efficiency: 91, target: 90 }
  ];

  const handleActionExecuted = (action: any, result: any) => {
    // Handle chat actions
    console.log('Action executed:', action, result);
    // Refresh relevant data based on action
    if (action.type === 'refresh_data') {
      fetchDashboardData();
    }
  };

  if (loading && !dashboardData) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <Activity className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading executive dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Executive Command Center</h1>
          <p className="text-gray-600 mt-1">Real-time business intelligence and strategic insights</p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setSelectedTimeRange('7d')}
            className={selectedTimeRange === '7d' ? 'bg-gray-100' : ''}
          >
            7 Days
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setSelectedTimeRange('30d')}
            className={selectedTimeRange === '30d' ? 'bg-gray-100' : ''}
          >
            30 Days
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setSelectedTimeRange('90d')}
            className={selectedTimeRange === '90d' ? 'bg-gray-100' : ''}
          >
            90 Days
          </Button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {kpiData.map((kpi: any, index: number) => (
          <KPICard key={index} {...kpi} />
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left Column - 2/3 width */}
        <div className="lg:col-span-2 space-y-6">
          {/* Revenue Trends */}
          <Card className="">
            <CardHeader className="">
              <CardTitle className="flex items-center gap-2">
                <LineChart className="h-5 w-5" />
                Revenue Trends
              </CardTitle>
            </CardHeader>
            <CardContent className="">
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={revenueData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis tickFormatter={(value) => `$${(value / 1000000).toFixed(1)}M`} />
                  <Tooltip formatter={(value: any) => `$${(value / 1000000).toFixed(2)}M`} />
                  <Legend />
                  <Area 
                    type="monotone" 
                    dataKey="revenue" 
                    stroke="#3B82F6" 
                    fill="#3B82F6" 
                    fillOpacity={0.2} 
                    strokeWidth={2}
                    name="Actual Revenue"
                  />
                  <Area 
                    type="monotone" 
                    dataKey="target" 
                    stroke="#10B981" 
                    fill="#10B981" 
                    fillOpacity={0.1} 
                    strokeWidth={2}
                    strokeDasharray="5 5"
                    name="Target"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Team Performance */}
          <Card className="">
            <CardHeader className="">
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Team Performance
              </CardTitle>
            </CardHeader>
            <CardContent className="">
              <div className="space-y-4">
                {teamPerformanceData.map((team: any, index: number) => (
                  <div key={index} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">{team.team}</span>
                      <span className="text-sm text-gray-600">{team.efficiency}%</span>
                    </div>
                    <div className="relative">
                      <Progress className="" value={team.efficiency} className="h-2" />
                      <div 
                        className="absolute top-0 h-2 w-1 bg-gray-400"
                        style={{ left: `${team.target}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column - 1/3 width */}
        <div className="space-y-6">
          {/* Competitive Analysis */}
          <Card className="">
            <CardHeader className="">
              <CardTitle className="flex items-center gap-2">
                <PieChart className="h-5 w-5" />
                Market Share Analysis
              </CardTitle>
            </CardHeader>
            <CardContent className="">
              <ResponsiveContainer width="100%" height={250}>
                <RechartsPieChart>
                  <Pie
                    data={competitorData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, marketShare }) => `${name}: ${marketShare}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="marketShare"
                  >
                    {competitorData.map((competitor: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </RechartsPieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Strategic Alerts */}
          <Card className="">
            <CardHeader className="">
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5" />
                Strategic Alerts
              </CardTitle>
            </CardHeader>
            <CardContent className="">
              <div className="space-y-3">
                <Alert>
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                  <AlertDescription>
                    Q2 revenue target exceeded by 12%
                  </AlertDescription>
                </Alert>
                <Alert>
                  <AlertTriangle className="h-4 w-4 text-yellow-600" />
                  <AlertDescription>
                    EliseAI launched new competitive feature
                  </AlertDescription>
                </Alert>
                <Alert>
                  <TrendingUp className="h-4 w-4 text-blue-600" />
                  <AlertDescription>
                    NMHC conference opportunity identified
                  </AlertDescription>
                </Alert>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Chat Interface */}
      <div className="mt-6">
        <EnhancedUnifiedChatInterface
          context={chatContext}
          height="400px"
          title="Executive AI Assistant"
          onActionExecuted={handleActionExecuted}
        />
      </div>
    </div>
  );
};

export default EnhancedCEODashboard;

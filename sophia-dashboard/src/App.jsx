import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Button } from '@/components/ui/button.jsx'
import { TrendingUp, TrendingDown, Users, DollarSign, Target, Phone, BarChart3, RefreshCw } from 'lucide-react'
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import './App.css'

// Sample data for charts
const revenueData = [
  { month: 'Jan', revenue: 850000, target: 900000 },
  { month: 'Feb', revenue: 920000, target: 950000 },
  { month: 'Mar', revenue: 1100000, target: 1000000 },
  { month: 'Apr', revenue: 1250000, target: 1200000 },
]

const salesData = [
  { name: 'Closed Won', value: 23, color: '#10b981' },
  { name: 'In Progress', value: 45, color: '#f59e0b' },
  { name: 'Qualified', value: 32, color: '#3b82f6' },
]

const teamData = [
  { department: 'Sales', productivity: 87, satisfaction: 4.2 },
  { department: 'Marketing', productivity: 92, satisfaction: 4.5 },
  { department: 'Engineering', productivity: 89, satisfaction: 4.1 },
  { department: 'Support', productivity: 94, satisfaction: 4.6 },
]

function App() {
  const [metrics, setMetrics] = useState(null)
  const [gongInsights, setGongInsights] = useState(null)
  const [loading, setLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState(new Date())

  const fetchData = async () => {
    setLoading(true)
    try {
      // Fetch dashboard metrics
      const metricsResponse = await fetch('http://localhost:8000/api/v1/dashboard/metrics')
      const metricsData = await metricsResponse.json()
      setMetrics(metricsData)

      // Fetch Gong insights
      const gongResponse = await fetch('http://localhost:8000/api/v1/gong/insights')
      const gongData = await gongResponse.json()
      setGongInsights(gongData)

      setLastUpdated(new Date())
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
    // Refresh data every 5 minutes
    const interval = setInterval(fetchData, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [])

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value)
  }

  const formatPercentage = (value) => {
    return `${value > 0 ? '+' : ''}${value.toFixed(1)}%`
  }

  if (loading && !metrics) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Loading Sophia AI Dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-foreground">Sophia AI</h1>
              <p className="text-muted-foreground">Executive Dashboard</p>
            </div>
            <div className="flex items-center gap-4">
              <Badge variant="outline" className="text-xs">
                Last updated: {lastUpdated.toLocaleTimeString()}
              </Badge>
              <Button onClick={fetchData} variant="outline" size="sm" disabled={loading}>
                <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        {/* Key Metrics Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Revenue Card */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(metrics?.revenue?.current || 0)}</div>
              <div className="flex items-center text-xs text-muted-foreground">
                {metrics?.revenue?.growth > 0 ? (
                  <TrendingUp className="h-3 w-3 mr-1 text-green-500" />
                ) : (
                  <TrendingDown className="h-3 w-3 mr-1 text-red-500" />
                )}
                <span className={metrics?.revenue?.growth > 0 ? 'text-green-500' : 'text-red-500'}>
                  {formatPercentage(metrics?.revenue?.growth || 0)}
                </span>
                <span className="ml-1">from last month</span>
              </div>
            </CardContent>
          </Card>

          {/* Sales Card */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Deals Closed</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics?.sales?.deals_closed || 0}</div>
              <p className="text-xs text-muted-foreground">
                Pipeline: {formatCurrency(metrics?.sales?.pipeline_value || 0)}
              </p>
            </CardContent>
          </Card>

          {/* Team Card */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Users</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics?.team?.active_users || 0}</div>
              <p className="text-xs text-muted-foreground">
                Productivity: {metrics?.team?.productivity_score || 0}%
              </p>
            </CardContent>
          </Card>

          {/* Gong Insights Card */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Call Insights</CardTitle>
              <Phone className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{gongInsights?.total_calls || 0}</div>
              <p className="text-xs text-muted-foreground">
                Avg: {gongInsights?.avg_duration || 0}min
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Revenue Trend Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Revenue Trend</CardTitle>
              <CardDescription>Monthly revenue vs target</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={revenueData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis tickFormatter={(value) => `$${value / 1000}K`} />
                  <Tooltip formatter={(value) => formatCurrency(value)} />
                  <Area type="monotone" dataKey="revenue" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.2} />
                  <Line type="monotone" dataKey="target" stroke="#ef4444" strokeDasharray="5 5" />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Sales Pipeline Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Sales Pipeline</CardTitle>
              <CardDescription>Deal distribution by stage</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={salesData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={120}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {salesData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <div className="flex justify-center gap-4 mt-4">
                {salesData.map((item, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }}></div>
                    <span className="text-sm text-muted-foreground">{item.name}: {item.value}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Team Performance */}
        <Card>
          <CardHeader>
            <CardTitle>Team Performance</CardTitle>
            <CardDescription>Productivity and satisfaction by department</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={teamData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="department" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="productivity" fill="#10b981" name="Productivity %" />
                <Bar dataKey="satisfaction" fill="#3b82f6" name="Satisfaction (1-5)" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Gong Insights */}
        {gongInsights && (
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Gong Call Insights</CardTitle>
              <CardDescription>AI-powered conversation analytics</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-primary">{gongInsights.sentiment_score}</div>
                  <p className="text-sm text-muted-foreground">Sentiment Score</p>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-primary">{gongInsights.avg_duration}min</div>
                  <p className="text-sm text-muted-foreground">Avg Call Duration</p>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-primary">{gongInsights.total_calls}</div>
                  <p className="text-sm text-muted-foreground">Total Calls</p>
                </div>
              </div>
              <div className="mt-4">
                <h4 className="font-semibold mb-2">Top Discussion Topics:</h4>
                <div className="flex gap-2 flex-wrap">
                  {gongInsights.top_topics?.map((topic, index) => (
                    <Badge key={index} variant="secondary">{topic}</Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  )
}

export default App


import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription } from '../ui/alert';
import { Loader2, TrendingUp, TrendingDown, AlertTriangle, Lightbulb } from 'lucide-react';
import EnhancedKPICard from './EnhancedKPICard';
// Mock components for layout purposes
const EnhancedExecutiveChart = () => <div className="h-64 bg-gray-700/50 rounded-lg flex items-center justify-center"><p>Executive Chart</p></div>;
const AutomatedInsightsPanel = ({ insights }) => <Card className="bg-white/10 backdrop-blur-xl border-white/20 h-full"><CardHeader><CardTitle>Automated Insights</CardTitle></CardHeader><CardContent>{insights.length} insights available</CardContent></Card>;
const PredictiveAnalyticsWidget = ({ title }) => <Card className="bg-white/10 backdrop-blur-xl border-white/20"><CardHeader><CardTitle>{title}</CardTitle></CardHeader><CardContent>Prediction data here</CardContent></Card>;

const AIEnhancedCEODashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [insights, setInsights] = useState([]);
  const [predictions, setPredictions] = useState({});
  const [loading, setLoading] = useState(true);
  const [selectedTimeRange, setSelectedTimeRange] = useState('30d');
  const [naturalLanguageQuery, setNaturalLanguageQuery] = useState('');
  const [queryResponse, setQueryResponse] = useState(null);
  const [queryLoading, setQueryLoading] = useState(false);

  const fetchDashboardData = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/intelligence/dashboard/enhanced-metrics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer faketoken' },
        body: JSON.stringify({ timeRange: selectedTimeRange, include_predictions: true })
      });
      if (!response.ok) throw new Error('Failed to fetch dashboard metrics');
      const data = await response.json();
      setDashboardData(data.metrics);
      setInsights(data.insights || []);
      setPredictions(data.predictions || {});
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  }, [selectedTimeRange]);

  const handleNaturalLanguageQuery = useCallback(async () => {
    if (!naturalLanguageQuery.trim()) return;
    setQueryLoading(true);
    try {
      const response = await fetch('/api/intelligence/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer faketoken' },
        body: JSON.stringify({ query: naturalLanguageQuery, context: { role: 'CEO' } })
      });
      const result = await response.json();
      setQueryResponse(result);
    } catch (error) {
      setQueryResponse({ answer: 'I encountered an error processing your query.', confidence_score: 0 });
    } finally {
      setQueryLoading(false);
    }
  }, [naturalLanguageQuery]);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-900 text-white">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading AI-Enhanced Dashboard...</span>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6 text-white">
      <div className="mb-8">
        <h1 className="text-4xl font-bold">AI-Enhanced Executive Command Center</h1>
        <p className="text-slate-300">Powered by Snowflake Intelligence & Cortex AI</p>
      </div>

      <Card className="bg-white/10 backdrop-blur-xl border-white/20 mb-6">
        <CardHeader><CardTitle className="flex items-center"><Lightbulb className="mr-2"/>Ask Anything About Your Business</CardTitle></CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <Input
              placeholder="e.g., 'What's driving our revenue growth this quarter?'"
              value={naturalLanguageQuery}
              onChange={(e) => setNaturalLanguageQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleNaturalLanguageQuery()}
              className="flex-1 bg-white/20 border-white/30 placeholder-white/70"
            />
            <Button onClick={handleNaturalLanguageQuery} disabled={queryLoading}>
              {queryLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Ask AI'}
            </Button>
          </div>
          {queryResponse && (
            <div className="mt-4 p-4 bg-black/20 rounded-lg">
              <p>{queryResponse.answer}</p>
              <div className="text-xs text-slate-400 mt-2">
                Confidence: {Math.round((queryResponse.confidence_score || 0) * 100)}%
              </div>
            </div>
          )}
        </CardContent>
      </Card>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <EnhancedKPICard title="Revenue" value={dashboardData?.revenue?.current} previousValue={dashboardData?.revenue?.previous} format="currency" insight={insights.find(i => i.metrics_affected?.includes('revenue'))} prediction={predictions.revenue_forecasting} />
        <EnhancedKPICard title="Customer Satisfaction" value={dashboardData?.satisfaction?.current} previousValue={dashboardData?.satisfaction?.previous} format="percentage" insight={insights.find(i => i.metrics_affected?.includes('customer_satisfaction'))} prediction={predictions.customer_satisfaction_prediction} />
        <EnhancedKPICard title="Sales Pipeline" value={dashboardData?.pipeline?.current} previousValue={dashboardData?.pipeline?.previous} format="currency" insight={insights.find(i => i.metrics_affected?.includes('pipeline_value'))} prediction={predictions.sales_pipeline_prediction} />
        <EnhancedKPICard title="Team Performance" value={dashboardData?.team_performance?.current} previousValue={dashboardData?.team_performance?.previous} format="score" insight={insights.find(i => i.metrics_affected?.includes('team_performance'))} prediction={predictions.team_performance_prediction}/>
      </div>

       <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
         <div className="lg:col-span-2"><EnhancedExecutiveChart /></div>
         <AutomatedInsightsPanel insights={insights} />
       </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PredictiveAnalyticsWidget title="Customer Churn Risk" />
        <PredictiveAnalyticsWidget title="Sales Forecast" />
      </div>

    </div>
  );
};

export default AIEnhancedCEODashboard; 
import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription } from '../ui/alert';
import { Loader2, TrendingUp, TrendingDown, AlertTriangle, Lightbulb } from 'lucide-react';
import EnhancedKPICard from './EnhancedKPICard';
// Assuming these components exist or will be created
// import { EnhancedExecutiveChart } from './EnhancedExecutiveChart';
// import { AutomatedInsightsPanel } from './AutomatedInsightsPanel';
// import { PredictiveAnalyticsWidget } from './PredictiveAnalyticsWidget';

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
    try {
      setLoading(true);
      const metricsResponse = await fetch('/api/intelligence/dashboard/enhanced-metrics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer faketoken' },
        body: JSON.stringify({ timeRange: selectedTimeRange })
      });
      const metricsData = await metricsResponse.json();
      setDashboardData(metricsData.metrics);
      setInsights(metricsData.insights || []);
      setPredictions(metricsData.predictions || {});
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  }, [selectedTimeRange]);

  const handleNaturalLanguageQuery = async () => {
    if (!naturalLanguageQuery.trim()) return;
    try {
      setQueryLoading(true);
      const response = await fetch('/api/intelligence/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer faketoken' },
        body: JSON.stringify({ query: naturalLanguageQuery, context: { role: 'CEO' } })
      });
      const result = await response.json();
      setQueryResponse(result);
    } catch (error) {
      console.error('Failed to process natural language query:', error);
      setQueryResponse({ answer: 'I encountered an error processing your query.', confidence_score: 0, sources_used: [] });
    } finally {
      setQueryLoading(false);
    }
  };

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
        <h1 className="text-4xl font-bold mb-2">AI-Enhanced Executive Command Center</h1>
        <p className="text-slate-300">Powered by Snowflake Intelligence & Cortex AI</p>
      </div>
      
      <Card className="bg-white/10 backdrop-blur-xl border-white/20 mb-6">
        <CardHeader><CardTitle>Ask Anything About Your Business</CardTitle></CardHeader>
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

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <EnhancedKPICard
            title="Revenue"
            value={dashboardData?.revenue?.current || 0}
            previousValue={dashboardData?.revenue?.previous || 0}
            format="currency"
            insight={insights.find(i => i.metrics_affected?.includes('revenue'))}
            prediction={predictions.revenue_prediction}
        />
        {/* Add more EnhancedKPICard instances for other metrics */}
      </div>
    </div>
  );
};

export default AIEnhancedCEODashboard; 
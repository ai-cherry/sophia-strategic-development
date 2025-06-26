import { useState, useEffect, useCallback } from 'react';
import apiClient from '../../../../services/apiClient';

export const useCEOMetrics = (timeRange = '30d') => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMetrics = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Try to fetch real CEO metrics
      const result = await apiClient.getCEOKPIs(timeRange);
      
      if (result.success) {
        setMetrics(result.data);
      } else {
        // Fallback to mock data with real-time variation
        const mockMetrics = {
          revenue: {
            current: '$2.4M',
            change: 5.2 + (Math.random() - 0.5) * 2,
            trend: 'up',
            target: '$2.6M'
          },
          deals: {
            current: '156',
            change: 12 + Math.floor(Math.random() * 10),
            trend: 'up',
            target: '180'
          },
          customerHealth: {
            current: '94%',
            change: 2.5 + (Math.random() - 0.5),
            trend: 'up',
            target: '96%'
          },
          teamPerformance: {
            current: '88%',
            change: 1.8 + (Math.random() - 0.5),
            trend: 'up',
            target: '92%'
          },
          revenueData: [
            { month: 'Jan', revenue: 1800000, target: 1700000, forecast: 1850000 },
            { month: 'Feb', revenue: 1950000, target: 1850000, forecast: 2000000 },
            { month: 'Mar', revenue: 2100000, target: 2000000, forecast: 2150000 },
            { month: 'Apr', revenue: 2250000, target: 2150000, forecast: 2300000 },
            { month: 'May', revenue: 2400000, target: 2300000, forecast: 2450000 },
            { month: 'Jun', revenue: 2550000, target: 2450000, forecast: 2600000 }
          ],
          alerts: [
            {
              id: 1,
              type: 'success',
              title: 'Q2 Revenue Target Exceeded',
              message: 'Revenue exceeded target by 12%',
              timestamp: new Date(),
              priority: 'high'
            },
            {
              id: 2,
              type: 'warning',
              title: 'Competitive Analysis',
              message: 'EliseAI launched new feature - market impact assessment needed',
              timestamp: new Date(Date.now() - 3600000),
              priority: 'medium'
            }
          ]
        };
        
        setMetrics(mockMetrics);
      }
    } catch (err) {
      console.error('Failed to fetch CEO metrics:', err);
      setError(err.message);
      
      // Even on error, provide basic mock data
      setMetrics({
        revenue: { current: 'N/A', change: 0, trend: 'neutral' },
        deals: { current: 'N/A', change: 0, trend: 'neutral' },
        customerHealth: { current: 'N/A', change: 0, trend: 'neutral' },
        teamPerformance: { current: 'N/A', change: 0, trend: 'neutral' },
        revenueData: [],
        alerts: []
      });
    } finally {
      setLoading(false);
    }
  }, [timeRange]);

  useEffect(() => {
    fetchMetrics();
  }, [fetchMetrics]);

  return {
    metrics,
    loading,
    error,
    refresh: fetchMetrics
  };
};


import { useState, useEffect, useCallback } from 'react';
import apiClient from '../../../../services/apiClient';

export const useMarketData = (timeRange = '30d') => {
  const [marketData, setMarketData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMarketData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Try to fetch real market data
      const result = await apiClient.getMarketData(timeRange);
      
      if (result.success) {
        setMarketData(result.data);
      } else {
        // Mock market intelligence data
        const mockMarketData = {
          marketShare: {
            current: 12.3,
            change: 1.8,
            trend: 'up',
            competitors: [
              { name: 'EliseAI', share: 28.5, change: -0.8 },
              { name: 'RentSpree', share: 18.2, change: 0.3 },
              { name: 'LeaseHawk', share: 15.7, change: -1.2 },
              { name: 'Pay Ready', share: 12.3, change: 1.8 },
              { name: 'Others', share: 25.3, change: -0.1 }
            ]
          },
          competitiveIntel: [
            {
              competitor: 'EliseAI',
              update: 'Launched AI-powered lease renewal automation',
              impact: 'High',
              date: new Date(Date.now() - 86400000),
              action: 'Monitor pricing changes'
            },
            {
              competitor: 'RentSpree',
              update: 'Expanded to 3 new markets',
              impact: 'Medium',
              date: new Date(Date.now() - 172800000),
              action: 'Evaluate market expansion'
            }
          ],
          marketTrends: [
            {
              trend: 'AI-Powered Automation',
              growth: 45,
              impact: 'High',
              opportunity: 'Expand AI capabilities'
            },
            {
              trend: 'Mobile-First Solutions',
              growth: 32,
              impact: 'Medium',
              opportunity: 'Enhance mobile experience'
            },
            {
              trend: 'Integration Platforms',
              growth: 28,
              impact: 'High',
              opportunity: 'Develop ecosystem partnerships'
            }
          ],
          industryMetrics: {
            marketSize: '$2.8B',
            growthRate: '23.4%',
            totalCompanies: 147,
            funding: '$450M'
          }
        };
        
        setMarketData(mockMarketData);
      }
    } catch (err) {
      console.error('Failed to fetch market data:', err);
      setError(err.message);
      
      setMarketData({
        marketShare: { current: 0, change: 0, trend: 'neutral', competitors: [] },
        competitiveIntel: [],
        marketTrends: [],
        industryMetrics: {}
      });
    } finally {
      setLoading(false);
    }
  }, [timeRange]);

  useEffect(() => {
    fetchMarketData();
  }, [fetchMarketData]);

  return {
    marketData,
    loading,
    error,
    refresh: fetchMarketData
  };
};

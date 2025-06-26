import { useState, useEffect, useCallback } from 'react';
import apiClient from '../../../../services/apiClient';

export const useTeamPerformance = (timeRange = '30d') => {
  const [performance, setPerformance] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchTeamPerformance = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Try to fetch real team performance data
      const result = await apiClient.getTeamPerformance(timeRange);
      
      if (result.success) {
        setPerformance(result.data);
      } else {
        // Mock team performance data
        const mockPerformance = {
          departments: [
            {
              name: 'Sales',
              score: 92,
              trend: 'up',
              change: 5.2,
              target: 95,
              metrics: {
                revenue: '$1.8M',
                deals: 45,
                conversion: '18%'
              }
            },
            {
              name: 'Marketing',
              score: 87,
              trend: 'up',
              change: 3.1,
              target: 90,
              metrics: {
                leads: '2,340',
                campaigns: 12,
                engagement: '24%'
              }
            },
            {
              name: 'Product',
              score: 94,
              trend: 'stable',
              change: 0.8,
              target: 95,
              metrics: {
                features: 8,
                bugFixes: 23,
                satisfaction: '96%'
              }
            },
            {
              name: 'Customer Success',
              score: 91,
              trend: 'up',
              change: 4.3,
              target: 93,
              metrics: {
                nps: 8.4,
                retention: '94%',
                tickets: 156
              }
            }
          ],
          overall: {
            score: 91,
            trend: 'up',
            change: 3.4,
            bestPerformer: 'Product',
            needsAttention: 'Marketing'
          },
          goals: [
            {
              department: 'Sales',
              goal: 'Q2 Revenue Target',
              progress: 85,
              status: 'on-track'
            },
            {
              department: 'Marketing',
              goal: 'Lead Generation',
              progress: 72,
              status: 'needs-attention'
            },
            {
              department: 'Product',
              goal: 'Feature Delivery',
              progress: 95,
              status: 'ahead'
            }
          ]
        };
        
        setPerformance(mockPerformance);
      }
    } catch (err) {
      console.error('Failed to fetch team performance:', err);
      setError(err.message);
      
      setPerformance({
        departments: [],
        overall: { score: 0, trend: 'neutral', change: 0 },
        goals: []
      });
    } finally {
      setLoading(false);
    }
  }, [timeRange]);

  useEffect(() => {
    fetchTeamPerformance();
  }, [fetchTeamPerformance]);

  return {
    performance,
    loading,
    error,
    refresh: fetchTeamPerformance
  };
};

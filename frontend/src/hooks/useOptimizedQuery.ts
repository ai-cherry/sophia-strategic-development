/**
 * Optimized Query Hook for Sophia AI Executive Dashboard
 * Provides efficient data fetching with caching and error handling
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import apiClient, { ApiResponse } from '../services/apiClient';

interface QueryOptions {
  enabled?: boolean;
  refetchInterval?: number;
  cacheTime?: number;
  retryCount?: number;
  retryDelay?: number;
  onSuccess?: (data: any) => void;
  onError?: (error: string) => void;
}

interface QueryState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  isStale: boolean;
}

// Simple in-memory cache
const queryCache = new Map<string, {
  data: any;
  timestamp: number;
  cacheTime: number;
}>();

export function useOptimizedQuery<T = any>(
  queryKey: string,
  queryFn: () => Promise<ApiResponse<T>>,
  options: QueryOptions = {}
): QueryState<T> {
  const {
    enabled = true,
    refetchInterval,
    cacheTime = 5 * 60 * 1000, // 5 minutes default
    retryCount = 3,
    retryDelay = 1000,
    onSuccess,
    onError
  } = options;

  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isStale, setIsStale] = useState(false);
  
  const retryCountRef = useRef(0);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const isMountedRef = useRef(true);

  // Check cache for existing data
  const getCachedData = useCallback((): T | null => {
    const cached = queryCache.get(queryKey);
    if (cached && Date.now() - cached.timestamp < cached.cacheTime) {
      return cached.data;
    }
    return null;
  }, [queryKey]);

  // Set cache data
  const setCachedData = useCallback((newData: T) => {
    queryCache.set(queryKey, {
      data: newData,
      timestamp: Date.now(),
      cacheTime
    });
  }, [queryKey, cacheTime]);

  // Execute query with retry logic
  const executeQuery = useCallback(async (isRetry = false) => {
    if (!enabled) return;

    // Check cache first
    const cachedData = getCachedData();
    if (cachedData && !isRetry) {
      setData(cachedData);
      setIsStale(false);
      return;
    }

    if (!isRetry) {
      setLoading(true);
      setError(null);
      setIsStale(false);
    }

    try {
      const response = await queryFn();
      
      if (!isMountedRef.current) return;

      if (response.error) {
        throw new Error(response.error);
      }

      const newData = response.data;
      setData(newData);
      setCachedData(newData);
      setError(null);
      retryCountRef.current = 0;

      if (onSuccess) {
        onSuccess(newData);
      }

    } catch (err) {
      if (!isMountedRef.current) return;

      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      
      // Retry logic
      if (retryCountRef.current < retryCount) {
        retryCountRef.current++;
        setTimeout(() => {
          executeQuery(true);
        }, retryDelay * retryCountRef.current);
        return;
      }

      setError(errorMessage);
      
      if (onError) {
        onError(errorMessage);
      }
    } finally {
      if (isMountedRef.current) {
        setLoading(false);
      }
    }
  }, [
    enabled, 
    queryFn, 
    getCachedData, 
    setCachedData, 
    retryCount, 
    retryDelay, 
    onSuccess, 
    onError
  ]);

  // Refetch function
  const refetch = useCallback(async () => {
    retryCountRef.current = 0;
    await executeQuery(true);
  }, [executeQuery]);

  // Initial fetch
  useEffect(() => {
    executeQuery();
  }, [executeQuery]);

  // Set up polling if refetchInterval is provided
  useEffect(() => {
    if (refetchInterval && enabled) {
      intervalRef.current = setInterval(() => {
        setIsStale(true);
        executeQuery(true);
      }, refetchInterval);

      return () => {
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
        }
      };
    }
  }, [refetchInterval, enabled, executeQuery]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isMountedRef.current = false;
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  return {
    data,
    loading,
    error,
    refetch,
    isStale
  };
}

// Specialized hooks for common queries
export function useHealthQuery(options?: QueryOptions) {
  return useOptimizedQuery(
    'health',
    () => apiClient.getHealth(),
    {
      refetchInterval: 30000, // 30 seconds
      ...options
    }
  );
}

export function useSystemStatusQuery(options?: QueryOptions) {
  return useOptimizedQuery(
    'system-status',
    () => apiClient.getSystemStatus(),
    {
      refetchInterval: 10000, // 10 seconds
      ...options
    }
  );
}

export function useBusinessIntelligenceQuery(options?: QueryOptions) {
  return useOptimizedQuery(
    'business-intelligence',
    () => apiClient.getBusinessIntelligence(),
    {
      refetchInterval: 60000, // 1 minute
      ...options
    }
  );
}

export function useMemoryInsightsQuery(options?: QueryOptions) {
  return useOptimizedQuery(
    'memory-insights',
    () => apiClient.getMemoryInsights(),
    {
      refetchInterval: 30000, // 30 seconds
      ...options
    }
  );
}

export function useTemporalLearningQuery(options?: QueryOptions) {
  return useOptimizedQuery(
    'temporal-learning',
    () => apiClient.getTemporalLearning(),
    {
      refetchInterval: 45000, // 45 seconds
      ...options
    }
  );
}

export function useLambdaLabsStatusQuery(options?: QueryOptions) {
  return useOptimizedQuery(
    'lambda-labs-status',
    () => apiClient.getLambdaLabsStatus(),
    {
      refetchInterval: 20000, // 20 seconds
      ...options
    }
  );
}

export function useDeploymentStatusQuery(options?: QueryOptions) {
  return useOptimizedQuery(
    'deployment-status',
    () => apiClient.getDeploymentStatus(),
    {
      refetchInterval: 15000, // 15 seconds
      ...options
    }
  );
}

export function useAIMemoryHealthQuery(options?: QueryOptions) {
  return useOptimizedQuery(
    'ai-memory-health',
    () => apiClient.getAIMemoryHealth(),
    {
      refetchInterval: 25000, // 25 seconds
      ...options
    }
  );
}

export function useCompetitorIntelligenceQuery(options?: QueryOptions) {
  return useOptimizedQuery(
    'competitor-intelligence',
    () => apiClient.getCompetitorIntelligence(),
    {
      refetchInterval: 300000, // 5 minutes
      ...options
    }
  );
}

export function useExternalIntelligenceQuery(options?: QueryOptions) {
  return useOptimizedQuery(
    'external-intelligence',
    () => apiClient.getExternalIntelligence(),
    {
      refetchInterval: 120000, // 2 minutes
      ...options
    }
  );
}

// Utility to clear cache
export function clearQueryCache(queryKey?: string) {
  if (queryKey) {
    queryCache.delete(queryKey);
  } else {
    queryCache.clear();
  }
}

// Utility to get cache status
export function getCacheStatus() {
  return {
    size: queryCache.size,
    keys: Array.from(queryCache.keys()),
    totalMemory: JSON.stringify(Array.from(queryCache.entries())).length
  };
} 
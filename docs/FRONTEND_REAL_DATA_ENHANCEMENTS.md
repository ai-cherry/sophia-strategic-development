# Frontend Enhancements for Real Data

**Date:** July 6, 2025
**Version:** 1.0
**Focus:** Frontend optimizations for live data integration

## Overview

This document outlines frontend enhancements needed to support the transition from mock to live data, ensuring optimal user experience with potentially slower and more variable data sources.

## 1. Loading States & Progressive Rendering

### 1.1 Skeleton Screens

```tsx
// frontend/src/components/shared/SkeletonLoader.tsx
import React from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui';

export const DealSkeleton = () => (
  <Card className="animate-pulse">
    <CardHeader>
      <div className="h-4 bg-gray-200 rounded w-3/4"></div>
    </CardHeader>
    <CardContent>
      <div className="space-y-2">
        <div className="h-4 bg-gray-200 rounded"></div>
        <div className="h-4 bg-gray-200 rounded w-5/6"></div>
        <div className="h-4 bg-gray-200 rounded w-4/6"></div>
      </div>
    </CardContent>
  </Card>
);

export const ChartSkeleton = () => (
  <div className="animate-pulse">
    <div className="h-64 bg-gray-200 rounded"></div>
    <div className="mt-4 grid grid-cols-4 gap-2">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="h-4 bg-gray-200 rounded"></div>
      ))}
    </div>
  </div>
);
```

### 1.2 Progressive Data Loading

```tsx
// frontend/src/hooks/useProgressiveData.ts
import { useState, useEffect, useCallback } from 'react';
import apiClient from '../services/apiClient';

interface ProgressiveDataState<T> {
  data: T | null;
  partialData: Partial<T> | null;
  isLoading: boolean;
  isPartiallyLoaded: boolean;
  error: Error | null;
  refetch: () => void;
}

export function useProgressiveData<T>(
  endpoint: string,
  options?: {
    initialData?: Partial<T>;
    refreshInterval?: number;
  }
): ProgressiveDataState<T> {
  const [state, setState] = useState<ProgressiveDataState<T>>({
    data: null,
    partialData: options?.initialData || null,
    isLoading: true,
    isPartiallyLoaded: false,
    error: null,
    refetch: () => {},
  });

  const fetchData = useCallback(async () => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      // First, try to get cached/partial data
      const partialResponse = await apiClient.get(`${endpoint}?partial=true`);
      if (partialResponse.data) {
        setState(prev => ({
          ...prev,
          partialData: partialResponse.data,
          isPartiallyLoaded: true,
        }));
      }

      // Then fetch complete data
      const fullResponse = await apiClient.get(endpoint);
      setState(prev => ({
        ...prev,
        data: fullResponse.data,
        isLoading: false,
        isPartiallyLoaded: false,
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: error as Error,
        isLoading: false,
      }));
    }
  }, [endpoint]);

  useEffect(() => {
    fetchData();

    if (options?.refreshInterval) {
      const interval = setInterval(fetchData, options.refreshInterval);
      return () => clearInterval(interval);
    }
  }, [fetchData, options?.refreshInterval]);

  return { ...state, refetch: fetchData };
}
```

## 2. Enhanced Error Handling

### 2.1 Error Boundary with Retry

```tsx
// frontend/src/components/shared/DataErrorBoundary.tsx
import React, { Component, ReactNode } from 'react';
import { Alert, AlertDescription, Button } from '@/components/ui';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onRetry?: () => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorType: 'connection' | 'data' | 'unknown';
}

export class DataErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null, errorType: 'unknown' };
  }

  static getDerivedStateFromError(error: Error): State {
    // Categorize error type
    let errorType: State['errorType'] = 'unknown';

    if (error.message.includes('Network') || error.message.includes('fetch')) {
      errorType = 'connection';
    } else if (error.message.includes('validation') || error.message.includes('data')) {
      errorType = 'data';
    }

    return {
      hasError: true,
      error,
      errorType,
    };
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error('Data error caught:', error, errorInfo);
    // Send to monitoring service
  }

  render() {
    if (this.state.hasError) {
      const { error, errorType } = this.state;

      if (this.props.fallback) {
        return <>{this.props.fallback}</>;
      }

      return (
        <Alert className="m-4">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            <div className="space-y-2">
              <p className="font-semibold">
                {errorType === 'connection' && 'Connection Error'}
                {errorType === 'data' && 'Data Processing Error'}
                {errorType === 'unknown' && 'Unexpected Error'}
              </p>
              <p className="text-sm text-gray-600">
                {errorType === 'connection' &&
                  'Unable to connect to our servers. Please check your internet connection.'}
                {errorType === 'data' &&
                  'The data received was invalid or incomplete. Our team has been notified.'}
                {errorType === 'unknown' &&
                  'Something went wrong. Please try again.'}
              </p>
              <p className="text-xs text-gray-500">{error?.message}</p>
              <Button
                size="sm"
                onClick={() => {
                  this.setState({ hasError: false, error: null });
                  this.props.onRetry?.();
                }}
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Try Again
              </Button>
            </div>
          </AlertDescription>
        </Alert>
      );
    }

    return this.props.children;
  }
}
```

### 2.2 Inline Error States

```tsx
// frontend/src/components/shared/DataFetchError.tsx
import React from 'react';
import { Alert, AlertDescription, Button } from '@/components/ui';
import { AlertTriangle, RefreshCw, WifiOff, Database } from 'lucide-react';

interface DataFetchErrorProps {
  error: Error;
  source?: string;
  onRetry?: () => void;
}

export const DataFetchError: React.FC<DataFetchErrorProps> = ({
  error,
  source,
  onRetry,
}) => {
  const isNetworkError = error.message.includes('Network') ||
                        error.message.includes('fetch');
  const isDataSourceError = error.message.includes('Snowflake') ||
                           error.message.includes('Gong') ||
                           error.message.includes('HubSpot');

  return (
    <Alert variant="destructive" className="my-4">
      <div className="flex items-start space-x-2">
        {isNetworkError ? (
          <WifiOff className="h-5 w-5 mt-0.5" />
        ) : isDataSourceError ? (
          <Database className="h-5 w-5 mt-0.5" />
        ) : (
          <AlertTriangle className="h-5 w-5 mt-0.5" />
        )}
        <div className="flex-1">
          <AlertDescription>
            <p className="font-semibold mb-1">
              {isNetworkError && 'Connection Problem'}
              {isDataSourceError && `${source || 'Data Source'} Unavailable`}
              {!isNetworkError && !isDataSourceError && 'Error Loading Data'}
            </p>
            <p className="text-sm mb-2">
              {isNetworkError &&
                'Please check your internet connection and try again.'}
              {isDataSourceError &&
                `We're having trouble connecting to ${source || 'the data source'}. This is usually temporary.`}
              {!isNetworkError && !isDataSourceError &&
                'An unexpected error occurred while loading your data.'}
            </p>
            {onRetry && (
              <Button size="sm" variant="outline" onClick={onRetry}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Retry
              </Button>
            )}
          </AlertDescription>
        </div>
      </div>
    </Alert>
  );
};
```

## 3. Dynamic Data Visualization

### 3.1 Adaptive Charts

```tsx
// frontend/src/components/charts/AdaptiveChart.tsx
import React, { useMemo } from 'react';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui';
import { ChartSkeleton } from '../shared/SkeletonLoader';

interface AdaptiveChartProps {
  data: any[];
  title: string;
  type?: 'line' | 'bar' | 'doughnut';
  loading?: boolean;
  error?: Error;
}

export const AdaptiveChart: React.FC<AdaptiveChartProps> = ({
  data,
  title,
  type = 'line',
  loading,
  error,
}) => {
  const chartData = useMemo(() => {
    if (!data || data.length === 0) return null;

    // Adapt data based on volume
    const dataPoints = data.length;
    const shouldAggregate = dataPoints > 100;

    if (shouldAggregate) {
      // Aggregate data for better visualization
      return aggregateData(data);
    }

    return formatChartData(data, type);
  }, [data, type]);

  const chartOptions = useMemo(() => ({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: type === 'doughnut',
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
      },
    },
    scales: type !== 'doughnut' ? {
      y: {
        beginAtZero: true,
        ticks: {
          callback: (value: any) => {
            if (value >= 1000000) {
              return `$${(value / 1000000).toFixed(1)}M`;
            } else if (value >= 1000) {
              return `$${(value / 1000).toFixed(0)}K`;
            }
            return `$${value}`;
          },
        },
      },
    } : undefined,
  }), [type]);

  if (loading) {
    return <ChartSkeleton />;
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64 flex items-center justify-center text-gray-500">
            Unable to load chart data
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!chartData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64 flex items-center justify-center text-gray-500">
            No data available
          </div>
        </CardContent>
      </Card>
    );
  }

  const ChartComponent = {
    line: Line,
    bar: Bar,
    doughnut: Doughnut,
  }[type];

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-64">
          <ChartComponent data={chartData} options={chartOptions} />
        </div>
      </CardContent>
    </Card>
  );
};

// Helper functions
function aggregateData(data: any[]) {
  // Implementation for data aggregation
  // Group by time periods, categories, etc.
}

function formatChartData(data: any[], type: string) {
  // Implementation for formatting data for charts
}
```

### 3.2 Real-time Data Updates

```tsx
// frontend/src/hooks/useRealtimeData.ts
import { useEffect, useState, useRef } from 'react';
import { io, Socket } from 'socket.io-client';

interface RealtimeDataOptions {
  channel: string;
  initialData?: any;
  onUpdate?: (data: any) => void;
  reconnectAttempts?: number;
}

export function useRealtimeData<T>({
  channel,
  initialData,
  onUpdate,
  reconnectAttempts = 3,
}: RealtimeDataOptions) {
  const [data, setData] = useState<T | null>(initialData || null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const socketRef = useRef<Socket | null>(null);
  const reconnectCount = useRef(0);

  useEffect(() => {
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'wss://ws.sophia-intel.ai';

    const connect = () => {
      socketRef.current = io(wsUrl, {
        transports: ['websocket'],
        reconnection: true,
        reconnectionAttempts: reconnectAttempts,
      });

      socketRef.current.on('connect', () => {
        setIsConnected(true);
        setError(null);
        reconnectCount.current = 0;

        // Subscribe to channel
        socketRef.current?.emit('subscribe', { channel });
      });

      socketRef.current.on('disconnect', () => {
        setIsConnected(false);
      });

      socketRef.current.on('error', (err) => {
        setError(new Error(err.message || 'WebSocket error'));
      });

      socketRef.current.on(`data:${channel}`, (newData: T) => {
        setData(newData);
        onUpdate?.(newData);
      });

      socketRef.current.on('reconnect_failed', () => {
        setError(new Error('Failed to reconnect after multiple attempts'));
      });
    };

    connect();

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, [channel, wsUrl, reconnectAttempts, onUpdate]);

  return {
    data,
    isConnected,
    error,
    reconnect: () => {
      if (socketRef.current) {
        socketRef.current.connect();
      }
    },
  };
}
```

## 4. Performance Optimizations

### 4.1 Data Caching Strategy

```tsx
// frontend/src/services/cacheService.ts
interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

class CacheService {
  private cache: Map<string, CacheEntry<any>> = new Map();
  private readonly defaultTTL = 5 * 60 * 1000; // 5 minutes

  set<T>(key: string, data: T, ttl?: number): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl: ttl || this.defaultTTL,
    });
  }

  get<T>(key: string): T | null {
    const entry = this.cache.get(key);

    if (!entry) return null;

    const isExpired = Date.now() - entry.timestamp > entry.ttl;

    if (isExpired) {
      this.cache.delete(key);
      return null;
    }

    return entry.data;
  }

  invalidate(pattern?: string): void {
    if (!pattern) {
      this.cache.clear();
      return;
    }

    // Invalidate keys matching pattern
    for (const key of this.cache.keys()) {
      if (key.includes(pattern)) {
        this.cache.delete(key);
      }
    }
  }

  preload(endpoints: string[]): Promise<void[]> {
    // Preload critical data
    return Promise.all(
      endpoints.map(endpoint =>
        fetch(endpoint)
          .then(res => res.json())
          .then(data => this.set(endpoint, data))
      )
    );
  }
}

export const cacheService = new CacheService();
```

### 4.2 Optimized Data Fetching

```tsx
// frontend/src/hooks/useOptimizedQuery.ts
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { cacheService } from '../services/cacheService';
import apiClient from '../services/apiClient';

interface OptimizedQueryOptions {
  staleTime?: number;
  cacheTime?: number;
  refetchInterval?: number;
  optimisticUpdate?: boolean;
}

export function useOptimizedQuery<T>(
  key: string | string[],
  endpoint: string,
  options?: OptimizedQueryOptions
) {
  const queryClient = useQueryClient();
  const cacheKey = Array.isArray(key) ? key.join(':') : key;

  return useQuery({
    queryKey: Array.isArray(key) ? key : [key],
    queryFn: async () => {
      // Check frontend cache first
      const cached = cacheService.get<T>(cacheKey);
      if (cached && options?.optimisticUpdate) {
        return cached;
      }

      // Fetch from API
      const response = await apiClient.get(endpoint);
      const data = response.data;

      // Update frontend cache
      cacheService.set(cacheKey, data);

      return data;
    },
    staleTime: options?.staleTime || 60000, // 1 minute
    cacheTime: options?.cacheTime || 300000, // 5 minutes
    refetchInterval: options?.refetchInterval,
    onSuccess: (data) => {
      // Update related queries if needed
      if (endpoint.includes('sales')) {
        queryClient.invalidateQueries(['analytics']);
      }
    },
  });
}
```

## Implementation Checklist

### Immediate Actions
- [ ] Implement skeleton loaders for all data-heavy components
- [ ] Add error boundaries to dashboard sections
- [ ] Create loading state components

### Short-term (1 week)
- [ ] Implement progressive data loading
- [ ] Add comprehensive error handling
- [ ] Set up real-time data updates

### Medium-term (2 weeks)
- [ ] Optimize chart rendering for large datasets
- [ ] Implement frontend caching strategy
- [ ] Add performance monitoring

## Conclusion

These frontend enhancements ensure a smooth user experience during the transition to live data, handling the increased latency, potential errors, and variable data quality that comes with real-world data sources.

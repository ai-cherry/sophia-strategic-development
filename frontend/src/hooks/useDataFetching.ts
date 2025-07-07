import { useState, useEffect, useCallback, useRef } from 'react';
import { useQuery, useQueryClient, QueryKey } from '@tanstack/react-query';
import { io, Socket } from 'socket.io-client';

import apiClient from '../services/apiClient';

// =================================
// Optimized Query Hook
// =================================

interface OptimizedQueryOptions {
  staleTime?: number;
  cacheTime?: number;
  refetchInterval?: number;
  enabled?: boolean;
}

const useOptimizedQuery = (queryKey, url, options) => {
  const queryClient = useQueryClient();

  const fetcher = async () => {
    const response = await apiClient.get(url);
    return response.data;
  };

  return useQuery(queryKey, fetcher, {
    ...options,
    onError: (error) => {
      console.error(`Error fetching ${url}:`, error);
      // Optional: Add global error handling, e.g., showing a toast notification
    },
    onSuccess: (data) => {
      // Optional: Add global success handling or logging
    },
  });
};

export { useOptimizedQuery };

// =================================
// Real-time Data Hook
// =================================

interface RealtimeDataOptions<T> {
  channel: string;
  onUpdate?: (data: T) => void;
}

export function useRealtimeData<T>({ channel, onUpdate }: RealtimeDataOptions) {
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const socketRef = useRef<Socket | null>(null);

  useEffect(() => {
    const wsUrl = import.meta.env.VITE_WS_URL || 'wss://ws.sophia-intel.ai';

    socketRef.current = io(wsUrl, {
      transports: ['websocket'],
      reconnection: true,
      reconnectionAttempts: 5,
    });

    socketRef.current.on('connect', () => {
      setIsConnected(true);
      setError(null);
      socketRef.current?.emit('subscribe', { channel });
    });

    socketRef.current.on('disconnect', () => setIsConnected(false));
    socketRef.current.on('error', (err) => setError(new Error(err.message || 'WebSocket error')));
    socketRef.current.on(`data:${channel}`, (newData: T) => onUpdate?.(newData));
    socketRef.current.on('reconnect_failed', () => setError(new Error('Failed to reconnect.')));

    return () => {
        socketRef.current?.disconnect();
    };
  }, [channel, onUpdate]);

  return { isConnected, error };
}

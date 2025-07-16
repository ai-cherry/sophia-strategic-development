import { useState, useEffect, useRef, useCallback } from 'react';

export interface PollingConfig {
  baseInterval: number;
  maxInterval: number;
  backoffMultiplier: number;
  errorThreshold: number;
  successThreshold: number;
}

export interface PollingState {
  isPolling: boolean;
  currentInterval: number;
  errorCount: number;
  successCount: number;
  lastSuccess: number | null;
  lastError: string | null;
}

const defaultConfig: PollingConfig = {
  baseInterval: 5000,      // Start with 5 seconds
  maxInterval: 60000,      // Max 60 seconds
  backoffMultiplier: 1.5,  // Increase by 50% on errors
  errorThreshold: 3,       // After 3 errors, increase interval
  successThreshold: 5      // After 5 successes, decrease interval
};

/**
 * Intelligent Polling Hook
 * Adapts polling frequency based on success/error rates
 * Replaces fixed 5-second polling with adaptive behavior
 */
export const useIntelligentPolling = (
  pollFunction: () => Promise<any>,
  config: Partial<PollingConfig> = {},
  enabled: boolean = true
) => {
  const finalConfig = { ...defaultConfig, ...config };
  const [state, setState] = useState<PollingState>({
    isPolling: false,
    currentInterval: finalConfig.baseInterval,
    errorCount: 0,
    successCount: 0,
    lastSuccess: null,
    lastError: null
  });
  
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isPollingRef = useRef(false);
  
  const calculateNextInterval = useCallback((
    currentInterval: number,
    errorCount: number,
    successCount: number
  ): number => {
    if (errorCount >= finalConfig.errorThreshold) {
      // Increase interval on errors (exponential backoff)
      return Math.min(
        currentInterval * finalConfig.backoffMultiplier,
        finalConfig.maxInterval
      );
    } else if (successCount >= finalConfig.successThreshold) {
      // Decrease interval on success (but not below base)
      return Math.max(
        currentInterval / finalConfig.backoffMultiplier,
        finalConfig.baseInterval
      );
    }
    return currentInterval;
  }, [finalConfig]);
  
  const executePoll = useCallback(async () => {
    if (!isPollingRef.current) return;
    
    try {
      await pollFunction();
      
      setState(prevState => {
        const newSuccessCount = prevState.successCount + 1;
        const newErrorCount = 0; // Reset error count on success
        const newInterval = calculateNextInterval(
          prevState.currentInterval,
          newErrorCount,
          newSuccessCount
        );
        
        return {
          ...prevState,
          errorCount: newErrorCount,
          successCount: newSuccessCount,
          currentInterval: newInterval,
          lastSuccess: Date.now(),
          lastError: null
        };
      });
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      
      setState(prevState => {
        const newErrorCount = prevState.errorCount + 1;
        const newSuccessCount = 0; // Reset success count on error
        const newInterval = calculateNextInterval(
          prevState.currentInterval,
          newErrorCount,
          newSuccessCount
        );
        
        return {
          ...prevState,
          errorCount: newErrorCount,
          successCount: newSuccessCount,
          currentInterval: newInterval,
          lastError: errorMessage
        };
      });
      
      console.warn('⚠️ Polling error:', errorMessage);
    }
  }, [pollFunction, calculateNextInterval]);
  
  const scheduleNextPoll = useCallback(() => {
    if (isPollingRef.current) {
      timeoutRef.current = setTimeout(() => {
        executePoll();
        scheduleNextPoll();
      }, state.currentInterval);
    }
  }, [executePoll, state.currentInterval]);
  
  const startPolling = useCallback(() => {
    if (!isPollingRef.current) {
      isPollingRef.current = true;
      setState(prev => ({ ...prev, isPolling: true }));
      executePoll(); // Execute immediately
      scheduleNextPoll();
    }
  }, [executePoll, scheduleNextPoll]);
  
  const stopPolling = useCallback(() => {
    isPollingRef.current = false;
    setState(prev => ({ ...prev, isPolling: false }));
    
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  }, []);
  
  const resetPolling = useCallback(() => {
    setState({
      isPolling: false,
      currentInterval: finalConfig.baseInterval,
      errorCount: 0,
      successCount: 0,
      lastSuccess: null,
      lastError: null
    });
  }, [finalConfig.baseInterval]);
  
  // Auto-start/stop based on enabled flag
  useEffect(() => {
    if (enabled) {
      startPolling();
    } else {
      stopPolling();
    }
    
    return () => {
      stopPolling();
    };
  }, [enabled, startPolling, stopPolling]);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopPolling();
    };
  }, [stopPolling]);
  
  return {
    ...state,
    startPolling,
    stopPolling,
    resetPolling,
    config: finalConfig
  };
};

export default useIntelligentPolling;

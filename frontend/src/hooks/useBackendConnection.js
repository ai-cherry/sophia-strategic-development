import { useState, useEffect, useCallback } from 'react';
import apiClient from '../services/apiClient';

export const useBackendConnection = () => {
  const [isHealthy, setIsHealthy] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState({
    backend: false,
    snowflake: false,
    websocket: false
  });
  const [error, setError] = useState(null);
  const [lastCheck, setLastCheck] = useState(null);

  const checkConnection = useCallback(async () => {
    try {
      const result = await apiClient.healthCheck();
      
      if (result.success) {
        setIsHealthy(true);
        setConnectionStatus({
          backend: true,
          snowflake: result.data?.services?.core === 'operational',
          websocket: true
        });
        setError(null);
      } else {
        setIsHealthy(false);
        setConnectionStatus({
          backend: false,
          snowflake: false,
          websocket: false
        });
        setError(result.error);
      }
    } catch (err) {
      setIsHealthy(false);
      setConnectionStatus({
        backend: false,
        snowflake: false,
        websocket: false
      });
      setError(err.message);
    } finally {
      setLastCheck(new Date());
    }
  }, []);

  useEffect(() => {
    // Initial check
    checkConnection();

    // Set up periodic health checks every 30 seconds
    const interval = setInterval(checkConnection, 30000);

    return () => clearInterval(interval);
  }, [checkConnection]);

  return {
    isHealthy,
    connectionStatus,
    error,
    lastCheck,
    checkConnection
  };
}; 
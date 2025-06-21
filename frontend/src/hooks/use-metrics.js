import { useState, useEffect } from 'react';
import api from '../services/api';

export default function useMetrics() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    async function fetchMetrics() {
      try {
        setLoading(true);
        const res = await api.getDashboardMetrics();
        if (!cancelled) {
          setData(res);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }
    fetchMetrics();
    return () => {
      cancelled = true;
    };
  }, []);

  return { data, loading, error };
}

import { useEffect, useState } from 'react';
import wsManager from '../services/WebSocketManager';

export default function useRealTimeEvents() {
  const [events, setEvents] = useState([]);
  const [status, setStatus] = useState('connecting');
  const [error, setError] = useState(null);

  useEffect(() => {
    const socket = wsManager.connect();
    const handleMessage = (data) => {
      setEvents((prev) => [data, ...prev]);
    };
    const handleOpen = () => setStatus('connected');
    const handleClose = () => setStatus('disconnected');
    const handleError = (e) => {
      setStatus('error');
      setError(e);
    };
    socket.addEventListener('open', handleOpen);
    socket.addEventListener('close', handleClose);
    socket.addEventListener('error', handleError);
    wsManager.subscribe(handleMessage);
    return () => {
      socket.removeEventListener('open', handleOpen);
      socket.removeEventListener('close', handleClose);
      socket.removeEventListener('error', handleError);
      wsManager.unsubscribe(handleMessage);
    };
  }, []);

  return { events, status, error };
}

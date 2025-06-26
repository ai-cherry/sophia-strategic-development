import axios from 'axios';

// API Configuration
const API_CONFIG = {
  production: 'https://8000-ihyzju3pnhb3mzxu6i43r-a616a0fd.manusvm.computer',
  development: 'http://localhost:8000',
  timeout: 10000,
  retries: 3,
  retryDelay: 1000
};

// Get base URL based on environment
const getBaseURL = () => {
  return process.env.NODE_ENV === 'production' 
    ? API_CONFIG.production 
    : API_CONFIG.development;
};

// Create axios instance with default configuration
const apiClient = axios.create({
  baseURL: getBaseURL(),
  timeout: API_CONFIG.timeout,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Request interceptor for authentication and logging
apiClient.interceptors.request.use(
  (config) => {
    // Add timestamp for debugging
    config.metadata = { startTime: new Date() };
    
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling and logging
apiClient.interceptors.response.use(
  (response) => {
    const duration = new Date() - response.config.metadata.startTime;
    console.log(`✅ API Response: ${response.config.method?.toUpperCase()} ${response.config.url} (${duration}ms)`);
    return response;
  },
  async (error) => {
    const duration = error.config?.metadata ? new Date() - error.config.metadata.startTime : 0;
    console.error(`❌ API Error: ${error.config?.method?.toUpperCase()} ${error.config?.url} (${duration}ms)`, error);
    
    // Handle different error types
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      
      switch (status) {
        case 401:
          // Unauthorized - clear auth and redirect to login
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
          break;
        case 403:
          // Forbidden
          throw new Error('Access denied. You do not have permission to perform this action.');
        case 404:
          // Not found
          throw new Error('The requested resource was not found.');
        case 429:
          // Rate limited
          throw new Error('Too many requests. Please try again later.');
        case 500:
          // Server error
          throw new Error('Internal server error. Please try again later.');
        default:
          // Other server errors
          throw new Error(data?.message || `Server error: ${status}`);
      }
    } else if (error.request) {
      // Network error - no response received
      if (error.code === 'ECONNABORTED') {
        throw new Error('Request timeout. Please check your connection and try again.');
      } else {
        throw new Error('Network error. Please check your connection and try again.');
      }
    } else {
      // Request setup error
      throw new Error('Request failed. Please try again.');
    }
  }
);

// Retry mechanism for failed requests
const retryRequest = async (fn, retries = API_CONFIG.retries) => {
  try {
    return await fn();
  } catch (error) {
    if (retries > 0 && shouldRetry(error)) {
      console.log(`🔄 Retrying request... (${API_CONFIG.retries - retries + 1}/${API_CONFIG.retries})`);
      await new Promise(resolve => setTimeout(resolve, API_CONFIG.retryDelay));
      return retryRequest(fn, retries - 1);
    }
    throw error;
  }
};

// Determine if request should be retried
const shouldRetry = (error) => {
  // Retry on network errors or 5xx server errors
  return !error.response || (error.response.status >= 500 && error.response.status < 600);
};

// API Methods
export const api = {
  // Health check
  health: () => retryRequest(() => apiClient.get('/health')),
  
  // Authentication
  auth: {
    login: (credentials) => retryRequest(() => apiClient.post('/auth/login', credentials)),
    logout: () => retryRequest(() => apiClient.post('/auth/logout')),
    refresh: () => retryRequest(() => apiClient.post('/auth/refresh')),
    me: () => retryRequest(() => apiClient.get('/auth/me'))
  },
  
  // Dashboard data
  dashboard: {
    getMetrics: () => retryRequest(() => apiClient.get('/dashboard/metrics')),
    getKPIs: () => retryRequest(() => apiClient.get('/dashboard/kpis')),
    getChartData: (chartType) => retryRequest(() => apiClient.get(`/dashboard/charts/${chartType}`)),
    getTeamPerformance: () => retryRequest(() => apiClient.get('/dashboard/team-performance'))
  },
  
  // Chat/AI
  chat: {
    sendMessage: (message) => retryRequest(() => apiClient.post('/chat/message', { message })),
    getHistory: () => retryRequest(() => apiClient.get('/chat/history')),
    clearHistory: () => retryRequest(() => apiClient.delete('/chat/history'))
  },
  
  // Search
  search: {
    query: (query, filters = {}) => retryRequest(() => apiClient.post('/search', { query, filters })),
    suggestions: (query) => retryRequest(() => apiClient.get(`/search/suggestions?q=${encodeURIComponent(query)}`))
  },
  
  // Projects
  projects: {
    list: () => retryRequest(() => apiClient.get('/projects')),
    get: (id) => retryRequest(() => apiClient.get(`/projects/${id}`)),
    create: (project) => retryRequest(() => apiClient.post('/projects', project)),
    update: (id, project) => retryRequest(() => apiClient.put(`/projects/${id}`, project)),
    delete: (id) => retryRequest(() => apiClient.delete(`/projects/${id}`))
  },
  
  // Analytics
  analytics: {
    getReports: () => retryRequest(() => apiClient.get('/analytics/reports')),
    getInsights: () => retryRequest(() => apiClient.get('/analytics/insights')),
    exportData: (format = 'csv') => retryRequest(() => apiClient.get(`/analytics/export?format=${format}`))
  }
};

// Connection status checker
export const checkConnection = async () => {
  try {
    const response = await apiClient.get('/health', { timeout: 5000 });
    return {
      connected: true,
      status: response.data?.status || 'healthy',
      latency: response.config.metadata ? new Date() - response.config.metadata.startTime : null
    };
  } catch (error) {
    return {
      connected: false,
      status: 'error',
      error: error.message,
      latency: null
    };
  }
};

// WebSocket connection helper
export const createWebSocketConnection = (endpoint = '/ws') => {
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsHost = getBaseURL().replace(/^https?:/, '');
  const wsUrl = `${wsProtocol}${wsHost}${endpoint}`;
  
  try {
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      console.log('🔌 WebSocket connected');
    };
    
    ws.onclose = () => {
      console.log('🔌 WebSocket disconnected');
    };
    
    ws.onerror = (error) => {
      console.error('🔌 WebSocket error:', error);
    };
    
    return ws;
  } catch (error) {
    console.error('🔌 Failed to create WebSocket connection:', error);
    return null;
  }
};

export default apiClient;


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

// Mock data generators for development/fallback
const generateMockKPIs = () => ({
  revenue: {
    current: 2400000,
    target: 2500000,
    change: 5.2,
    trend: 'up'
  },
  deals: {
    current: 156,
    target: 150,
    change: 12,
    trend: 'up'
  },
  efficiency: {
    current: 112,
    target: 110,
    change: 2.5,
    trend: 'up'
  },
  arr: {
    current: 8300000,
    target: 8000000,
    change: 18,
    trend: 'up'
  }
});

const generateMockTeamPerformance = () => ({
  sales: { performance: 94, target: 90, trend: 'up' },
  engineering: { performance: 88, target: 85, trend: 'up' },
  customerSuccess: { performance: 96, target: 95, trend: 'up' },
  marketing: { performance: 82, target: 80, trend: 'up' },
  operations: { performance: 91, target: 90, trend: 'up' }
});

const generateMockMarketData = () => ({
  marketShare: [
    { name: 'Sophia AI', value: 35, color: '#8b5cf6' },
    { name: 'EliseAI', value: 28, color: '#ef4444' },
    { name: 'Others', value: 37, color: '#6b7280' }
  ],
  competitorAnalysis: {
    threats: 2,
    opportunities: 5,
    marketGrowth: 15.3
  }
});

const generateMockAlerts = () => ([
  {
    id: 1,
    type: 'success',
    title: 'Q2 Revenue Target Exceeded',
    message: 'Revenue has exceeded Q2 target by 5.2%',
    timestamp: new Date().toISOString(),
    priority: 'high'
  },
  {
    id: 2,
    type: 'warning',
    title: 'EliseAI Competitive Feature',
    message: 'Competitor launched new AI feature - review needed',
    timestamp: new Date().toISOString(),
    priority: 'medium'
  },
  {
    id: 3,
    type: 'info',
    title: 'NMHC Conference Opportunity',
    message: 'Speaking opportunity at NMHC conference available',
    timestamp: new Date().toISOString(),
    priority: 'low'
  }
]);

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
  
  // CEO Dashboard Methods
  getCEOKPIs: async (timeRange = '30d') => {
    try {
      const response = await retryRequest(() => apiClient.get(`/ceo/kpis?range=${timeRange}`));
      return response.data;
    } catch (error) {
      console.warn('Using mock KPI data due to API error:', error.message);
      return generateMockKPIs();
    }
  },
  
  getTeamPerformance: async (timeRange = '30d') => {
    try {
      const response = await retryRequest(() => apiClient.get(`/ceo/team-performance?range=${timeRange}`));
      return response.data;
    } catch (error) {
      console.warn('Using mock team performance data due to API error:', error.message);
      return generateMockTeamPerformance();
    }
  },
  
  getMarketData: async () => {
    try {
      const response = await retryRequest(() => apiClient.get('/ceo/market-data'));
      return response.data;
    } catch (error) {
      console.warn('Using mock market data due to API error:', error.message);
      return generateMockMarketData();
    }
  },
  
  getStrategicAlerts: async () => {
    try {
      const response = await retryRequest(() => apiClient.get('/ceo/alerts'));
      return response.data;
    } catch (error) {
      console.warn('Using mock alerts data due to API error:', error.message);
      return generateMockAlerts();
    }
  },
  
  getRevenueProjections: async (timeRange = '12m') => {
    try {
      const response = await retryRequest(() => apiClient.get(`/ceo/revenue-projections?range=${timeRange}`));
      return response.data;
    } catch (error) {
      console.warn('Using mock revenue projections due to API error:', error.message);
      return {
        projections: [
          { month: 'Jan', actual: 2100000, projected: 2000000 },
          { month: 'Feb', actual: 2200000, projected: 2100000 },
          { month: 'Mar', actual: 2400000, projected: 2200000 },
          { month: 'Apr', actual: null, projected: 2500000 },
          { month: 'May', actual: null, projected: 2600000 },
          { month: 'Jun', actual: null, projected: 2700000 }
        ]
      };
    }
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
  },

  // Agno Performance Metrics
  agno: {
    getPerformanceMetrics: async () => {
      try {
        const response = await retryRequest(() => apiClient.get('/agno/performance-metrics'));
        return response.data;
      } catch (error) {
        console.warn('Using mock Agno performance data due to API error:', error.message);
        return {
          summary: {
            call_analysis: {
              avg_instantiation_us: 150,
              pool_size: 8,
              pool_max: 12,
              instantiation_samples: 1024
            }
          },
          last_updated: new Date().toISOString()
        };
      }
    }
  },

  // Knowledge Management
  knowledge: {
    uploadFile: (file) => {
      const formData = new FormData();
      formData.append('file', file);
      return retryRequest(() => apiClient.post('/knowledge/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      }));
    },
    syncSource: (source) => retryRequest(() => apiClient.post(`/knowledge/sync/${source}`)),
    getIngestionJobs: () => retryRequest(() => apiClient.get('/knowledge/jobs')),
    getJobStatus: (jobId) => retryRequest(() => apiClient.get(`/knowledge/jobs/${jobId}`))
  },

  // LLM Cost Analysis
  llm: {
    getCostAnalysis: async (timeRange = '30d') => {
      try {
        const response = await retryRequest(() => apiClient.get(`/llm/cost-analysis?range=${timeRange}`));
        return response.data;
      } catch (error) {
        console.warn('Using mock LLM cost data due to API error:', error.message);
        return [
          { name: 'GPT-4o', cost: 4200 },
          { name: 'Claude 3 Opus', cost: 5500 },
          { name: 'Gemini 1.5 Pro', cost: 3100 },
          { name: 'Llama 3', cost: 1800 },
        ];
      }
    }
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

// Backward compatibility exports
export const fetchAgnoPerformanceMetrics = api.agno.getPerformanceMetrics;


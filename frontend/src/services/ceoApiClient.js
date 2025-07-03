import axios from 'axios';

// Environment-aware backend URL configuration
const getBackendUrl = () => {
  // Check for Vite environment variable first
  if (import.meta.env.VITE_BACKEND_URL) {
    return import.meta.env.VITE_BACKEND_URL;
  }
  
  // Check for legacy React environment variable
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  
  // Environment-based detection
  const isDevelopment = import.meta.env.DEV || 
                       window.location.hostname === 'localhost' ||
                       window.location.hostname === '127.0.0.1';
  
  // Use port 8001 for development (CEO test server)
  const baseURL = isDevelopment ? 'http://localhost:8001' : 'https://api.sophia-intel.ai';
  
  console.log(`CEO API Client using ${isDevelopment ? 'development' : 'production'} URL:`, baseURL);
  return baseURL;
};

// Create specialized axios instance for CEO dashboard
const ceoApiClient = axios.create({
  baseURL: getBackendUrl(),
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Request interceptor
ceoApiClient.interceptors.request.use(
  (config) => {
    config.metadata = { startTime: new Date() };
    console.log(`🚀 CEO API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ CEO API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
ceoApiClient.interceptors.response.use(
  (response) => {
    const duration = new Date() - response.config.metadata.startTime;
    console.log(`✅ CEO API Response: ${response.config.method?.toUpperCase()} ${response.config.url} (${duration}ms)`);
    return response;
  },
  (error) => {
    const duration = error.config?.metadata ? new Date() - error.config.metadata.startTime : 0;
    console.error(`❌ CEO API Error: ${error.config?.method?.toUpperCase()} ${error.config?.url} (${duration}ms)`, error);
    return Promise.reject(error);
  }
);

// CEO Dashboard API Methods
export const ceoApi = {
  // Health check
  health: async () => {
    try {
      const response = await ceoApiClient.get('/api/v1/ceo/health');
      return response.data;
    } catch (error) {
      console.warn('CEO Health check failed:', error.message);
      return { status: 'error', message: error.message };
    }
  },

  // Universal chat
  chat: async (message, searchContext = 'business_intelligence', userId = 'ceo') => {
    try {
      const response = await ceoApiClient.post('/api/v1/ceo/chat', {
        message,
        search_context: searchContext,
        user_id: userId
      });
      return response.data;
    } catch (error) {
      console.warn('CEO Chat failed:', error.message);
      return {
        response: "I'm currently experiencing connectivity issues. Please check the backend connection and try again.",
        sources: [],
        timestamp: new Date().toISOString()
      };
    }
  },

  // Dashboard summary with real-time metrics
  getDashboardSummary: async () => {
    try {
      const response = await ceoApiClient.get('/api/v1/ceo/dashboard/summary');
      return response.data;
    } catch (error) {
      console.error('CEO Dashboard summary failed - Backend connection required:', error.message);
      throw new Error(`Backend API unavailable: ${error.message}`);
    }
  },

  // Universal search
  search: async (query, context = 'universal', limit = 10) => {
    try {
      const response = await ceoApiClient.post('/api/v1/ceo/search', {
        query,
        context,
        limit
      });
      return response.data;
    } catch (error) {
      console.error('CEO Search failed - Backend connection required:', error.message);
      throw new Error(`Search API unavailable: ${error.message}`);
    }
  },

  // Business insights
  getInsights: async (priority = 'all', limit = 5) => {
    try {
      const response = await ceoApiClient.get(`/api/v1/ceo/insights?priority=${priority}&limit=${limit}`);
      return response.data;
    } catch (error) {
      console.error('CEO Insights failed - Backend connection required:', error.message);
      throw new Error(`Insights API unavailable: ${error.message}`);
    }
  },

  // Configuration and capabilities
  getConfig: async () => {
    try {
      const response = await ceoApiClient.get('/api/v1/ceo/config');
      return response.data;
    } catch (error) {
      console.warn('CEO Config failed:', error.message);
      return {
        features: {
          universal_chat: true,
          universal_search: true,
          dashboard_summary: true,
          business_insights: true,
          real_time_metrics: true
        },
        search_contexts: [
          'business_intelligence',
          'universal',
          'internal',
          'web_research',
          'deep_research',
          'blended'
        ],
        version: '1.0.0'
      };
    }
  }
};

// Connection status checker for CEO dashboard
export const checkCEOConnection = async () => {
  try {
    const response = await ceoApiClient.get('/api/v1/ceo/health', { timeout: 5000 });
    return {
      connected: true,
      status: response.data?.status || 'healthy',
      latency: response.config.metadata ? new Date() - response.config.metadata.startTime : null,
      backend_url: getBackendUrl()
    };
  } catch (error) {
    return {
      connected: false,
      status: 'error',
      error: error.message,
      latency: null,
      backend_url: getBackendUrl()
    };
  }
};

export default ceoApiClient; 
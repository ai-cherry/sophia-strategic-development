import axios from 'axios';

// Environment-aware backend URL configuration
const API_CONFIG = {
  production: 'https://api.sophia-intel.ai',
  development: 'http://localhost:8000', // Updated to match backend port
  timeout: 10000,
  retries: 3,
  retryDelay: 1000
};

const getBaseURL = () => {
  const isDevelopment = process.env.NODE_ENV === 'development' ||
                       window.location.hostname === 'localhost' ||
                       window.location.hostname === '127.0.0.1';
  return isDevelopment ? API_CONFIG.development : API_CONFIG.production;
};

// Create clean axios instance
const apiClient = axios.create({
  baseURL: getBaseURL(),
  timeout: API_CONFIG.timeout,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Interceptors for logging and error handling
apiClient.interceptors.request.use(
  (config) => {
    config.metadata = { startTime: new Date() };
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ API Request Failed:', error);
        throw error; // Don't fallback to mock data
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  (response) => {
    const duration = new Date() - response.config.metadata.startTime;
    console.log(`✅ API Response: ${response.config.method?.toUpperCase()} ${response.config.url} (${duration}ms)`);
    return response;
  },
  (error) => {
    const duration = error.config?.metadata ? new Date() - error.config.metadata.startTime : 0;
    console.error(`❌ API Error: ${error.config?.method?.toUpperCase()} ${error.config?.url} (${duration}ms)`, error);
    return Promise.reject(error);
  }
);

// Enhanced API methods for Phase 2.3 and Phase 2.4 integration
const api = {
  // Health and status endpoints
  async getHealth() {
    const response = await apiClient.get('/health');
    return response.data;
  },

  // Chat endpoints
  async sendMessage(message, conversationId = null) {
    const response = await apiClient.post('/chat', {
      message,
      conversation_id: conversationId
    });
    return response.data;
  },

  // Phase 2.3 Cross-Component Integration endpoints
  async getIntegrationStatus() {
    try {
      const response = await apiClient.get('/api/integration/status');
      return response.data;
    } catch (error) {
        throw new Error("Backend API not available - check deployment");
    }
  },

  async executeIntegration(taskType, description, mode = 'executive_intelligence') {
    try {
      const response = await apiClient.post('/api/integration/execute', {
        task_type: taskType,
        description,
        mode
      });
      return response.data;
    } catch (error) {
        throw new Error("Backend API not available - check deployment");
    }
  },

  // Phase 2.4 Advanced AI Orchestration endpoints
  async getOrchestrationStatus() {
    try {
      const response = await apiClient.get('/api/orchestration/status');
      return response.data;
    } catch (error) {
        throw new Error("Backend API not available - check deployment");
    }
  },

  async executeAdvancedTask(taskType, description, complexity = 'moderate') {
    try {
      const response = await apiClient.post('/api/orchestration/execute', {
        task_type: taskType,
        description,
        complexity,
        priority: 1
      });
      return response.data;
    } catch (error) {
        throw new Error("Backend API not available - check deployment");
    }
  },

  // Executive Intelligence endpoints
  async getExecutiveIntelligence() {
    try {
      const response = await apiClient.get('/api/executive/intelligence');
      return response.data;
    } catch (error) {
        throw new Error("Backend API not available - check deployment");
    }
  },

  // Performance metrics endpoints
  async getPerformanceMetrics() {
    try {
      const response = await apiClient.get('/api/performance/metrics');
      return response.data;
    } catch (error) {
        throw new Error("Backend API not available - check deployment");
    }
  },

  // Workflow automation endpoints
  async getWorkflowStatus() {
    try {
      const response = await apiClient.get('/api/workflows/status');
      return response.data;
    } catch (error) {
        throw new Error("Backend API not available - check deployment");
    }
  },

  // Memory system endpoints (existing functionality)
  async searchMemory(query, limit = 10) {
    try {
      const response = await apiClient.post('/api/memory/search', {
        query,
        limit
      });
      return response.data;
    } catch (error) {
        throw new Error("Backend API not available - check deployment");
    }
  },

  async getCacheMetrics() {
    try {
      const response = await apiClient.get('/api/memory/cache/metrics');
      return response.data;
    } catch (error) {
        throw new Error("Backend API not available - check deployment");
    }
  },

  async getMemoryStats() {
    try {
      const response = await apiClient.get('/api/memory/stats');
      return response.data;
    } catch (error) {
        throw new Error("Backend API not available - check deployment");
    }
  }
};

export default api;

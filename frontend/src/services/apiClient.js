import axios from 'axios';

// Environment-aware backend URL configuration
const API_CONFIG = {
  production: 'https://api.sophia-intel.ai',
  development: 'http://localhost:8000',
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
    console.error('❌ Request Error:', error);
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

export default apiClient; 
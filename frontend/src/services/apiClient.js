import axios from 'axios';

// Environment-aware API URL configuration
const getApiUrl = () => {
  // React environment variables (prefixed with REACT_APP_) for Vercel compatibility
  // Also support Vite environment variables (prefixed with VITE_) for local development
  const apiUrl = process.env.REACT_APP_API_URL || import.meta.env.VITE_API_URL;
  const environment = process.env.REACT_APP_ENVIRONMENT || import.meta.env.VITE_ENVIRONMENT || import.meta.env.MODE || process.env.NODE_ENV;
  
  if (apiUrl) {
    return apiUrl;
  }
  
  // Fallback URLs based on environment
  switch (environment) {
    case 'production':
      return 'https://api.sophia.payready.com';
    case 'staging':
      return 'https://api.staging.sophia.payready.com';
    case 'development':
    case 'dev':
      return 'https://api.dev.sophia.payready.com';
    default:
      // Local development fallback
      return 'http://localhost:8000/api/v1';
  }
};

const apiClient = axios.create({
  baseURL: getApiUrl(),
  timeout: 30000, // 30 second timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for authentication
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add environment context header
    const environment = process.env.REACT_APP_ENVIRONMENT || import.meta.env.VITE_ENVIRONMENT || import.meta.env.MODE || process.env.NODE_ENV;
    config.headers['X-Environment'] = environment;
    
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', {
      message: error.message,
      status: error.response?.status,
      data: error.response?.data,
      url: error.config?.url,
    });
    
    // Handle authentication errors
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      // Optionally redirect to login
      window.location.href = '/login';
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;

export const fetchAgnoPerformanceMetrics = async () => {
  const response = await apiClient.get('/metrics/agno-performance');
  return response.data;
};

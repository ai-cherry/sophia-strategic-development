// Environment-aware API URL configuration
const getApiUrl = () => {
  // Vite environment variables (prefixed with VITE_) for Vercel compatibility
  const apiUrl = import.meta.env.VITE_API_URL;
  const environment = import.meta.env.VITE_ENVIRONMENT || import.meta.env.MODE || process.env.NODE_ENV;
  
  if (apiUrl) {
    return `${apiUrl}/api/v1`;
  }
  
  // Fallback URLs based on environment
  switch (environment) {
    case 'production':
      return 'https://api.sophia.payready.com/api/v1';
    case 'staging':
      return 'https://api.staging.sophia.payready.com/api/v1';
    case 'development':
    case 'dev':
      return 'https://api.dev.sophia.payready.com/api/v1';
    default:
      // Local development fallback
      return 'http://localhost:8000/api/v1';
  }
};

const API_BASE_URL = getApiUrl();
const API_KEY = import.meta.env.VITE_API_KEY || 'sophia-dashboard-dev-key'; // Environment-specific API key

const request = async (endpoint, options = {}) => {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = {
        'Content-Type': 'application/json',
        'X-API-KEY': API_KEY,
        'X-Environment': import.meta.env.VITE_ENVIRONMENT || import.meta.env.MODE || process.env.NODE_ENV,
        ...options.headers,
    };

    const config = {
        ...options,
        headers,
    };

    try {
        const response = await fetch(url, config);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API call failed:', {
            url,
            error: error.message,
            environment: import.meta.env.VITE_ENVIRONMENT || import.meta.env.MODE || process.env.NODE_ENV
        });
        throw error;
    }
};

export const getDashboardMetrics = () => {
    return request('/dashboard/metrics');
};

export const getCEOMetrics = (timeRange = '30d') => {
    return request(`/dashboard/ceo/metrics?timeRange=${timeRange}`);
};

export const getKnowledgeStats = () => {
    return request('/dashboard/knowledge/stats');
};

export const getProjectOverview = () => {
    return request('/dashboard/project/overview');
};

export const querySnowflake = (query) => {
    return request(`/data/snowflake/query?query=${encodeURIComponent(query)}`);
};

export const getAIInsights = (data) => {
    return request('/ai/insights', {
        method: 'POST',
        body: JSON.stringify(data),
    });
};

export const getHealth = () => {
    return request('/health');
};

export const sendChatMessage = (message, context = {}) => {
    return request('/chat/message', {
        method: 'POST',
        body: JSON.stringify({ message, context }),
    });
};

export const executeAction = (action, context = {}) => {
    return request('/chat/action', {
        method: 'POST',
        body: JSON.stringify({ action, context }),
    });
};

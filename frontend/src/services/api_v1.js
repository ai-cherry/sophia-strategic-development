const API_BASE_URL = 'http://localhost:8000/api/v1'; // This should be in an env file
const API_KEY = 'sophia-dashboard-prod-key'; // This should be stored securely

const request = async (endpoint, options = {}) => {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = {
        'Content-Type': 'application/json',
        'X-API-KEY': API_KEY,
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
        console.error('API call failed:', error);
        throw error;
    }
};

export const getDashboardMetrics = () => {
    return request('/dashboard/metrics');
};

export const getSalesCalls = () => {
    return request('/sales/calls');
};

export const getSalesAnalytics = () => {
    return request('/sales/analytics');
};

export const getSlackInsights = () => {
    return request('/communications/slack');
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

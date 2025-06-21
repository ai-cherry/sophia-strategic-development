import apiClient from './apiClient.js';

class ApiService {
  async request(method, endpoint, data = null, config = {}) {
    const response = await apiClient({ url: endpoint, method, data, ...config });
    return response.data;
  }

  async login(email, password) {
    const data = await this.request('post', '/auth/login', { email, password });
    if (data.token) {
      localStorage.setItem('auth_token', data.token);
    }
    return data;
  }

  async logout() {
    localStorage.removeItem('auth_token');
  }

  // Company Metrics
  getCompanyMetrics() {
    return this.request('get', '/company/metrics');
  }

  getDashboardMetrics() {
    return this.request('get', '/dashboard/metrics');
  }

  getRevenueData(period = 'monthly') {
    return this.request('get', `/company/revenue?period=${period}`);
  }

  getCustomerMetrics() {
    return this.request('get', '/company/customers');
  }

  getHealthScore() {
    return this.request('get', '/company/health-score');
  }

  // Strategy
  getStrategyInsights() {
    return this.request('get', '/strategy/insights');
  }

  getGrowthOpportunities() {
    return this.request('get', '/strategy/growth-opportunities');
  }

  getMarketAnalysis() {
    return this.request('get', '/strategy/market-analysis');
  }

  // Operations
  getOperationalMetrics() {
    return this.request('get', '/operations/metrics');
  }

  getWorkflows() {
    return this.request('get', '/operations/workflows');
  }

  getSystemStatus() {
    return this.request('get', '/operations/status');
  }

  // AI Insights
  getAIInsights() {
    return this.request('get', '/ai/insights');
  }

  getPredictions() {
    return this.request('get', '/ai/predictions');
  }

  getRecommendations() {
    return this.request('get', '/ai/recommendations');
  }

  // Property Management
  getPropertyData() {
    return this.request('get', '/property/units');
  }

  searchUnits(filters) {
    return this.request('post', '/property/search', filters);
  }

  // Knowledge Base
  searchKnowledge(query) {
    return this.request('post', '/knowledge/search', { query });
  }

  getKnowledgeStats() {
    return this.request('get', '/knowledge/stats');
  }
}

export default new ApiService();

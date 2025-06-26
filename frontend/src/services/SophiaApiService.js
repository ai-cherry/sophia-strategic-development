/**
 * Sophia AI API Service
 * Unified service for all API communication with enhanced dashboard integration
 */

class SophiaApiService {
  constructor() {
    // Environment-aware configuration
    this.baseURL = this.getApiBaseUrl();
    this.wsURL = this.getWebSocketUrl();
    
    console.log('Sophia API Service initialized:', {
      apiUrl: this.baseURL,
      wsUrl: this.wsURL
    });
  }

  getApiBaseUrl() {
    // React environment variables for production deployment
    const apiUrl = process.env.REACT_APP_API_URL || 
                   process.env.VITE_API_URL ||
                   'http://localhost:8000';
    return apiUrl;
  }

  getWebSocketUrl() {
    // WebSocket URL configuration
    const wsUrl = process.env.REACT_APP_WS_URL || 
                  process.env.VITE_WS_URL;
    
    if (wsUrl) return wsUrl;
    
    // Convert HTTP URL to WebSocket URL
    const baseUrl = this.getApiBaseUrl();
    return baseUrl.replace(/^https?:/, baseUrl.startsWith('https:') ? 'wss:' : 'ws:');
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }

      return response.json();
    } catch (error) {
      console.error('API Request failed:', error);
      throw error;
    }
  }

  // ============================================================================
  // CHAT & WEBSOCKET INTEGRATION
  // ============================================================================

  createWebSocketConnection(userId = 'ceo', sessionId = null) {
    const connectionId = sessionId || `${userId}_${Date.now()}`;
    const wsUrl = `${this.wsURL}/api/v1/sophia/chat/ws/${connectionId}?user_id=${userId}`;
    
    console.log('Creating WebSocket connection:', wsUrl);
    return new WebSocket(wsUrl);
  }

  async createChatSession(userId = 'ceo', dashboardType = 'executive') {
    return this.request('/api/v1/sophia/chat/sessions', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        dashboard_type: dashboardType,
        session_title: `${dashboardType.charAt(0).toUpperCase() + dashboardType.slice(1)} Session`
      })
    });
  }

  async getSessionMessages(sessionId) {
    return this.request(`/api/v1/sophia/chat/sessions/${sessionId}/messages`);
  }

  async getChatPersonalities() {
    return this.request('/api/v1/sophia/chat/personalities');
  }

  async getSearchContexts() {
    return this.request('/api/v1/sophia/search/contexts');
  }

  async getUserProfile(userId) {
    return this.request(`/api/v1/sophia/users/${userId}`);
  }

  // ============================================================================
  // KNOWLEDGE BASE INTEGRATION
  // ============================================================================

  async uploadFile(file, userId = 'ceo', categoryId = 'general', onProgress = null) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', userId);
    formData.append('category_id', categoryId);

    const xhr = new XMLHttpRequest();
    
    return new Promise((resolve, reject) => {
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable && onProgress) {
          const percentComplete = (event.loaded / event.total) * 100;
          onProgress(percentComplete);
        }
      });

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response = JSON.parse(xhr.responseText);
            resolve(response);
          } catch (error) {
            reject(new Error('Invalid JSON response'));
          }
        } else {
          reject(new Error(`Upload failed: ${xhr.status} ${xhr.statusText}`));
        }
      });

      xhr.addEventListener('error', () => {
        reject(new Error('Upload failed: Network error'));
      });

      xhr.open('POST', `${this.baseURL}/api/knowledge/upload`);
      xhr.send(formData);
    });
  }

  async searchKnowledge(query, limit = 10, categoryId = null) {
    const params = new URLSearchParams({
      query,
      limit: limit.toString()
    });
    
    if (categoryId) {
      params.append('category_id', categoryId);
    }
    
    return this.request(`/api/knowledge/search?${params}`);
  }

  async getKnowledgeCategories() {
    return this.request('/api/knowledge/categories');
  }

  async getKnowledgeStats() {
    return this.request('/api/knowledge/stats');
  }

  // ============================================================================
  // DASHBOARD DATA INTEGRATION
  // ============================================================================

  async getDashboardMetrics(dashboardType = 'executive') {
    return this.request(`/api/dashboard/${dashboardType}/metrics`);
  }

  async getExecutiveKPIs() {
    return this.request('/api/dashboard/executive/kpis');
  }

  async getRecentActivity(limit = 10) {
    return this.request(`/api/dashboard/activity?limit=${limit}`);
  }

  async getAIInsights(dashboardType = 'executive') {
    return this.request(`/api/dashboard/${dashboardType}/insights`);
  }

  async getNotifications(userId = 'ceo') {
    return this.request(`/api/notifications?user_id=${userId}`);
  }

  async markNotificationRead(notificationId) {
    return this.request(`/api/notifications/${notificationId}/read`, {
      method: 'POST'
    });
  }

  // ============================================================================
  // INTEGRATION APIS
  // ============================================================================

  async getLinearProjects() {
    return this.request('/api/integrations/linear/projects');
  }

  async getLinearIssues(projectId = null) {
    const params = projectId ? `?project_id=${projectId}` : '';
    return this.request(`/api/integrations/linear/issues${params}`);
  }

  async getAsanaProjects() {
    return this.request('/api/integrations/asana/projects');
  }

  async getGongCalls(limit = 10) {
    return this.request(`/api/integrations/gong/calls?limit=${limit}`);
  }

  async getHubSpotDeals() {
    return this.request('/api/integrations/hubspot/deals');
  }

  // ============================================================================
  // HEALTH & MONITORING
  // ============================================================================

  async getHealth() {
    return this.request('/health');
  }

  async getDetailedHealth() {
    return this.request('/health/detailed');
  }

  async getSystemStatus() {
    return this.request('/api/system/status');
  }

  // ============================================================================
  // UTILITY METHODS
  // ============================================================================

  isHealthy(healthResponse) {
    return healthResponse && healthResponse.status === 'healthy';
  }

  formatError(error) {
    if (error.response && error.response.data) {
      return error.response.data.message || error.response.data.detail || 'API Error';
    }
    return error.message || 'Unknown error occurred';
  }
}

// Create singleton instance
const sophiaApiService = new SophiaApiService();

export default sophiaApiService; 
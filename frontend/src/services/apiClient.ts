/**
 * API Client for Sophia AI Frontend
 * GPU-accelerated memory operations with Weaviate/Redis/PostgreSQL
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiClient {
  private getAuthToken(): string | null {
    return localStorage.getItem('esc_token');
  }

  private async request(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<any> {
    const token = this.getAuthToken();
    
    const response = await fetch(`${API_BASE}/api${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Request failed' }));
      throw new Error(error.message || `HTTP ${response.status}`);
    }

    return response.json();
  }

  async post(endpoint: string, data: any): Promise<any> {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async get(endpoint: string): Promise<any> {
    return this.request(endpoint, {
      method: 'GET',
    });
  }

  // Memory Operations (GPU-accelerated)
  async searchMemory(query: string, limit: number = 10): Promise<any> {
    return this.post('/v2/memory/search_knowledge', { query, limit });
  }

  async addMemory(content: string, category: string, metadata?: any): Promise<any> {
    return this.post('/v2/memory/add_knowledge', {
      content,
      category,
      metadata,
    });
  }

  async getMemoryStats(): Promise<any> {
    return this.get('/v2/memory/stats');
  }

  // Cache Metrics
  async getCacheMetrics(): Promise<any> {
    return this.get('/v2/metrics/cache');
  }

  // Chat Operations
  async sendMessage(message: string, sessionId: string): Promise<any> {
    return this.post('/v4/orchestrate', {
      query: message,
      user_id: 'ceo_user',
      session_id: sessionId,
    });
  }

  // System Status
  async getSystemStatus(): Promise<any> {
    return this.get('/v4/system/status');
  }

  // MCP Server Operations
  async getMCPServerStatus(): Promise<any> {
    return this.get('/v2/mcp/status');
  }

  async invokeMCPTool(server: string, tool: string, args: any): Promise<any> {
    return this.post(`/v2/mcp/${server}/tool`, {
      name: tool,
      arguments: args,
    });
  }

  // Analytics Operations
  async getProjectAnalytics(): Promise<any> {
    return this.get('/v2/analytics/projects');
  }

  async getTeamAnalytics(): Promise<any> {
    return this.get('/v2/analytics/team');
  }

  async getSalesAnalytics(): Promise<any> {
    return this.get('/v2/analytics/sales');
  }

  // Gong Integration
  async searchCallTranscripts(query: string): Promise<any> {
    return this.invokeMCPTool('gong', 'search_call_memory', { query, limit: 5 });
  }

  // HubSpot Integration
  async getDeals(status?: string): Promise<any> {
    return this.invokeMCPTool('hubspot_unified', 'list_deals', { status });
  }

  // Linear Integration
  async getActiveProjects(): Promise<any> {
    return this.invokeMCPTool('linear', 'list_projects', { status: 'active' });
  }
}

const apiClient = new ApiClient();
export default apiClient; 
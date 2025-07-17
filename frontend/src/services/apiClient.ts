/**
 * Unified API Client for Sophia AI Executive Dashboard
 * Provides consistent interface for all backend communications
 */

// 🔧 CRITICAL FIX: Import unified environment configuration
import { getBaseURL, getWebSocketURL } from '../config/environment';

interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  status: number;
}

class ApiClient {
  private baseURL: string;
  
  constructor() {
    // 🔧 CRITICAL FIX: Use unified environment configuration
    this.baseURL = getBaseURL();
  }

  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      const data = await response.json();
      
      return {
        data,
        status: response.status,
      };
    } catch (error) {
      console.error(`API Error for ${endpoint}:`, error);
      return {
        error: error instanceof Error ? error.message : 'Unknown error',
        status: 500,
      };
    }
  }

  // Core API methods
  async get<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  async post<T>(endpoint: string, data: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async put<T>(endpoint: string, data: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }

  // Specialized methods for Sophia AI
  async chat(message: string): Promise<ApiResponse<any>> {
    return this.post('/chat', { message });
  }

  async getHealth(): Promise<ApiResponse<any>> {
    return this.get('/health');
  }

  async getSystemStatus(): Promise<ApiResponse<any>> {
    return this.get('/system/status');
  }

  async getMetrics(): Promise<ApiResponse<any>> {
    return this.get('/metrics');
  }

  // Intelligence endpoints
  async getBusinessIntelligence(): Promise<ApiResponse<any>> {
    return this.get('/api/v1/intelligence/business');
  }

  async getMemoryInsights(): Promise<ApiResponse<any>> {
    return this.get('/api/v1/memory/insights');
  }

  async getTemporalLearning(): Promise<ApiResponse<any>> {
    return this.get('/api/v1/temporal-learning/dashboard/data');
  }

  async getLambdaLabsStatus(): Promise<ApiResponse<any>> {
    return this.get('/api/v1/lambda-labs/status');
  }

  async getDeploymentStatus(): Promise<ApiResponse<any>> {
    return this.get('/api/v1/deployment/status');
  }

  async getAIMemoryHealth(): Promise<ApiResponse<any>> {
    return this.get('/api/v1/ai-memory/health');
  }

  async getCompetitorIntelligence(): Promise<ApiResponse<any>> {
    return this.get('/api/v1/competitor-intelligence');
  }

  async getExternalIntelligence(): Promise<ApiResponse<any>> {
    return this.get('/api/v1/external-intelligence');
  }

  // WebSocket connection helper
  createWebSocket(path: string = '/ws'): WebSocket {
    // 🔧 CRITICAL FIX: Use unified WebSocket URL configuration
    return new WebSocket(getWebSocketURL());
  }
}

// Export singleton instance
const apiClient = new ApiClient();
export default apiClient;

// Export types for use in components
export type { ApiResponse }; 
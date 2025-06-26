/**
 * Enhanced Sophia AI API Client
 * Handles all API communication with robust error handling and user-friendly error messages
 */

class SophiaApiService {
  constructor() {
    // Environment-aware API configuration
    this.baseURL = this.getApiUrl();
    this.wsUrl = this.getWsUrl();
    this.retryAttempts = 3;
    this.retryDelay = 1000; // 1 second
  }

  getApiUrl() {
    // Production vs Development URL handling
    if (window.location.hostname === 'app.sophia-intel.ai') {
      return 'https://api.sophia-intel.ai';
    }
    
    // Check environment variables
    const envApiUrl = process.env.REACT_APP_API_URL || process.env.VITE_API_URL;
    if (envApiUrl) {
      return envApiUrl;
    }
    
    // Default fallback
    return window.location.hostname === 'localhost' 
      ? 'http://localhost:8000' 
      : 'https://api.sophia-intel.ai';
  }

  getWsUrl() {
    const apiUrl = this.getApiUrl();
    return apiUrl.replace('http://', 'ws://').replace('https://', 'wss://');
  }

  /**
   * Enhanced fetch with comprehensive error handling
   */
  async enhancedFetch(url, options = {}) {
    const fullUrl = url.startsWith('http') ? url : `${this.baseURL}${url}`;
    
    // Default headers
    const defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };

    const config = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers
      }
    };

    for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
      try {
        const response = await fetch(fullUrl, config);
        
        // Check if response is OK
        if (!response.ok) {
          const error = await this.handleErrorResponse(response);
          throw error;
        }

        // Check content type
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
          console.error('Non-JSON response received:', {
            url: fullUrl,
            status: response.status,
            contentType,
            headers: Object.fromEntries(response.headers.entries())
          });
          
          // Log to backend error monitoring
          this.logError('non_json_response', {
            url: fullUrl,
            status: response.status,
            contentType
          });
          
          throw new Error('Service temporarily unavailable. Please try again later.');
        }

        // Parse JSON safely
        try {
          const data = await response.json();
          return data;
        } catch (parseError) {
          console.error('JSON parsing failed:', parseError);
          this.logError('json_parse_error', { url: fullUrl, error: parseError.message });
          throw new Error('Invalid response format. Please try again later.');
        }

      } catch (error) {
        // If it's our last attempt, throw the error
        if (attempt === this.retryAttempts) {
          // Log comprehensive error details
          console.error('API call failed after all retries:', {
            url: fullUrl,
            attempt,
            error: error.message,
            stack: error.stack
          });
          
          this.logError('api_call_failed', {
            url: fullUrl,
            attempts: this.retryAttempts,
            error: error.message
          });
          
          throw error;
        }
        
        // Wait before retrying
        await new Promise(resolve => setTimeout(resolve, this.retryDelay * attempt));
      }
    }
  }

  /**
   * Handle error responses with user-friendly messages
   */
  async handleErrorResponse(response) {
    let errorMessage = 'An unexpected error occurred. Please try again later.';
    let errorDetails = {};

    try {
      const errorData = await response.text();
      
      // Try to parse as JSON first
      try {
        const jsonError = JSON.parse(errorData);
        errorMessage = jsonError.detail || jsonError.message || errorMessage;
        errorDetails = jsonError;
      } catch {
        // If not JSON, check if it's HTML (common backend error)
        if (errorData.includes('<html>') || errorData.includes('<!DOCTYPE')) {
          console.error('Backend returned HTML instead of JSON:', {
            status: response.status,
            url: response.url,
            html: errorData.substring(0, 500)
          });
          errorMessage = 'Service configuration error. Please contact support.';
        } else {
          errorMessage = errorData || errorMessage;
        }
      }
    } catch {
      // Fallback for cases where we can't read the response
      errorMessage = `Service error (${response.status}). Please try again later.`;
    }

    // Create user-friendly error messages based on status code
    switch (response.status) {
      case 401:
        errorMessage = 'Authentication required. Please refresh the page.';
        break;
      case 403:
        errorMessage = 'Access denied. Please check your permissions.';
        break;
      case 404:
        errorMessage = 'Requested data not found.';
        break;
      case 429:
        errorMessage = 'Too many requests. Please wait a moment and try again.';
        break;
      case 500:
        errorMessage = 'Server error. Our team has been notified.';
        break;
      case 502:
      case 503:
      case 504:
        errorMessage = 'Service temporarily unavailable. Please try again in a few minutes.';
        break;
    }

    const error = new Error(errorMessage);
    error.status = response.status;
    error.details = errorDetails;
    return error;
  }

  /**
   * Log errors to backend monitoring
   */
  async logError(errorType, details) {
    try {
      // Don't use enhancedFetch here to avoid infinite loops
      await fetch(`${this.baseURL}/api/v1/monitoring/error`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          error_type: errorType,
          timestamp: new Date().toISOString(),
          user_agent: navigator.userAgent,
          url: window.location.href,
          details
        })
      });
    } catch (logError) {
      // Silently fail - don't break the main application
      console.warn('Failed to log error to backend:', logError);
    }
  }

  // ============================================================================
  // HEALTH & SYSTEM APIs
  // ============================================================================

  async healthCheck() {
    try {
      const data = await this.enhancedFetch('/health');
      return { success: true, data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  // ============================================================================
  // CEO DASHBOARD APIs
  // ============================================================================

  async getCEODashboardData(timeRange = '30d') {
    try {
      const data = await this.enhancedFetch(`/api/v1/ceo/dashboard?time_range=${timeRange}`);
      return { success: true, data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async getCEOKPIs(timeRange = '30d') {
    try {
      const data = await this.enhancedFetch(`/api/v1/ceo/kpis?time_range=${timeRange}`);
      return { success: true, data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async getCEOMetrics(timeRange = '30d', metrics = []) {
    try {
      const queryParams = new URLSearchParams({
        time_range: timeRange,
        metrics: metrics.join(',')
      });
      const data = await this.enhancedFetch(`/api/v1/ceo/metrics?${queryParams}`);
      return { success: true, data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async searchCEODashboard(query, timeRange = '30d') {
    try {
      const data = await this.enhancedFetch('/api/v1/ceo/search', {
        method: 'POST',
        body: JSON.stringify({
          query,
          time_range: timeRange,
          scope: 'dashboard'
        })
      });
      return { success: true, data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async getTeamPerformance(timeRange = '30d') {
    try {
      const data = await this.enhancedFetch(`/api/v1/ceo/team-performance?time_range=${timeRange}`);
      return { success: true, data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async getMarketData(timeRange = '30d') {
    try {
      const data = await this.enhancedFetch(`/api/v1/ceo/market-data?time_range=${timeRange}`);
      return { success: true, data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  // ============================================================================
  // CHAT & WEBSOCKET APIs
  // ============================================================================

  async sendChatMessage(message, userId = 'ceo_user', sessionId = null) {
    try {
      const data = await this.enhancedFetch('/api/v1/chat/message', {
        method: 'POST',
        body: JSON.stringify({
          message,
          user_id: userId,
          session_id: sessionId,
          context: 'ceo_dashboard'
        })
      });
      return { success: true, data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  /**
   * Enhanced WebSocket connection with robust error handling and reconnection
   */
  createWebSocketConnection(userId, onMessage, onError, onClose, onOpen) {
    const wsUrl = `${this.wsUrl}/ws/chat/${userId}`;
    let ws = null;
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 5;
    const reconnectDelay = 1000; // Start with 1 second
    let isIntentionallyClosed = false;

    const connect = () => {
      try {
        console.log(`Attempting WebSocket connection to: ${wsUrl}`);
        ws = new WebSocket(wsUrl);

        ws.onopen = (event) => {
          console.log('WebSocket connected successfully');
          reconnectAttempts = 0; // Reset on successful connection
          if (onOpen) onOpen(event);
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            onMessage(data);
          } catch (parseError) {
            console.error('Failed to parse WebSocket message:', parseError);
            // Send a user-friendly error through the message handler
            onMessage({
              type: 'error',
              content: 'Received invalid message format',
              timestamp: new Date().toISOString()
            });
          }
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.logError('websocket_error', {
            url: wsUrl,
            reconnectAttempts,
            error: error.message || 'Unknown WebSocket error'
          });
          if (onError) onError(error);
        };

        ws.onclose = (event) => {
          console.log('WebSocket closed:', event.code, event.reason);
          
          if (onClose) onClose(event);

          // Only attempt to reconnect if not intentionally closed and within retry limits
          if (!isIntentionallyClosed && reconnectAttempts < maxReconnectAttempts) {
            reconnectAttempts++;
            const delay = reconnectDelay * Math.pow(2, reconnectAttempts - 1); // Exponential backoff
            
            console.log(`Attempting to reconnect in ${delay}ms (attempt ${reconnectAttempts}/${maxReconnectAttempts})`);
            
            setTimeout(() => {
              if (!isIntentionallyClosed) {
                connect();
              }
            }, delay);
          } else if (reconnectAttempts >= maxReconnectAttempts) {
            console.error('Max reconnection attempts reached');
            if (onError) {
              onError(new Error('Connection lost. Please refresh the page to reconnect.'));
            }
          }
        };

      } catch (connectionError) {
        console.error('Failed to create WebSocket connection:', connectionError);
        this.logError('websocket_connection_failed', {
          url: wsUrl,
          error: connectionError.message
        });
        if (onError) onError(connectionError);
      }
    };

    // Initial connection
    connect();

    // Return control object
    return {
      send: (data) => {
        if (ws && ws.readyState === WebSocket.OPEN) {
          ws.send(typeof data === 'string' ? data : JSON.stringify(data));
          return true;
        } else {
          console.warn('WebSocket not connected, message not sent:', data);
          return false;
        }
      },
      close: () => {
        isIntentionallyClosed = true;
        if (ws) {
          ws.close();
        }
      },
      getReadyState: () => ws ? ws.readyState : WebSocket.CLOSED,
      reconnect: () => {
        if (isIntentionallyClosed) {
          isIntentionallyClosed = false;
          reconnectAttempts = 0;
          connect();
        }
      }
    };
  }

  // ============================================================================
  // FILE UPLOAD APIs
  // ============================================================================

  async uploadFile(file, type = 'document', context = 'ceo_dashboard') {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('type', type);
      formData.append('context', context);

      // Don't set Content-Type header for FormData - let browser set it
      const data = await this.enhancedFetch('/api/v1/knowledge/upload', {
        method: 'POST',
        headers: {}, // Remove default JSON headers for file upload
        body: formData
      });
      
      return { success: true, data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  // ============================================================================
  // PROJECT MANAGEMENT APIs
  // ============================================================================

  async getLinearProjects(teamId = null, state = null) {
    try {
      const queryParams = new URLSearchParams();
      if (teamId) queryParams.append('team_id', teamId);
      if (state) queryParams.append('state', state);
      
      const data = await this.enhancedFetch(`/api/v1/integrations/linear/projects?${queryParams}`);
      return { success: true, data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async getLinearHealth() {
    try {
      const data = await this.enhancedFetch('/api/v1/integrations/linear/health');
      return { success: true, data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }
}

// Export singleton instance
const apiClient = new SophiaApiService();
export default apiClient;

export const fetchAgnoPerformanceMetrics = async () => {
  const response = await apiClient.get('/metrics/agno-performance');
  return response.data;
};


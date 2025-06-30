/**
 * MCP Integration Service
 * Bridges the unified dashboard and chat components with the MCP ecosystem
 * Created: July 2025 - Strategic Plan Enhancement
 */

import apiClient from './apiClient.js';

class MCPIntegrationService {
  constructor() {
    this.mcpEndpoints = {
      orchestrator: '/api/mcp/sophia_ai_orchestrator',
      memory: '/api/mcp/enhanced_ai_memory',
      portkey: '/api/mcp/portkey_gateway',
      codeIntel: '/api/mcp/code_intelligence',
      businessIntel: '/api/mcp/business_intelligence',
      playwright: '/api/mcp/microsoft_playwright_official',
      figma: '/api/mcp/glips_figma_context_official',
      portkeyAdmin: '/api/mcp/portkey_admin_official',
      openrouter: '/api/mcp/openrouter_search_official'
    };
    
    this.isConnected = false;
    this.availableServices = new Set();
  }

  /**
   * Initialize MCP connections and check service availability
   */
  async initialize() {
    try {
      const healthChecks = await Promise.allSettled(
        Object.entries(this.mcpEndpoints).map(async ([service, endpoint]) => {
          try {
            const response = await apiClient.get(`${endpoint}/health`);
            if (response.data.status === 'healthy') {
              this.availableServices.add(service);
              return { service, status: 'available' };
            }
          } catch (error) {
            return { service, status: 'unavailable', error: error.message };
          }
        })
      );

      this.isConnected = this.availableServices.size > 0;
      
      console.log(`MCP Integration: ${this.availableServices.size} services available`, 
                  Array.from(this.availableServices));
      
      return {
        connected: this.isConnected,
        services: Array.from(this.availableServices),
        total: this.availableServices.size
      };
    } catch (error) {
      console.error('MCP Integration initialization failed:', error);
      return { connected: false, services: [], total: 0, error: error.message };
    }
  }

  /**
   * Enhanced chat processing with MCP orchestration
   */
  async processChat(message, mode = 'universal', sessionId = null) {
    if (!this.isConnected) {
      // Fallback to standard API if MCP not available
      return apiClient.chat.sendMessage(message, mode, sessionId);
    }

    try {
      // Route through MCP orchestrator for enhanced processing
      const mcpRequest = {
        message,
        mode,
        sessionId,
        mcpServices: {
          orchestrator: this.availableServices.has('orchestrator'),
          memory: this.availableServices.has('memory'),
          businessIntel: this.availableServices.has('businessIntel')
        },
        enhancedFeatures: {
          contextAware: true,
          costOptimized: this.availableServices.has('portkeyAdmin'),
          multiProvider: this.availableServices.has('openrouter')
        }
      };

      const response = await apiClient.post('/api/v1/chat/mcp-enhanced', mcpRequest);
      
      // Track MCP usage for dashboard analytics
      this.trackMCPUsage(mode, response.data.mcpMetrics);
      
      return response.data;
    } catch (error) {
      console.warn('MCP-enhanced chat failed, falling back to standard:', error);
      return apiClient.chat.sendMessage(message, mode, sessionId);
    }
  }

  /**
   * Get enhanced dashboard metrics using MCP services
   */
  async getEnhancedDashboardMetrics() {
    const metrics = {
      standard: await apiClient.dashboard.getMetrics(),
      mcp: {
        available: this.isConnected,
        services: this.availableServices.size,
        enhanced: {}
      }
    };

    if (!this.isConnected) return metrics;

    try {
      // Enhanced cost analysis via Portkey Admin
      if (this.availableServices.has('portkeyAdmin')) {
        const costData = await apiClient.get(this.mcpEndpoints.portkeyAdmin + '/cost-analysis');
        metrics.mcp.enhanced.costOptimization = costData.data;
      }

      // Enhanced performance metrics via orchestrator
      if (this.availableServices.has('orchestrator')) {
        const perfData = await apiClient.get(this.mcpEndpoints.orchestrator + '/performance');
        metrics.mcp.enhanced.orchestratorMetrics = perfData.data;
      }

      // Business intelligence insights
      if (this.availableServices.has('businessIntel')) {
        const biData = await apiClient.get(this.mcpEndpoints.businessIntel + '/insights');
        metrics.mcp.enhanced.businessInsights = biData.data;
      }

      // Model diversity metrics via OpenRouter
      if (this.availableServices.has('openrouter')) {
        const modelData = await apiClient.get(this.mcpEndpoints.openrouter + '/model-usage');
        metrics.mcp.enhanced.modelDiversity = modelData.data;
      }

    } catch (error) {
      console.warn('Enhanced metrics collection failed:', error);
      metrics.mcp.error = error.message;
    }

    return metrics;
  }

  /**
   * Get Agno performance with MCP enhancements
   */
  async getEnhancedAgnoMetrics() {
    const baseMetrics = await apiClient.agno.getPerformanceMetrics();
    
    if (!this.availableServices.has('memory') || !this.availableServices.has('orchestrator')) {
      return baseMetrics;
    }

    try {
      // Enhanced agent memory analysis
      const memoryInsights = await apiClient.get(this.mcpEndpoints.memory + '/agent-patterns');
      
      // Orchestrator performance optimization suggestions
      const optimizations = await apiClient.get(this.mcpEndpoints.orchestrator + '/agent-optimization');

      return {
        ...baseMetrics,
        mcpEnhanced: {
          memoryPatterns: memoryInsights.data,
          optimizationSuggestions: optimizations.data,
          enhancedAt: new Date().toISOString()
        }
      };
    } catch (error) {
      console.warn('Enhanced Agno metrics failed:', error);
      return baseMetrics;
    }
  }

  /**
   * Track MCP usage for analytics
   */
  trackMCPUsage(mode, metrics) {
    if (!metrics) return;
    
    // Store usage data for dashboard analytics
    const usage = {
      timestamp: new Date().toISOString(),
      mode,
      services: metrics.servicesUsed || [],
      performance: metrics.performance || {},
      cost: metrics.cost || {}
    };

    // Store in localStorage for dashboard display
    const existingUsage = JSON.parse(localStorage.getItem('mcpUsageData') || '[]');
    existingUsage.push(usage);
    
    // Keep only last 100 entries
    if (existingUsage.length > 100) {
      existingUsage.splice(0, existingUsage.length - 100);
    }
    
    localStorage.setItem('mcpUsageData', JSON.stringify(existingUsage));
  }

  /**
   * Get MCP usage analytics for dashboard
   */
  getMCPAnalytics() {
    const usage = JSON.parse(localStorage.getItem('mcpUsageData') || '[]');
    
    if (usage.length === 0) {
      return {
        totalRequests: 0,
        servicesUsed: [],
        averageResponseTime: 0,
        costSavings: 0
      };
    }

    const analytics = {
      totalRequests: usage.length,
      servicesUsed: [...new Set(usage.flatMap(u => u.services))],
      averageResponseTime: usage.reduce((sum, u) => sum + (u.performance.responseTime || 0), 0) / usage.length,
      costSavings: usage.reduce((sum, u) => sum + (u.cost.savings || 0), 0),
      lastHour: usage.filter(u => new Date() - new Date(u.timestamp) < 3600000).length
    };

    return analytics;
  }

  /**
   * Check if specific MCP service is available
   */
  isServiceAvailable(serviceName) {
    return this.availableServices.has(serviceName);
  }

  /**
   * Get connection status
   */
  getConnectionStatus() {
    return {
      connected: this.isConnected,
      services: Array.from(this.availableServices),
      total: this.availableServices.size,
      endpoints: this.mcpEndpoints
    };
  }
}

// Create singleton instance
const mcpIntegration = new MCPIntegrationService();

// Auto-initialize when imported
mcpIntegration.initialize().catch(console.error);

export default mcpIntegration;


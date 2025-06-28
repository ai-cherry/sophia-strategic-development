/**
 * Environment Configuration for Sophia AI Frontend
 * Centralized configuration management for all environment variables
 */

// Development defaults
const defaultConfig = {
  // Backend API Configuration
  backendUrl: 'http://localhost:8000',
  wsUrl: 'ws://localhost:8000',
  
  // Enhanced CEO Dashboard Configuration
  figmaPersonalAccessToken: null, // Set via VITE_FIGMA_PERSONAL_ACCESS_TOKEN
  figmaFileKey: null, // Set via VITE_FIGMA_FILE_KEY
  
  // Design System Configuration
  designSystemMode: 'production',
  glassmorphismEnabled: true,
  
  // Dashboard Feature Flags
  enableEnhancedDashboard: true,
  enableChartJsDashboard: true,
  enableFigmaIntegration: true,
  enableRealTimeCharts: true,
  
  // Analytics & Monitoring
  enablePerformanceMonitoring: true,
  analyticsEnabled: false,
  debugMode: false,
  
  // Security Configuration
  ceoAccessToken: process.env.REACT_APP_CEO_ACCESS_TOKEN || 'sophia_ceo_access_2024',
  adminMode: false,
  
  // Deployment Configuration
  deploymentEnv: 'development',
  buildVersion: '1.0.0'
};

/**
 * Get environment configuration with fallbacks
 */
function getEnvironmentConfig() {
  const config = { ...defaultConfig };
  
  // Backend Configuration
  if (import.meta.env.VITE_BACKEND_URL) {
    config.backendUrl = import.meta.env.VITE_BACKEND_URL;
  }
  
  if (import.meta.env.VITE_WS_URL) {
    config.wsUrl = import.meta.env.VITE_WS_URL;
  }
  
  // Figma Integration
  if (import.meta.env.VITE_FIGMA_PERSONAL_ACCESS_TOKEN) {
    config.figmaPersonalAccessToken = import.meta.env.VITE_FIGMA_PERSONAL_ACCESS_TOKEN;
  }
  
  if (import.meta.env.VITE_FIGMA_FILE_KEY) {
    config.figmaFileKey = import.meta.env.VITE_FIGMA_FILE_KEY;
  }
  
  // Design System
  if (import.meta.env.VITE_DESIGN_SYSTEM_MODE) {
    config.designSystemMode = import.meta.env.VITE_DESIGN_SYSTEM_MODE;
  }
  
  if (import.meta.env.VITE_GLASSMORPHISM_ENABLED !== undefined) {
    config.glassmorphismEnabled = import.meta.env.VITE_GLASSMORPHISM_ENABLED === 'true';
  }
  
  // Feature Flags
  if (import.meta.env.VITE_ENABLE_ENHANCED_DASHBOARD !== undefined) {
    config.enableEnhancedDashboard = import.meta.env.VITE_ENABLE_ENHANCED_DASHBOARD === 'true';
  }
  
  if (import.meta.env.VITE_ENABLE_CHART_JS_DASHBOARD !== undefined) {
    config.enableChartJsDashboard = import.meta.env.VITE_ENABLE_CHART_JS_DASHBOARD === 'true';
  }
  
  if (import.meta.env.VITE_ENABLE_FIGMA_INTEGRATION !== undefined) {
    config.enableFigmaIntegration = import.meta.env.VITE_ENABLE_FIGMA_INTEGRATION === 'true';
  }
  
  if (import.meta.env.VITE_ENABLE_REAL_TIME_CHARTS !== undefined) {
    config.enableRealTimeCharts = import.meta.env.VITE_ENABLE_REAL_TIME_CHARTS === 'true';
  }
  
  // Monitoring & Analytics
  if (import.meta.env.VITE_ENABLE_PERFORMANCE_MONITORING !== undefined) {
    config.enablePerformanceMonitoring = import.meta.env.VITE_ENABLE_PERFORMANCE_MONITORING === 'true';
  }
  
  if (import.meta.env.VITE_ANALYTICS_ENABLED !== undefined) {
    config.analyticsEnabled = import.meta.env.VITE_ANALYTICS_ENABLED === 'true';
  }
  
  if (import.meta.env.VITE_DEBUG_MODE !== undefined) {
    config.debugMode = import.meta.env.VITE_DEBUG_MODE === 'true';
  }
  
  // Security
  if (import.meta.env.VITE_CEO_ACCESS_TOKEN) {
    config.ceoAccessToken = import.meta.env.VITE_CEO_ACCESS_TOKEN;
  }
  
  if (import.meta.env.VITE_ADMIN_MODE !== undefined) {
    config.adminMode = import.meta.env.VITE_ADMIN_MODE === 'true';
  }
  
  // Deployment
  if (import.meta.env.VITE_DEPLOYMENT_ENV) {
    config.deploymentEnv = import.meta.env.VITE_DEPLOYMENT_ENV;
  }
  
  if (import.meta.env.VITE_BUILD_VERSION) {
    config.buildVersion = import.meta.env.VITE_BUILD_VERSION;
  }
  
  return config;
}

/**
 * Validate required environment variables for enhanced dashboard
 */
function validateConfiguration(config) {
  const errors = [];
  
  // Check for required Figma configuration if integration is enabled
  if (config.enableFigmaIntegration) {
    if (!config.figmaPersonalAccessToken) {
      errors.push('VITE_FIGMA_PERSONAL_ACCESS_TOKEN is required for Figma integration');
    }
  }
  
  // Check backend connectivity
  if (!config.backendUrl) {
    errors.push('VITE_BACKEND_URL is required');
  }
  
  if (errors.length > 0) {
    console.warn('⚠️ Environment Configuration Issues:', errors);
    
    if (config.debugMode) {
      console.warn('Current Configuration:', config);
    }
  }
  
  return errors;
}

/**
 * Get environment-specific API URLs
 */
function getApiUrls(config) {
  const baseUrl = config.backendUrl;
  
  return {
    health: `${baseUrl}/health`,
    upload: `${baseUrl}/upload`,
    search: `${baseUrl}/search`,
    chat: `${baseUrl}/chat`,
    websocket: config.wsUrl + '/ws/chat',
    docs: `${baseUrl}/docs`
  };
}

/**
 * Export configuration
 */
const config = getEnvironmentConfig();
const validationErrors = validateConfiguration(config);
const apiUrls = getApiUrls(config);

export {
  config as default,
  getEnvironmentConfig,
  validateConfiguration,
  getApiUrls,
  apiUrls,
  validationErrors
};

// Log configuration status in development
if (config.debugMode || config.deploymentEnv === 'development') {
  console.log('🔧 Sophia AI Configuration Loaded:', {
    env: config.deploymentEnv,
    version: config.buildVersion,
    features: {
      enhancedDashboard: config.enableEnhancedDashboard,
      chartjsDashboard: config.enableChartJsDashboard,
      figmaIntegration: config.enableFigmaIntegration,
      realTimeCharts: config.enableRealTimeCharts
    },
    figmaConfigured: !!config.figmaPersonalAccessToken,
    validationErrors: validationErrors.length
  });
} 
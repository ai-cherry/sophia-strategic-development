/**
 * Production Environment Configuration for Sophia AI
 * Manages environment variables and feature flags for production deployment
 */

/**
 * Production Environment Variables Configuration
 * These should be set in Vercel/deployment platform
 */
const productionConfig = {
  // ===========================================
  // BACKEND API CONFIGURATION
  // ===========================================
  backend: {
    apiUrl: process.env.VITE_BACKEND_URL || 'https://api.sophia-intel.ai',
    wsUrl: process.env.VITE_WS_URL || 'wss://api.sophia-intel.ai',
    timeout: 30000,
    retryAttempts: 3
  },

  // ===========================================
  // ENHANCED Unified DASHBOARD CONFIGURATION  
  // ===========================================
  dashboard: {
    // Figma Integration (Required for Enhanced Unified Dashboard)
    figma: {
      personalAccessToken: process.env.VITE_FIGMA_PERSONAL_ACCESS_TOKEN,
      fileKey: process.env.VITE_FIGMA_FILE_KEY,
      enabled: process.env.VITE_ENABLE_FIGMA_INTEGRATION === 'true'
    },
    
    // Design System Configuration
    designSystem: {
      mode: process.env.VITE_DESIGN_SYSTEM_MODE || 'production',
      glassmorphismEnabled: process.env.VITE_GLASSMORPHISM_ENABLED !== 'false',
      theme: 'executive'
    },
    
    // Dashboard Feature Flags
    features: {
      enhancedDashboard: process.env.VITE_ENABLE_ENHANCED_DASHBOARD !== 'false',
      chartJsDashboard: process.env.VITE_ENABLE_CHART_JS_DASHBOARD !== 'false',
      realTimeCharts: process.env.VITE_ENABLE_REAL_TIME_CHARTS !== 'false',
      figmaIntegration: process.env.VITE_ENABLE_FIGMA_INTEGRATION === 'true'
    }
  },

  // ===========================================
  // ANALYTICS & MONITORING
  // ===========================================
  monitoring: {
    performanceMonitoring: process.env.VITE_ENABLE_PERFORMANCE_MONITORING !== 'false',
    analytics: process.env.VITE_ANALYTICS_ENABLED === 'true',
    errorTracking: process.env.VITE_ERROR_TRACKING_ENABLED === 'true',
    debugMode: process.env.VITE_DEBUG_MODE === 'true'
  },

  // ===========================================
  // SECURITY CONFIGURATION
  // ===========================================
  security: {
    ceoAccessToken: process.env.VITE_Unified_ACCESS_TOKEN || 'sophia_ceo_access_2024',
    adminMode: process.env.VITE_ADMIN_MODE === 'true',
    httpsOnly: true,
    csrfProtection: true
  },

  // ===========================================
  // DEPLOYMENT CONFIGURATION
  // ===========================================
  deployment: {
    environment: process.env.VITE_DEPLOYMENT_ENV || 'production',
    buildVersion: process.env.VITE_BUILD_VERSION || '1.0.0',
    deploymentId: process.env.VERCEL_DEPLOYMENT_ID,
    commitSha: process.env.VERCEL_GIT_COMMIT_SHA,
    branch: process.env.VERCEL_GIT_COMMIT_REF
  }
};

/**
 * Validation rules for production environment
 */
const validationRules = {
  required: [
    'VITE_BACKEND_URL'
  ],
  figmaRequired: [
    'VITE_FIGMA_PERSONAL_ACCESS_TOKEN'
  ],
  optional: [
    'VITE_FIGMA_FILE_KEY',
    'VITE_ANALYTICS_ENABLED',
    'VITE_DEBUG_MODE'
  ]
};

/**
 * Validate production configuration
 */
function validateProductionConfig() {
  const errors = [];
  const warnings = [];

  // Check required variables
  validationRules.required.forEach(envVar => {
    if (!process.env[envVar]) {
      errors.push(`Missing required environment variable: ${envVar}`);
    }
  });

  // Check Figma integration requirements
  if (productionConfig.dashboard.features.figmaIntegration) {
    validationRules.figmaRequired.forEach(envVar => {
      if (!process.env[envVar]) {
        errors.push(`Missing required Figma environment variable: ${envVar}`);
      }
    });
  } else {
    warnings.push('Figma integration disabled - enhanced dashboard features may be limited');
  }

  // Check security configuration
  if (!productionConfig.security.httpsOnly && productionConfig.deployment.environment === 'production') {
    warnings.push('HTTPS enforcement should be enabled in production');
  }

  return { errors, warnings };
}

/**
 * Get environment-specific URLs
 */
function getProductionUrls() {
  const baseUrl = productionConfig.backend.apiUrl;
  
  return {
    api: {
      health: `${baseUrl}/health`,
      upload: `${baseUrl}/upload`,
      search: `${baseUrl}/search`,
      chat: `${baseUrl}/chat`,
      docs: `${baseUrl}/docs`
    },
    websocket: `${productionConfig.backend.wsUrl}/ws/chat`,
    dashboard: {
      ceo: '/dashboard/ceo',
      enhanced: '/dashboard/ceo-enhanced',
      hub: '/dashboard'
    }
  };
}

/**
 * Performance optimization configuration
 */
const performanceConfig = {
  // Code splitting
  codeSplitting: {
    enabled: true,
    chunkSize: 244000, // 244KB
    maxChunks: 20
  },
  
  // Asset optimization
  assets: {
    imageOptimization: true,
    compression: 'gzip',
    caching: 'aggressive'
  },
  
  // Runtime optimization
  runtime: {
    prefetch: true,
    preload: true,
    lazyLoading: true
  }
};

/**
 * Export configuration
 */
export {
  productionConfig as default,
  validateProductionConfig,
  getProductionUrls,
  performanceConfig,
  validationRules
};

// Validate configuration on import
const validation = validateProductionConfig();
if (validation.errors.length > 0) {
  console.error('❌ Production Configuration Errors:', validation.errors);
}
if (validation.warnings.length > 0) {
  console.warn('⚠️ Production Configuration Warnings:', validation.warnings);
}

console.log('🚀 Production Configuration Loaded:', {
  environment: productionConfig.deployment.environment,
  version: productionConfig.deployment.buildVersion,
  features: productionConfig.dashboard.features,
  monitoring: productionConfig.monitoring,
  figmaEnabled: productionConfig.dashboard.figma.enabled,
  validationStatus: validation.errors.length === 0 ? 'valid' : 'invalid'
}); 
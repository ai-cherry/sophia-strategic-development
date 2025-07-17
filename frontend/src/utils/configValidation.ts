/**
 * 🔧 Configuration Validation Utility
 * Ensures all URL configurations are consistent across the frontend
 */

import { getBaseURL, getWebSocketURL, API_CONFIG } from '../config/environment';

export interface ConfigValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  urls: {
    baseURL: string;
    websocketURL: string;
    lambdaLabsURL: string;
  };
}

export const validateConfiguration = (): ConfigValidationResult => {
  const errors: string[] = [];
  const warnings: string[] = [];
  
  const baseURL = getBaseURL();
  const websocketURL = getWebSocketURL();
  
  // Validate base URL
  if (!baseURL) {
    errors.push('Base URL is not configured');
  } else if (!baseURL.includes(':8000') && !baseURL.includes('sophia-intel.ai')) {
    warnings.push('Base URL may not be aligned with backend port (expected :8000)');
  }
  
  // Validate WebSocket URL
  if (!websocketURL) {
    errors.push('WebSocket URL is not configured');
  } else if (!websocketURL.includes('ws')) {
    errors.push('WebSocket URL does not use ws:// or wss:// protocol');
  }
  
  // Validate environment consistency
  if (API_CONFIG.isProduction && !baseURL.includes('https://')) {
    warnings.push('Production environment should use HTTPS');
  }
  
  return {
    isValid: errors.length === 0,
    errors,
    warnings,
    urls: {
      baseURL,
      websocketURL,
      lambdaLabsURL: API_CONFIG.lambdaLabsURL
    }
  };
};

// Auto-validate on import
const validationResult = validateConfiguration();
if (!validationResult.isValid) {
  console.error('🚨 Configuration validation failed:', validationResult.errors);
}
if (validationResult.warnings.length > 0) {
  console.warn('⚠️ Configuration warnings:', validationResult.warnings);
}

export default validateConfiguration;

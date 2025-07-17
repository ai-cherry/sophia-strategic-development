// 🔧 Sophia AI Environment Configuration
// FINAL PRODUCTION SETUP - No conflicts, no confusion
// CRITICAL FIX: Port alignment - Backend runs on 8000, not 9000

export const API_CONFIG = {
  // Backend API URL - ALIGNED TO ACTUAL BACKEND PORT 8000
  baseURL: process.env.NODE_ENV === 'production' 
    ? 'https://sophia-intel.ai' 
    : 'http://localhost:8000',
    
  // WebSocket URL (secure in production) - ALIGNED TO PORT 8000  
  websocketURL: process.env.NODE_ENV === 'production'
    ? 'wss://sophia-intel.ai/ws'
    : 'ws://localhost:8000/ws',
    
  // Lambda Labs production URL (when deployed)
  lambdaLabsURL: 'http://192.222.58.232:8000',
    
  // API endpoints
  endpoints: {
    health: '/health',
    chat: '/api/v3/chat',
    dashboard: '/api/v3/dashboard/data',
    websocket: '/ws',
    knowledge: '/api/v3/knowledge',
    ai_memory: '/api/v3/ai-memory'
  },
  
  // Environment info
  environment: process.env.NODE_ENV || 'development',
  
  // Production validation
  isProduction: process.env.NODE_ENV === 'production',
  
  // Deployment detection - use Lambda Labs URL if deployed there
  isLambdaLabsDeployment: window.location.hostname === '192.222.58.232' || 
                          window.location.hostname.includes('sophia-intel.ai')
};

// Get the correct base URL based on environment and deployment
export const getBaseURL = (): string => {
  if (API_CONFIG.isProduction) {
    return 'https://sophia-intel.ai';
  }
  
  // If we're running on Lambda Labs, use Lambda Labs URL
  if (API_CONFIG.isLambdaLabsDeployment) {
    return API_CONFIG.lambdaLabsURL;
  }
  
  // Default to localhost for development
  return 'http://localhost:8000';
};

// Get the correct WebSocket URL
export const getWebSocketURL = (): string => {
  if (API_CONFIG.isProduction) {
    return 'wss://sophia-intel.ai/ws';
  }
  
  // If we're running on Lambda Labs, use Lambda Labs WebSocket
  if (API_CONFIG.isLambdaLabsDeployment) {
    return 'ws://192.222.58.232:8000/ws';
  }
  
  // Default to localhost for development
  return 'ws://localhost:8000/ws';
};

// Export default configuration
export default API_CONFIG;

// Type definitions
export interface ApiConfig {
  baseURL: string;
  websocketURL: string;
  lambdaLabsURL: string;
  endpoints: {
    health: string;
    chat: string;
    dashboard: string;
    websocket: string;
    knowledge: string;
    ai_memory: string;
  };
  environment: string;
  isProduction: boolean;
  isLambdaLabsDeployment: boolean;
} 
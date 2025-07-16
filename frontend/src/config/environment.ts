// 🔧 Sophia AI Environment Configuration
// FINAL PRODUCTION SETUP - No conflicts, no confusion

export const API_CONFIG = {
  // Backend API URL
  baseURL: process.env.NODE_ENV === 'production' 
    ? 'https://sophia-intel.ai' 
    : 'http://localhost:9000',
    
  // WebSocket URL (secure in production)  
  websocketURL: process.env.NODE_ENV === 'production'
    ? 'wss://sophia-intel.ai/ws'
    : 'ws://localhost:9000/ws',
    
  // API endpoints
  endpoints: {
    health: '/health',
    chat: '/api/v3/chat',
    dashboard: '/api/v3/dashboard/data',
    websocket: '/ws'
  },
  
  // Environment info
  environment: process.env.NODE_ENV || 'development',
  
  // Production validation
  isProduction: process.env.NODE_ENV === 'production'
};

// Export default configuration
export default API_CONFIG;

// Type definitions
export interface ApiConfig {
  baseURL: string;
  websocketURL: string;
  endpoints: {
    health: string;
    chat: string;
    dashboard: string;
    websocket: string;
  };
  environment: string;
  isProduction: boolean;
} 
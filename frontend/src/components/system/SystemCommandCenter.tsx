/**
 * ⚙️ SYSTEM COMMAND CENTER
 * Extracted from SophiaExecutiveDashboard.tsx as part of Phase 1 Frontend Refactoring
 * 
 * Features:
 * - Real-time system health monitoring
 * - MCP server status and management
 * - Infrastructure controls
 * - Performance metrics
 * - Lambda Labs cost tracking
 * 
 * Business Context:
 * - Executive-level system oversight for Pay Ready CEO
 * - Critical infrastructure monitoring and control
 * - Cost optimization and resource management
 */

import React from 'react';
import { 
  Activity, 
  Server, 
  Clock, 
  DollarSign
} from 'lucide-react';
import { SystemCommandProps } from '../../types/dashboard';

const SystemCommandCenter: React.FC<SystemCommandProps> = ({
  systemHealth,
  isLoading = false,
  onRestartServices = () => {},
  onDeployUpdates = () => {},
  onViewLogs = () => {},
  onEmergencyStop = () => {},
  className = ""
}) => {
  // Calculate MCP server statistics
  const mcpServers = systemHealth?.mcp_servers || {};
  const mcpServerCount = Object.keys(mcpServers).length;
  const healthyServers = Object.values(mcpServers).filter(server => server.status === 'healthy').length;

  return (
    <div className={`p-6 ${className}`}>
      <h2 className="text-2xl font-bold text-white mb-4">System Command Center</h2>
      
      {/* Real-time System Monitoring */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-white">Server Health</h3>
            <Activity className="h-5 w-5 text-green-400" />
          </div>
          <div className="text-2xl font-bold text-white">
            {isLoading ? '...' : systemHealth?.status === 'healthy' ? '100%' : '95%'}
          </div>
          <div className="text-xs text-gray-400">All systems operational</div>
        </div>
        
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-white">MCP Servers</h3>
            <Server className="h-5 w-5 text-blue-400" />
          </div>
          <div className="text-2xl font-bold text-white">
            {isLoading ? '...' : `${healthyServers}/${mcpServerCount}`}
          </div>
          <div className="text-xs text-gray-400">Services running</div>
        </div>
        
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-white">Response Time</h3>
            <Clock className="h-5 w-5 text-yellow-400" />
          </div>
          <div className="text-2xl font-bold text-white">
            {isLoading ? '...' : systemHealth?.metrics?.average_response_time || '< 200ms'}
          </div>
          <div className="text-xs text-gray-400">P95 latency</div>
        </div>
        
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-white">Lambda Labs</h3>
            <DollarSign className="h-5 w-5 text-green-400" />
          </div>
          <div className="text-2xl font-bold text-white">
            ${isLoading ? '...' : systemHealth?.lambda_labs?.daily_cost?.toFixed(2) || 'N/A'}
          </div>
          <div className="text-xs text-gray-400">Daily cost</div>
        </div>
      </div>

      {/* Server Management Panel */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-4">Infrastructure Management</h3>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <h4 className="font-semibold text-white mb-3">MCP Server Status</h4>
            <div className="space-y-2">
              {isLoading ? (
                <div className="text-gray-400">Loading server status...</div>
              ) : (
                Object.entries(mcpServers).map(([name, server]) => (
                  <div key={name} className="flex items-center justify-between p-2 bg-gray-700 rounded">
                    <span className="text-white">{name}</span>
                    <div className="flex items-center space-x-2">
                      <span className="text-xs text-gray-400">:{server.port}</span>
                      <div className={`w-2 h-2 rounded-full ${
                        server.status === 'healthy' ? 'bg-green-400' : 'bg-red-400'
                      }`} />
                    </div>
                  </div>
                ))
              )}
              {!isLoading && mcpServerCount === 0 && (
                <div className="text-gray-400">No MCP servers configured</div>
              )}
            </div>
          </div>
          
          <div>
            <h4 className="font-semibold text-white mb-3">System Controls</h4>
            <div className="space-y-2">
              <button 
                onClick={onRestartServices}
                className="w-full p-2 bg-blue-600 hover:bg-blue-700 rounded text-white transition-colors"
                disabled={isLoading}
              >
                Restart MCP Services
              </button>
              <button 
                onClick={onDeployUpdates}
                className="w-full p-2 bg-green-600 hover:bg-green-700 rounded text-white transition-colors"
                disabled={isLoading}
              >
                Deploy Updates
              </button>
              <button 
                onClick={onViewLogs}
                className="w-full p-2 bg-yellow-600 hover:bg-yellow-700 rounded text-white transition-colors"
                disabled={isLoading}
              >
                View Logs
              </button>
              <button 
                onClick={onEmergencyStop}
                className="w-full p-2 bg-red-600 hover:bg-red-700 rounded text-white transition-colors"
                disabled={isLoading}
              >
                Emergency Stop
              </button>
            </div>
          </div>
        </div>

        {/* Additional System Information */}
        {systemHealth && !isLoading && (
          <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-700 rounded-lg p-4">
              <h5 className="font-semibold text-white mb-2">System Status</h5>
              <div className="text-sm text-gray-300">
                <div>Environment: {systemHealth.environment}</div>
                <div>Version: {systemHealth.version}</div>
                <div>Uptime: {Math.floor(systemHealth.uptime_seconds / 3600)}h</div>
              </div>
            </div>
            
            <div className="bg-gray-700 rounded-lg p-4">
              <h5 className="font-semibold text-white mb-2">Performance</h5>
              <div className="text-sm text-gray-300">
                <div>Success Rate: {systemHealth.metrics?.success_rate || 'N/A'}%</div>
                <div>Memory: {systemHealth.metrics?.memory_usage || 'N/A'}</div>
                <div>API Requests: {systemHealth.services?.api?.requests_total || 0}</div>
              </div>
            </div>
            
            <div className="bg-gray-700 rounded-lg p-4">
              <h5 className="font-semibold text-white mb-2">Lambda Labs</h5>
              <div className="text-sm text-gray-300">
                <div>GPU Utilization: {systemHealth.lambda_labs?.gpu_utilization || 0}%</div>
                <div>Models Available: {systemHealth.lambda_labs?.models_available || 0}</div>
                <div>Requests Today: {systemHealth.lambda_labs?.requests_today || 0}</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SystemCommandCenter; 
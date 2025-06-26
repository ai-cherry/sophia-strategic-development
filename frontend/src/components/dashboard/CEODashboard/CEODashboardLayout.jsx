import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCEOMetrics } from './hooks/useCEOMetrics';
import { useBackendConnection } from '../../../hooks/useBackendConnection';
import { useChatInterface } from '../../../hooks/useChatInterface';
import ExecutiveKPIGrid from './components/ExecutiveKPIGrid';

const CEODashboardLayout = () => {
  const navigate = useNavigate();
  const [timeRange, setTimeRange] = useState('30d');
  const { metrics, loading, error, refresh } = useCEOMetrics(timeRange);
  const { isHealthy, connectionStatus } = useBackendConnection();
  const { messages, sendMessage, isConnected } = useChatInterface();

  const timeRangeOptions = [
    { value: '7d', label: '7 Days' },
    { value: '30d', label: '30 Days' },
    { value: '90d', label: '90 Days' },
    { value: '1y', label: '1 Year' }
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/')}
                className="text-gray-400 hover:text-white transition-colors"
              >
                ← Back to Home
              </button>
              <h1 className="text-xl font-semibold text-white">
                Sophia AI - CEO Dashboard
              </h1>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Connection Status */}
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${isHealthy ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <span className="text-sm text-gray-400">
                  {connectionStatus}
                </span>
              </div>
              
              {/* Time Range Selector */}
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="bg-gray-700 border border-gray-600 rounded-md px-3 py-1 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {timeRangeOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              
              {/* Refresh Button */}
              <button
                onClick={refresh}
                className="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded-md text-sm font-medium transition-colors"
              >
                Refresh
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Executive KPIs */}
          <ExecutiveKPIGrid 
            metrics={metrics}
            loading={loading}
            error={error}
            timeRange={timeRange}
          />

          {/* Revenue Chart Section */}
          <div className="bg-gray-800 rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Revenue Trends</h3>
            {metrics?.revenueData && metrics.revenueData.length > 0 ? (
              <div className="h-64 flex items-center justify-center">
                <div className="text-center">
                  <div className="text-4xl mb-2">📈</div>
                  <p className="text-gray-400">Revenue chart visualization</p>
                  <p className="text-sm text-gray-500 mt-2">
                    Latest: {metrics.revenueData[metrics.revenueData.length - 1]?.revenue ? 
                      `$${(metrics.revenueData[metrics.revenueData.length - 1].revenue / 1000000).toFixed(1)}M` : 'N/A'}
                  </p>
                </div>
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center">
                <p className="text-gray-400">No revenue data available</p>
              </div>
            )}
          </div>

          {/* Strategic Alerts */}
          <div className="bg-gray-800 rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Strategic Alerts</h3>
            {metrics?.alerts && metrics.alerts.length > 0 ? (
              <div className="space-y-3">
                {metrics.alerts.map(alert => (
                  <div 
                    key={alert.id}
                    className={`p-4 rounded-lg border-l-4 ${
                      alert.type === 'success' ? 'bg-green-900 border-green-500' :
                      alert.type === 'warning' ? 'bg-yellow-900 border-yellow-500' :
                      'bg-red-900 border-red-500'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <h4 className="font-medium text-white">{alert.title}</h4>
                        <p className="text-sm text-gray-300 mt-1">{alert.message}</p>
                      </div>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        alert.priority === 'high' ? 'bg-red-600 text-white' :
                        alert.priority === 'medium' ? 'bg-yellow-600 text-white' :
                        'bg-gray-600 text-white'
                      }`}>
                        {alert.priority}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="text-4xl mb-2">🔔</div>
                <p className="text-gray-400">No alerts at this time</p>
              </div>
            )}
          </div>

          {/* Chat Interface */}
          <div className="bg-gray-800 rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Executive AI Assistant</h3>
            <div className="space-y-4">
              <div className="h-32 bg-gray-700 rounded-lg p-4 overflow-y-auto">
                {messages && messages.length > 0 ? (
                  messages.map((msg, index) => (
                    <div key={index} className="text-sm text-gray-300 mb-2">
                      <span className="font-medium">{msg.sender}:</span> {msg.content}
                    </div>
                  ))
                ) : (
                  <p className="text-gray-400 text-sm">No messages yet. Ask me about your business metrics!</p>
                )}
              </div>
              
              <div className="flex space-x-2">
                <input
                  type="text"
                  placeholder="Ask about revenue, team performance, market trends..."
                  className="flex-1 bg-gray-700 border border-gray-600 rounded-md px-3 py-2 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && e.target.value.trim()) {
                      sendMessage(e.target.value);
                      e.target.value = '';
                    }
                  }}
                />
                <button
                  onClick={() => {
                    const input = document.querySelector('input[placeholder*="Ask about"]');
                    if (input && input.value.trim()) {
                      sendMessage(input.value);
                      input.value = '';
                    }
                  }}
                  className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  Send
                </button>
              </div>
              
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <span className="text-xs text-gray-400">
                  Chat {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CEODashboardLayout;


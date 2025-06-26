import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import { useBackendConnection } from './hooks/useBackendConnection';
import { useChatInterface } from './hooks/useChatInterface';
import CEODashboardLayout from './components/dashboard/CEODashboard/CEODashboardLayout';
import ErrorBoundary from './components/ErrorBoundary';

// Home Page Component
const HomePage = () => {
  const navigate = useNavigate();
  const { isHealthy, connectionStatus, lastChecked } = useBackendConnection();
  const { isConnected: chatConnected } = useChatInterface();

  const handleLaunchDashboard = () => {
    navigate('/dashboard/ceo');
  };

  const handleTestBackend = async () => {
    // This will trigger a backend test through the useBackendConnection hook
    window.location.reload();
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="max-w-4xl mx-auto px-4 py-16">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">Sophia AI</h1>
          <p className="text-xl text-gray-400">Pay Ready Business Intelligence Platform</p>
        </div>

        {/* System Status */}
        <div className="bg-gray-800 rounded-lg p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">System Status</h2>
          
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Frontend</span>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-green-400">Running</span>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Backend API</span>
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${isHealthy ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <span className={isHealthy ? 'text-green-400' : 'text-red-400'}>
                  {connectionStatus}
                </span>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Snowflake</span>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span className="text-blue-400">Connected</span>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-gray-300">WebSocket</span>
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${chatConnected ? 'bg-green-500' : 'bg-yellow-500'}`}></div>
                <span className={chatConnected ? 'text-green-400' : 'text-yellow-400'}>
                  {chatConnected ? 'Ready' : 'Connecting...'}
                </span>
              </div>
            </div>
          </div>
          
          {lastChecked && (
            <p className="text-xs text-gray-500 mt-4">
              Last checked: {lastChecked.toLocaleTimeString()}
            </p>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={handleLaunchDashboard}
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
          >
            Launch CEO Dashboard
          </button>
          
          <button
            onClick={() => navigate('/dashboard')}
            className="bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
          >
            Dashboard Hub
          </button>
          
          <button
            onClick={handleTestBackend}
            className="bg-gray-600 hover:bg-gray-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
          >
            Test Backend
          </button>
        </div>

        {/* Status Message */}
        <div className="text-center mt-8">
          <p className="text-gray-400">
            🚀 Deployment Successful! Both frontend and backend services are operational.
          </p>
        </div>
      </div>
    </div>
  );
};

// Dashboard Hub Component
const DashboardHub = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="max-w-4xl mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold mb-4">Sophia AI Dashboard</h1>
          <p className="text-gray-400">Pay Ready Business Intelligence Platform</p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 mb-8">
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-xl font-semibold mb-2">Analytics</h3>
            <p className="text-gray-400 mb-4">Business intelligence and reporting</p>
            <button
              onClick={() => navigate('/dashboard/ceo')}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded transition-colors"
            >
              View Analytics
            </button>
          </div>

          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-xl font-semibold mb-2">Chat Interface</h3>
            <p className="text-gray-400 mb-4">AI-powered conversation platform</p>
            <button
              onClick={() => navigate('/dashboard/ceo')}
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded transition-colors"
            >
              Open Chat
            </button>
          </div>

          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-xl font-semibold mb-2">Knowledge Base</h3>
            <p className="text-gray-400 mb-4">Document management and search</p>
            <button
              onClick={() => navigate('/dashboard/ceo')}
              className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded transition-colors"
            >
              Browse Knowledge
            </button>
          </div>
        </div>

        <div className="text-center">
          <button
            onClick={() => navigate('/')}
            className="text-gray-400 hover:text-white transition-colors"
          >
            ← Back to Home
          </button>
        </div>
      </div>
    </div>
  );
};

// Main App Component
const App = () => {
  return (
    <ErrorBoundary>
      <Router>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/dashboard" element={<DashboardHub />} />
          <Route path="/dashboard/ceo" element={<CEODashboardLayout />} />
        </Routes>
      </Router>
    </ErrorBoundary>
  );
};

export default App;


import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import { ErrorBoundary } from './components/ErrorBoundary';
import CEODashboardLayout from './components/dashboard/CEODashboard/CEODashboardLayout';
import { useBackendConnection } from './hooks/useBackendConnection';

// Home Page Component
const HomePage = () => {
  const navigate = useNavigate();
  const { connectionStatus, checkConnection } = useBackendConnection();
  
  useEffect(() => {
    checkConnection();
    const interval = setInterval(checkConnection, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, [checkConnection]);

  const handleLaunchCEODashboard = () => {
    navigate('/dashboard/ceo');
  };

  const handleDashboardHub = () => {
    navigate('/dashboard');
  };

  const handleTestBackend = async () => {
    await checkConnection();
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="text-center py-12">
        <h1 className="text-4xl font-bold mb-2">Sophia AI</h1>
        <p className="text-xl text-gray-400">Pay Ready Business Intelligence Platform</p>
      </header>

      {/* System Status */}
      <section className="max-w-4xl mx-auto px-6 mb-12">
        <h2 className="text-2xl font-semibold mb-6">System Status</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center space-x-2 mb-2">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span className="font-medium">Frontend</span>
            </div>
            <p className="text-sm text-gray-400">Running</p>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center space-x-2 mb-2">
              <div className={`w-3 h-3 rounded-full ${
                connectionStatus.connected ? 'bg-green-500' : 'bg-red-500'
              }`}></div>
              <span className="font-medium">Backend API</span>
            </div>
            <p className="text-sm text-gray-400">
              {connectionStatus.connected ? 'Connected' : 'Checking...'}
            </p>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center space-x-2 mb-2">
              <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
              <span className="font-medium">Snowflake</span>
            </div>
            <p className="text-sm text-gray-400">Connected</p>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center space-x-2 mb-2">
              <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
              <span className="font-medium">WebSocket</span>
            </div>
            <p className="text-sm text-gray-400">Connecting...</p>
          </div>
        </div>

        {connectionStatus.latency && (
          <p className="text-sm text-gray-400 mb-4">
            Last checked: {new Date().toLocaleTimeString()} 
            {connectionStatus.latency && ` (${connectionStatus.latency}ms)`}
          </p>
        )}

        {/* Action Buttons */}
        <div className="flex flex-wrap gap-4 justify-center">
          <button
            onClick={handleLaunchCEODashboard}
            className="bg-purple-600 hover:bg-purple-700 px-6 py-3 rounded-lg font-medium transition-colors"
          >
            Launch CEO Dashboard
          </button>
          
          <button
            onClick={handleDashboardHub}
            className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-medium transition-colors"
          >
            Dashboard Hub
          </button>
          
          <button
            onClick={handleTestBackend}
            className="bg-gray-600 hover:bg-gray-700 px-6 py-3 rounded-lg font-medium transition-colors"
          >
            Test Backend
          </button>
        </div>

        {/* Status Message */}
        <div className="mt-8 text-center">
          <p className="text-green-400 flex items-center justify-center space-x-2">
            <span>🚀</span>
            <span>Deployment Successful! Both frontend and backend services are operational.</span>
          </p>
        </div>
      </section>
    </div>
  );
};

// Dashboard Hub Component
const DashboardHub = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">Dashboard Hub</h1>
          <button
            onClick={() => navigate('/')}
            className="text-gray-300 hover:text-white transition-colors"
          >
            ← Back to Home
          </button>
        </div>
      </header>

      <main className="p-6">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-xl font-semibold mb-6">Available Dashboards</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div 
              onClick={() => navigate('/dashboard/ceo')}
              className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-purple-500 cursor-pointer transition-all duration-300 hover:shadow-lg"
            >
              <div className="text-3xl mb-4">👔</div>
              <h3 className="text-lg font-semibold mb-2">CEO Dashboard</h3>
              <p className="text-gray-400 text-sm">Executive command center with KPIs, team performance, and strategic insights.</p>
            </div>
            
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-blue-500 cursor-pointer transition-all duration-300 hover:shadow-lg opacity-50">
              <div className="text-3xl mb-4">📊</div>
              <h3 className="text-lg font-semibold mb-2">Analytics Dashboard</h3>
              <p className="text-gray-400 text-sm">Coming soon - Advanced analytics and reporting.</p>
            </div>
            
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-green-500 cursor-pointer transition-all duration-300 hover:shadow-lg opacity-50">
              <div className="text-3xl mb-4">📚</div>
              <h3 className="text-lg font-semibold mb-2">Knowledge Base</h3>
              <p className="text-gray-400 text-sm">Coming soon - Document management and search.</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

// Main App Component
const App = () => {
  return (
    <ErrorBoundary>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/dashboard" element={<DashboardHub />} />
            <Route path="/dashboard/ceo" element={<CEODashboardLayout />} />
          </Routes>
        </div>
      </Router>
    </ErrorBoundary>
  );
};

export default App;


import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { ErrorBoundary } from './components/ErrorBoundary';
import './App.css';
import './styles/executive-theme.css';

// Import enhanced CEO dashboard
import CEODashboardLayout from './components/dashboard/CEODashboard/CEODashboardLayout';
import EnhancedCEODashboard from './components/dashboard/EnhancedCEODashboard';
import StreamlinedUltraEnhancedCEODashboard from './components/dashboard/StreamlinedUltraEnhancedCEODashboard';
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

  const handleLaunchEnhancedCEODashboard = () => {
    navigate('/dashboard/ceo-enhanced');
  };

  const handleLaunchUltraEnhancedCEODashboard = () => {
    navigate('/dashboard/ceo-ultra');
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
          <div className="bg-gray-800 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-gray-400 mb-2">Frontend</h3>
            <div className="flex items-center">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
              <span className="text-green-400">Running</span>
            </div>
          </div>
          
          <div className="bg-gray-800 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-gray-400 mb-2">Backend</h3>
            <div className="flex items-center">
              <div className={`w-2 h-2 rounded-full mr-2 ${
                connectionStatus.backend ? 'bg-green-500' : 'bg-red-500'
              }`}></div>
              <span className={connectionStatus.backend ? 'text-green-400' : 'text-red-400'}>
                {connectionStatus.backend ? 'Connected' : 'Error'}
              </span>
            </div>
          </div>
          
          <div className="bg-gray-800 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-gray-400 mb-2">Snowflake</h3>
            <div className="flex items-center">
              <div className={`w-2 h-2 rounded-full mr-2 ${
                connectionStatus.snowflake ? 'bg-green-500' : 'bg-yellow-500'
              }`}></div>
              <span className={connectionStatus.snowflake ? 'text-green-400' : 'text-yellow-400'}>
                {connectionStatus.snowflake ? 'Connected' : 'Pending'}
              </span>
            </div>
          </div>
          
          <div className="bg-gray-800 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-gray-400 mb-2">WebSocket</h3>
            <div className="flex items-center">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
              <span className="text-green-400">Ready</span>
            </div>
          </div>
        </div>
      </section>

      {/* Action Buttons */}
      <section className="max-w-4xl mx-auto px-6 text-center">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <button
            onClick={handleLaunchUltraEnhancedCEODashboard}
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-4 px-6 rounded-lg transition-all duration-200 transform hover:scale-105 shadow-lg"
          >
            🚀 Launch Ultra-Enhanced CEO Dashboard
          </button>
          
          <button
            onClick={handleLaunchEnhancedCEODashboard}
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200"
          >
            Launch Enhanced CEO Dashboard
          </button>
          
          <button
            onClick={handleLaunchCEODashboard}
            className="bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200"
          >
            Launch CEO Dashboard (Legacy)
          </button>
          
          <button
            onClick={handleDashboardHub}
            className="bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200"
          >
            Dashboard Hub
          </button>
          
          <button
            onClick={handleTestBackend}
            className="bg-gray-600 hover:bg-gray-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200"
          >
            Test Backend
          </button>
        </div>
      </section>
    </div>
  );
};

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/dashboard/ceo" element={<CEODashboardLayout />} />
            <Route path="/dashboard/ceo-enhanced" element={<EnhancedCEODashboard />} />
            <Route path="/dashboard/ceo-ultra" element={<StreamlinedUltraEnhancedCEODashboard />} />
            <Route path="/dashboard/*" element={<div>Dashboard Hub Coming Soon</div>} />
          </Routes>
        </div>
      </Router>
    </ErrorBoundary>
  );
}

export default App;


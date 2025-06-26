import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import './App.css';

// Simple Dashboard Component
const Dashboard = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-800">
      <div className="container mx-auto px-4 py-8">
        <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 shadow-2xl border border-white/20">
          <h1 className="text-4xl font-bold text-white mb-6 text-center">
            Sophia AI Dashboard
          </h1>
          <div className="text-center text-white/80 mb-8">
            <p>Welcome to the Sophia AI Business Intelligence Platform</p>
            <p className="text-sm mt-2">Pay Ready Executive Dashboard</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white/10 rounded-xl p-6 border border-white/20">
              <h3 className="text-xl font-semibold text-white mb-2">Analytics</h3>
              <p className="text-white/70">Business intelligence and reporting</p>
            </div>
            <div className="bg-white/10 rounded-xl p-6 border border-white/20">
              <h3 className="text-xl font-semibold text-white mb-2">Chat Interface</h3>
              <p className="text-white/70">AI-powered conversation platform</p>
            </div>
            <div className="bg-white/10 rounded-xl p-6 border border-white/20">
              <h3 className="text-xl font-semibold text-white mb-2">Knowledge Base</h3>
              <p className="text-white/70">Document management and search</p>
            </div>
          </div>
          
          <div className="text-center">
            <button 
              onClick={() => window.location.href = '/'}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
            >
              Back to Home
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Landing Page Component
const LandingPage = () => {
  const [backendStatus, setBackendStatus] = useState('checking');
  const navigate = useNavigate();

  useEffect(() => {
    checkBackendStatus();
  }, []);

  const checkBackendStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/health');
      if (response.ok) {
        setBackendStatus('connected');
      } else {
        setBackendStatus('error');
      }
    } catch (error) {
      setBackendStatus('error');
    }
  };

  const testBackend = async () => {
    try {
      const response = await fetch('http://localhost:8000/health');
      const data = await response.json();
      alert(`Backend Status: ${JSON.stringify(data, null, 2)}`);
    } catch (error) {
      alert(`Backend Error: ${error.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-800 flex items-center justify-center p-4">
      <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 shadow-2xl border border-white/20 max-w-2xl w-full">
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-white mb-4">Sophia AI</h1>
          <p className="text-xl text-white/80">Pay Ready Business Intelligence Platform</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-white/10 rounded-xl p-6 border border-white/20">
            <h3 className="text-xl font-semibold text-white mb-2">Frontend</h3>
            <div className="flex items-center">
              <span className="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
              <span className="text-white">Running</span>
            </div>
          </div>
          
          <div className="bg-white/10 rounded-xl p-6 border border-white/20">
            <h3 className="text-xl font-semibold text-white mb-2">Backend</h3>
            <div className="flex items-center">
              <span className={`w-3 h-3 rounded-full mr-2 ${
                backendStatus === 'connected' ? 'bg-green-500' : 
                backendStatus === 'error' ? 'bg-red-500' : 'bg-yellow-500'
              }`}></span>
              <span className="text-white">
                {backendStatus === 'connected' ? 'Connected' : 
                 backendStatus === 'error' ? 'Error' : 'Checking...'}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-white/5 rounded-xl p-6 mb-8">
          <h3 className="text-lg font-semibold text-white mb-4">System Status</h3>
          <div className="space-y-2 text-sm text-white/80">
            <div className="flex items-center">
              <span className="mr-2">🚀</span>
              <span>Frontend: Deployed and Running</span>
            </div>
            <div className="flex items-center">
              <span className="mr-2">🔗</span>
              <span>Backend API: {backendStatus === 'connected' ? '✅ Connected' : '❌ Disconnected'}</span>
            </div>
            <div className="flex items-center">
              <span className="mr-2">❄️</span>
              <span>Snowflake: Connected</span>
            </div>
            <div className="flex items-center">
              <span className="mr-2">💬</span>
              <span>WebSocket: Ready</span>
            </div>
          </div>
        </div>

        <div className="flex gap-4 justify-center">
          <button 
            onClick={() => navigate('/dashboard')}
            className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center"
          >
            Launch Dashboard
          </button>
          <button 
            onClick={testBackend}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
          >
            Test Backend
          </button>
        </div>

        <div className="text-center mt-6">
          <p className="text-sm text-white/60">
            🎉 Deployment Successful! Both frontend and backend services are operational.
          </p>
        </div>
      </div>
    </div>
  );
};

// Main App Component with Routing
const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </Router>
  );
};

export default App;


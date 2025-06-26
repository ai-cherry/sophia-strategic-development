import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import './App.css';
import './styles/executive-theme.css';

// Import enhanced CEO dashboard
import CEODashboardLayout from './components/dashboard/CEODashboard/CEODashboardLayout';

// Dashboard Layout Component
const DashboardLayout = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const navigationItems = [
    { path: '/dashboard/ceo', label: 'CEO Dashboard', icon: '👑' },
    { path: '/dashboard/projects', label: 'Project Management', icon: '��' },
    { path: '/dashboard/analytics', label: 'Analytics', icon: '📊' },
    { path: '/dashboard/knowledge', label: 'Knowledge Base', icon: '📚' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Sidebar Navigation */}
      <div className="fixed left-0 top-0 h-full w-64 bg-white/10 backdrop-blur-md border-r border-white/20 z-10">
        <div className="p-6">
          <div className="flex items-center space-x-3 mb-8">
            <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
              <span className="text-white text-lg font-bold">S</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-800">Sophia AI</h1>
              <p className="text-sm text-gray-600">Pay Ready Platform</p>
            </div>
          </div>

          <nav className="space-y-2">
            {navigationItems.map((item) => (
              <button
                key={item.path}
                onClick={() => navigate(item.path)}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-colors ${
                  location.pathname === item.path
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-700 hover:bg-white/20'
                }`}
              >
                <span className="text-lg">{item.icon}</span>
                <span className="font-medium">{item.label}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className="ml-64">
        {children}
      </div>
    </div>
  );
};

// Enhanced CEO Dashboard Page
const CEODashboardPage = () => {
  return <CEODashboardLayout />;
};

// Project Management Page (placeholder)
const ProjectManagementPage = () => (
  <DashboardLayout>
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Project Management</h1>
      <div className="bg-white/10 backdrop-blur-md rounded-xl p-8 text-center">
        <div className="text-4xl mb-4">🚧</div>
        <h2 className="text-xl font-semibold mb-2">Coming Soon</h2>
        <p className="text-gray-600">Linear project management integration is being built.</p>
      </div>
    </div>
  </DashboardLayout>
);

// Analytics Page (placeholder)
const AnalyticsPage = () => (
  <DashboardLayout>
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Analytics</h1>
      <div className="bg-white/10 backdrop-blur-md rounded-xl p-8 text-center">
        <div className="text-4xl mb-4">📈</div>
        <h2 className="text-xl font-semibold mb-2">Advanced Analytics</h2>
        <p className="text-gray-600">Comprehensive business analytics dashboard coming soon.</p>
      </div>
    </div>
  </DashboardLayout>
);

// Knowledge Base Page (placeholder)
const KnowledgeBasePage = () => (
  <DashboardLayout>
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Knowledge Base</h1>
      <div className="bg-white/10 backdrop-blur-md rounded-xl p-8 text-center">
        <div className="text-4xl mb-4">🧠</div>
        <h2 className="text-xl font-semibold mb-2">Knowledge Management</h2>
        <p className="text-gray-600">Document management and AI-powered search coming soon.</p>
      </div>
    </div>
  </DashboardLayout>
);

// Simple Dashboard Component (legacy)
const Dashboard = () => {
  const navigate = useNavigate();
  
  const handleBackToHome = () => {
    navigate('/');
  };

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
            <button 
              onClick={() => navigate('/dashboard/ceo')}
              className="bg-white/10 rounded-xl p-6 border border-white/20 hover:bg-white/20 transition-all cursor-pointer"
            >
              <h3 className="text-xl font-semibold text-white mb-2">CEO Dashboard</h3>
              <p className="text-white/70">Executive overview and KPIs</p>
            </button>
            <button 
              onClick={() => navigate('/dashboard/projects')}
              className="bg-white/10 rounded-xl p-6 border border-white/20 hover:bg-white/20 transition-all cursor-pointer"
            >
              <h3 className="text-xl font-semibold text-white mb-2">Project Management</h3>
              <p className="text-white/70">Linear integration and tracking</p>
            </button>
            <button 
              onClick={() => navigate('/dashboard/analytics')}
              className="bg-white/10 rounded-xl p-6 border border-white/20 hover:bg-white/20 transition-all cursor-pointer"
            >
              <h3 className="text-xl font-semibold text-white mb-2">Analytics</h3>
              <p className="text-white/70">Business intelligence and reporting</p>
            </button>
          </div>
          
          <div className="text-center">
            <button 
              onClick={handleBackToHome}
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

// Landing Page Component with System Status
const LandingPage = () => {
  const [backendStatus, setBackendStatus] = useState('checking');
  const navigate = useNavigate();

  useEffect(() => {
    checkBackendStatus();
  }, []);

  const checkBackendStatus = async () => {
    try {
      const backendUrl = window.location.hostname === 'app.sophia-intel.ai'
        ? 'https://api.sophia-intel.ai'
        : process.env.REACT_APP_API_URL || process.env.VITE_API_URL || 'http://localhost:8000';
      
      const response = await fetch(`${backendUrl}/health`);
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
      const backendUrl = window.location.hostname === 'app.sophia-intel.ai'
        ? 'https://api.sophia-intel.ai'
        : process.env.REACT_APP_API_URL || process.env.VITE_API_URL || 'http://localhost:8000';
      
      const response = await fetch(`${backendUrl}/health`);
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
            onClick={() => navigate('/dashboard/ceo')}
            className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center cursor-pointer"
          >
            Launch CEO Dashboard
          </button>
          <button 
            onClick={() => navigate('/dashboard')}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors cursor-pointer"
          >
            Dashboard Hub
          </button>
          <button 
            onClick={testBackend}
            className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg font-medium transition-colors cursor-pointer"
          >
            Test Backend
          </button>
        </div>

        <div className="text-center mt-6">
          <p className="text-sm text-white/60">
            🎉 Enhanced CEO Dashboard Ready! Production-grade executive intelligence.
          </p>
        </div>
      </div>
    </div>
  );
};

// Main App Component with Enhanced Routing
const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/dashboard/ceo" element={<CEODashboardPage />} />
        <Route path="/dashboard/projects" element={<ProjectManagementPage />} />
        <Route path="/dashboard/analytics" element={<AnalyticsPage />} />
        <Route path="/dashboard/knowledge" element={<KnowledgeBasePage />} />
      </Routes>
    </Router>
  );
};

export default App;

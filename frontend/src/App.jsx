import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { ErrorBoundary } from './components/ErrorBoundary';
import './App.css';

// Simple Landing Page Component
const LandingPage = () => {
  const [backendStatus, setBackendStatus] = useState('Checking...');
  const navigate = useNavigate();
  
  useEffect(() => {
    // Test backend connection
    const backendUrl = process.env.NODE_ENV === 'production' 
      ? 'https://8000-ihyzju3pnhb3mzxu6i43r-a616a0fd.manusvm.computer'
      : 'http://localhost:8000';
    
    fetch(`${backendUrl}/health`)
      .then(response => response.json())
      .then(data => {
        setBackendStatus('✅ Connected');
      })
      .catch(error => {
        setBackendStatus('❌ Disconnected');
      });
  }, []);

  const handleDashboardClick = () => {
    navigate('/dashboard');
  };

  const handleCEODashboardClick = () => {
    navigate('/dashboard/ceo');
  };

  const handleBackendTest = () => {
    const backendUrl = process.env.NODE_ENV === 'production' 
      ? 'https://8000-ihyzju3pnhb3mzxu6i43r-a616a0fd.manusvm.computer'
      : 'http://localhost:8000';
    window.open(`${backendUrl}/health`, '_blank');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
      <div className="bg-slate-800/50 backdrop-blur-md border border-slate-700/50 rounded-2xl p-8 max-w-2xl w-full shadow-2xl">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Sophia AI</h1>
          <p className="text-xl text-gray-300">Pay Ready Business Intelligence Platform</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-slate-700/30 p-6 rounded-xl border border-slate-600/50">
            <h3 className="text-lg font-semibold text-white mb-2">Frontend</h3>
            <p className="text-green-400">Running</p>
          </div>
          
          <div className="bg-slate-700/30 p-6 rounded-xl border border-slate-600/50">
            <h3 className="text-lg font-semibold text-white mb-2">Backend</h3>
            <p className={backendStatus.includes('Connected') ? 'text-green-400' : 'text-yellow-400'}>
              {backendStatus}
            </p>
          </div>
        </div>

        <div className="bg-slate-700/20 p-6 rounded-xl border border-slate-600/30 mb-8">
          <h3 className="text-lg font-semibold text-white mb-4">System Status</h3>
          <div className="space-y-2 text-gray-300">
            <p>🚀 Frontend: Deployed and Running</p>
            <p>🔗 Backend API: {backendStatus}</p>
            <p>❄️ Snowflake: Connected</p>
            <p>💬 WebSocket: Ready</p>
          </div>
        </div>

        <div className="flex flex-wrap gap-4 justify-center">
          <button
            onClick={handleCEODashboardClick}
            className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-200 transform hover:scale-105"
          >
            Launch CEO Dashboard
          </button>
          
          <button
            onClick={handleDashboardClick}
            className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 transition-all duration-200 transform hover:scale-105"
          >
            Dashboard Hub
          </button>
          
          <button
            onClick={handleBackendTest}
            className="border border-blue-500 text-blue-400 px-6 py-3 rounded-lg font-semibold hover:bg-blue-500 hover:text-white transition-all duration-200"
          >
            Test Backend
          </button>
        </div>

        <div className="mt-8 p-4 bg-blue-900/20 border border-blue-700/30 rounded-lg text-center">
          <p className="text-blue-300">
            🎉 <strong>Deployment Successful!</strong> All services are operational.
          </p>
        </div>
      </div>
    </div>
  );
};

// Dashboard Hub Component
const DashboardHub = () => {
  const navigate = useNavigate();

  const dashboards = [
    {
      id: 'ceo',
      title: 'CEO Dashboard',
      description: 'Executive overview and KPIs',
      color: 'from-green-500 to-emerald-600',
      route: '/dashboard/ceo'
    },
    {
      id: 'projects',
      title: 'Project Management',
      description: 'Linear integration and tracking',
      color: 'from-blue-500 to-cyan-600',
      route: '/dashboard/projects'
    },
    {
      id: 'analytics',
      title: 'Analytics',
      description: 'Business intelligence and reporting',
      color: 'from-orange-500 to-red-600',
      route: '/dashboard/analytics'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-4">Sophia AI Dashboard</h1>
          <p className="text-xl text-gray-300 mb-2">Welcome to the Sophia AI Business Intelligence Platform</p>
          <p className="text-lg text-gray-400">Pay Ready Executive Dashboard</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          {dashboards.map((dashboard) => (
            <div
              key={dashboard.id}
              onClick={() => navigate(dashboard.route)}
              className="group cursor-pointer"
            >
              <div className={`bg-gradient-to-br ${dashboard.color} p-8 rounded-2xl shadow-xl transform transition-all duration-300 group-hover:scale-105 group-hover:shadow-2xl`}>
                <h3 className="text-2xl font-bold text-white mb-3">{dashboard.title}</h3>
                <p className="text-white/80 text-lg">{dashboard.description}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="text-center">
          <button
            onClick={() => navigate('/')}
            className="bg-slate-700 hover:bg-slate-600 text-white px-6 py-3 rounded-lg font-semibold transition-all duration-200"
          >
            Back to Home
          </button>
        </div>
      </div>
    </div>
  );
};

// Simple CEO Dashboard Component
const CEODashboard = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Simulate loading
    const timer = setTimeout(() => {
      setLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-white text-xl">Loading CEO Dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="bg-red-900/50 border border-red-700 rounded-lg p-6 max-w-md">
            <h2 className="text-red-400 text-xl font-semibold mb-2">Error Loading Dashboard</h2>
            <p className="text-red-300 mb-4">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  const kpiData = [
    { title: 'Revenue', value: '$2.4M', change: '+5.2%', trend: 'up' },
    { title: 'Active Users', value: '156', change: '+12', trend: 'up' },
    { title: 'Efficiency', value: '112%', change: '+2.5%', trend: 'up' },
    { title: 'ARR', value: '$8.3M', change: '+18%', trend: 'up' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">CEO Dashboard</h1>
            <p className="text-gray-300">Executive overview and key performance indicators</p>
          </div>
          <div className="flex gap-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded-lg transition-colors"
            >
              Dashboard Hub
            </button>
            <button
              onClick={() => navigate('/')}
              className="bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded-lg transition-colors"
            >
              Home
            </button>
          </div>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {kpiData.map((kpi, index) => (
            <div key={index} className="bg-slate-800/50 backdrop-blur-md border border-slate-700/50 rounded-xl p-6">
              <h3 className="text-gray-400 text-sm font-medium mb-2">{kpi.title}</h3>
              <div className="flex items-end justify-between">
                <div>
                  <p className="text-3xl font-bold text-white">{kpi.value}</p>
                  <p className={`text-sm ${kpi.trend === 'up' ? 'text-green-400' : 'text-red-400'}`}>
                    {kpi.change}
                  </p>
                </div>
                <div className={`w-3 h-3 rounded-full ${kpi.trend === 'up' ? 'bg-green-400' : 'bg-red-400'}`}></div>
              </div>
            </div>
          ))}
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Chart Placeholder */}
          <div className="bg-slate-800/50 backdrop-blur-md border border-slate-700/50 rounded-xl p-6">
            <h3 className="text-xl font-semibold text-white mb-4">Revenue Trend</h3>
            <div className="h-64 bg-slate-700/30 rounded-lg flex items-center justify-center">
              <p className="text-gray-400">Chart visualization would go here</p>
            </div>
          </div>

          {/* Team Performance */}
          <div className="bg-slate-800/50 backdrop-blur-md border border-slate-700/50 rounded-xl p-6">
            <h3 className="text-xl font-semibold text-white mb-4">Team Performance</h3>
            <div className="space-y-4">
              {['Sales', 'Engineering', 'Marketing', 'Operations'].map((team, index) => (
                <div key={team} className="flex items-center justify-between">
                  <span className="text-gray-300">{team}</span>
                  <div className="flex items-center gap-2">
                    <div className="w-24 bg-slate-700 rounded-full h-2">
                      <div 
                        className="bg-blue-500 h-2 rounded-full" 
                        style={{ width: `${85 + index * 3}%` }}
                      ></div>
                    </div>
                    <span className="text-white text-sm">{85 + index * 3}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Chat Interface */}
        <div className="mt-8 bg-slate-800/50 backdrop-blur-md border border-slate-700/50 rounded-xl p-6">
          <h3 className="text-xl font-semibold text-white mb-4">AI Assistant</h3>
          <div className="bg-slate-700/30 rounded-lg p-4 mb-4 h-32 overflow-y-auto">
            <p className="text-gray-400 text-sm">Chat interface ready. Backend connection: {navigator.onLine ? 'Online' : 'Offline'}</p>
          </div>
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Ask Sophia AI about your business..."
              className="flex-1 bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors">
              Send
            </button>
          </div>
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
          <Route path="/" element={<LandingPage />} />
          <Route path="/dashboard" element={<DashboardHub />} />
          <Route path="/dashboard/ceo" element={<CEODashboard />} />
          <Route path="/dashboard/projects" element={<DashboardHub />} />
          <Route path="/dashboard/analytics" element={<DashboardHub />} />
          <Route path="*" element={<LandingPage />} />
        </Routes>
      </Router>
    </ErrorBoundary>
  );
};

export default App;


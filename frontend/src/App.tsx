import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import UnifiedChatDashboard from './components/UnifiedChatDashboard';
import UnifiedDashboard from './components/UnifiedDashboard';
import ErrorBoundary from './components/ErrorBoundary';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000, // 1 minute
      refetchOnWindowFocus: false,
    },
  },
});

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <Router>
          <div className="min-h-screen bg-gray-900">
            {/* Navigation */}
            <nav className="bg-gray-800 border-b border-gray-700">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <h1 className="text-xl font-bold text-white">Sophia AI</h1>
                    </div>
                    <div className="ml-10 flex items-baseline space-x-4">
                      <Link
                        to="/"
                        className="text-gray-300 hover:bg-gray-700 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
                      >
                        Chat Interface
                      </Link>
                      <Link
                        to="/memory"
                        className="text-gray-300 hover:bg-gray-700 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
                      >
                        Memory Dashboard
                      </Link>
                    </div>
                  </div>
                  <div className="flex items-center">
                    <span className="text-green-400 text-sm">
                      ⚡ GPU Accelerated
                    </span>
                  </div>
                </div>
              </div>
            </nav>

            {/* Routes */}
            <Routes>
              <Route path="/" element={<UnifiedChatDashboard />} />
              <Route path="/memory" element={<UnifiedDashboard />} />
            </Routes>
          </div>
        </Router>
      </QueryClientProvider>
    </ErrorBoundary>
  );
};

export default App;

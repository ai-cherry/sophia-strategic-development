import React, { useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import EnhancedUnifiedDashboard from './components/dashboard/EnhancedUnifiedDashboard';
import { KnowledgeLayout } from './components/knowledge/KnowledgeLayout';
import { DocumentsPage } from './pages/knowledge/DocumentsPage';
import { DiscoveryQueuePage } from './pages/knowledge/DiscoveryQueuePage';
import { CurationChatPage } from './pages/knowledge/CurationChatPage';
import { KnowledgeAnalyticsPage } from './pages/knowledge/KnowledgeAnalyticsPage';
import { KnowledgeSearchPage } from './pages/knowledge/KnowledgeSearchPage';
import { KnowledgeSettingsPage } from './pages/knowledge/KnowledgeSettingsPage';
import './styles/globals.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
    },
  },
});

function App() {
  useEffect(() => {
    // Apply dark theme by default
    document.documentElement.classList.add('dark');
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gray-950 text-gray-50">
          <Routes>
            {/* Dashboard routes */}
            <Route path="/" element={<EnhancedUnifiedDashboard />} />
            <Route path="/dashboard" element={<EnhancedUnifiedDashboard />} />

            {/* Knowledge Base routes */}
            <Route path="/knowledge" element={<KnowledgeLayout />}>
              <Route index element={<DocumentsPage />} />
              <Route path="discovery" element={<DiscoveryQueuePage />} />
              <Route path="curation" element={<CurationChatPage />} />
              <Route path="analytics" element={<KnowledgeAnalyticsPage />} />
              <Route path="search" element={<KnowledgeSearchPage />} />
              <Route path="settings" element={<KnowledgeSettingsPage />} />
            </Route>

            {/* Default redirect */}
            <Route path="/" element={<Navigate to="/dashboard" />} />
          </Routes>
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;

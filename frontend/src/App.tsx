import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import UnifiedDashboard from './components/dashboard/UnifiedDashboard';
import { KnowledgeLayout } from './components/knowledge/KnowledgeLayout';
import { DocumentsPage } from './pages/knowledge/DocumentsPage';
import { DiscoveryQueuePage } from './pages/knowledge/DiscoveryQueuePage';
import { CurationChatPage } from './pages/knowledge/CurationChatPage';
import { KnowledgeAnalyticsPage } from './pages/knowledge/KnowledgeAnalyticsPage';
import { KnowledgeSearchPage } from './pages/knowledge/KnowledgeSearchPage';
import { KnowledgeSettingsPage } from './pages/knowledge/KnowledgeSettingsPage';

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        {/* Dashboard routes */}
        <Route path="/dashboard" element={<UnifiedDashboard />} />

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
    </Router>
  );
};

export default App;

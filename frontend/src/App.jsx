import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ErrorBoundary } from './components/ErrorBoundary';
import UnifiedDashboardLayout from './components/shared/UnifiedDashboardLayout';
import EnhancedCEODashboard from './components/dashboard/EnhancedCEODashboard';
import EnhancedKnowledgeDashboard from './components/dashboard/EnhancedKnowledgeDashboard';
import EnhancedProjectDashboard from './components/dashboard/EnhancedProjectDashboard';
import './App.css';

// Main App Component with Full Dashboard
const App = () => {
  return (
    <ErrorBoundary>
      <Router>
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
          <Routes>
            {/* Redirect root to CEO dashboard */}
            <Route path="/" element={<Navigate to="/dashboard/ceo" replace />} />
            
            {/* Dashboard routes with unified layout */}
            <Route path="/dashboard" element={<UnifiedDashboardLayout />}>
              <Route path="ceo" element={<EnhancedCEODashboard />} />
              <Route path="knowledge" element={<EnhancedKnowledgeDashboard />} />
              <Route path="projects" element={<EnhancedProjectDashboard />} />
              {/* Default dashboard route */}
              <Route index element={<Navigate to="ceo" replace />} />
            </Route>
            
            {/* Fallback route */}
            <Route path="*" element={<Navigate to="/dashboard/ceo" replace />} />
          </Routes>
        </div>
      </Router>
    </ErrorBoundary>
  );
};

export default App;


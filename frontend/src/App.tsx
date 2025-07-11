import React from 'react';
import UnifiedChatDashboard from './components/UnifiedChatDashboard';
import ErrorBoundary from './components/ErrorBoundary';

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <UnifiedChatDashboard />
    </ErrorBoundary>
  );
};

export default App;

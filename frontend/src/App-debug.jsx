import React from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import { ErrorBoundary } from './components/ErrorBoundary';

// Simple test components
const TestHomePage = () => {
  const navigate = useNavigate();
  
  return (
    <div style={{ padding: '20px' }}>
      <h1>Sophia AI - Debug Mode</h1>
      <p>Testing basic routing and navigation</p>
      <button onClick={() => navigate('/test')}>Go to Test Page</button>
    </div>
  );
};

const TestPage = () => {
  return (
    <div style={{ padding: '20px' }}>
      <h1>Test Page</h1>
      <p>This is a test page to verify routing works.</p>
    </div>
  );
};

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/" element={<TestHomePage />} />
            <Route path="/test" element={<TestPage />} />
          </Routes>
        </div>
      </Router>
    </ErrorBoundary>
  );
}

export default App;


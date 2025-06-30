import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import { ErrorBoundary } from './components/ErrorBoundary';
import UnifiedChatInterface from './components/chat/UnifiedChatInterface';
import './App.css';

// Simplified UnifiedDashboard with integrated chat
const SimpleUnifiedDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  
  return (
    <div style={{ padding: '20px', minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
      <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
        <h1 style={{ color: '#333', marginBottom: '10px' }}>🚀 Sophia AI Unified Dashboard</h1>
        <p style={{ color: '#666' }}>Consolidated Executive Command Center</p>
        
        {/* Tab Navigation */}
        <div style={{ marginTop: '20px', borderBottom: '1px solid #e0e0e0' }}>
          <div style={{ display: 'flex', gap: '20px' }}>
            {['overview', 'analytics', 'chat'].map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                style={{
                  padding: '10px 20px',
                  border: 'none',
                  background: 'none',
                  borderBottom: activeTab === tab ? '2px solid #8b5cf6' : '2px solid transparent',
                  color: activeTab === tab ? '#8b5cf6' : '#666',
                  fontWeight: activeTab === tab ? 'bold' : 'normal',
                  cursor: 'pointer',
                  textTransform: 'capitalize'
                }}
              >
                {tab === 'chat' ? '💬 AI Assistant' : tab === 'analytics' ? '📊 Analytics' : '📈 Overview'}
              </button>
            ))}
          </div>
        </div>
      </div>
      
      {/* Tab Content */}
      {activeTab === 'overview' && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginBottom: '20px' }}>
            <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', border: '1px solid #e0e0e0' }}>
              <h3 style={{ color: '#333', marginBottom: '10px' }}>💰 Monthly Revenue</h3>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#333' }}>$2.1M</div>
              <div style={{ color: '#10b981', fontSize: '14px' }}>↗ +3.2% from last month</div>
            </div>
            
            <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', border: '1px solid #e0e0e0' }}>
              <h3 style={{ color: '#333', marginBottom: '10px' }}>👥 Active Agents</h3>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#333' }}>48</div>
              <div style={{ color: '#10b981', fontSize: '14px' }}>↗ +5 from last month</div>
            </div>
            
            <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', border: '1px solid #e0e0e0' }}>
              <h3 style={{ color: '#333', marginBottom: '10px' }}>✅ Success Rate</h3>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#333' }}>94.2%</div>
              <div style={{ color: '#ef4444', fontSize: '14px' }}>↘ -0.5% from last month</div>
            </div>
            
            <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', border: '1px solid #e0e0e0' }}>
              <h3 style={{ color: '#333', marginBottom: '10px' }}>📊 API Calls</h3>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#333' }}>1.2B</div>
              <div style={{ color: '#10b981', fontSize: '14px' }}>↗ +12% from last month</div>
            </div>
          </div>
          
          <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', border: '1px solid #e0e0e0' }}>
            <h3 style={{ color: '#333', marginBottom: '15px' }}>🤖 Agno Performance</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '15px' }}>
              <div>
                <div style={{ fontSize: '12px', color: '#666' }}>Avg Instantiation</div>
                <div style={{ fontSize: '18px', fontWeight: 'bold' }}>245μs</div>
              </div>
              <div>
                <div style={{ fontSize: '12px', color: '#666' }}>Pool Size</div>
                <div style={{ fontSize: '18px', fontWeight: 'bold' }}>12 / 20</div>
              </div>
            </div>
            <div style={{ marginTop: '15px', padding: '10px', backgroundColor: '#f8f9fa', borderRadius: '4px', fontSize: '12px', color: '#666' }}>
              Agno-powered agents are 5000x faster than legacy implementations
            </div>
          </div>
        </>
      )}
      
      {activeTab === 'analytics' && (
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', border: '1px solid #e0e0e0' }}>
          <h3 style={{ color: '#333', marginBottom: '15px' }}>📊 Advanced Analytics</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
            <div>
              <h4 style={{ color: '#333', marginBottom: '10px' }}>Cost Analysis</h4>
              <div style={{ padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span>OpenAI GPT-4</span>
                  <span>$8.50</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span>Portkey Gateway</span>
                  <span>$2.30</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 'bold', borderTop: '1px solid #ddd', paddingTop: '8px' }}>
                  <span>Total</span>
                  <span>$10.80</span>
                </div>
              </div>
            </div>
            
            <div>
              <h4 style={{ color: '#333', marginBottom: '10px' }}>Usage Trends</h4>
              <div style={{ padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
                <div style={{ marginBottom: '8px' }}>
                  <div style={{ fontSize: '12px', color: '#666' }}>Peak Usage</div>
                  <div style={{ fontSize: '16px', fontWeight: 'bold' }}>2:00 PM - 4:00 PM</div>
                </div>
                <div style={{ marginBottom: '8px' }}>
                  <div style={{ fontSize: '12px', color: '#666' }}>Most Active Mode</div>
                  <div style={{ fontSize: '16px', fontWeight: 'bold' }}>Sophia AI (65%)</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {activeTab === 'chat' && (
        <div style={{ backgroundColor: 'white', borderRadius: '8px', border: '1px solid #e0e0e0', overflow: 'hidden' }}>
          <UnifiedChatInterface
            mode="sophia"
            height="600px"
            showModeSelector={true}
            showSettings={true}
            apiEndpoint="/api/v1/chat"
          />
        </div>
      )}
    </div>
  );
};

// Home Page Component
const HomePage = () => {
  const navigate = useNavigate();
  
  return (
    <div style={{ padding: '40px', textAlign: 'center', minHeight: '100vh', backgroundColor: '#f9fafb' }}>
      <div style={{ maxWidth: '800px', margin: '0 auto' }}>
        <h1 style={{ fontSize: '48px', fontWeight: 'bold', color: '#1f2937', marginBottom: '20px' }}>
          🧠 Sophia AI
        </h1>
        <p style={{ fontSize: '20px', color: '#6b7280', marginBottom: '40px' }}>
          Pay Ready Business Intelligence Platform
        </p>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginTop: '40px' }}>
          <button 
            onClick={() => navigate('/dashboard/unified')}
            style={{ 
              padding: '20px', 
              backgroundColor: '#8b5cf6', 
              color: 'white', 
              border: 'none', 
              borderRadius: '8px', 
              fontSize: '16px', 
              fontWeight: 'bold',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
            onMouseOver={(e) => e.target.style.backgroundColor = '#7c3aed'}
            onMouseOut={(e) => e.target.style.backgroundColor = '#8b5cf6'}
          >
            🚀 Launch Unified Dashboard
          </button>
          
          <button 
            onClick={() => navigate('/chat')}
            style={{ 
              padding: '20px', 
              backgroundColor: '#10b981', 
              color: 'white', 
              border: 'none', 
              borderRadius: '8px', 
              fontSize: '16px', 
              fontWeight: 'bold',
              cursor: 'pointer'
            }}
          >
            💬 Open Chat Interface
          </button>
          
          <button 
            onClick={() => navigate('/test')}
            style={{ 
              padding: '20px', 
              backgroundColor: '#f59e0b', 
              color: 'white', 
              border: 'none', 
              borderRadius: '8px', 
              fontSize: '16px', 
              fontWeight: 'bold',
              cursor: 'pointer'
            }}
          >
            🧪 Test Page
          </button>
        </div>
      </div>
    </div>
  );
};

const ChatPage = () => {
  const navigate = useNavigate();
  
  return (
    <div style={{ padding: '20px', minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ marginBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ color: '#333', margin: 0 }}>💬 Sophia AI Chat Interface</h1>
          <button 
            onClick={() => navigate('/')} 
            style={{ 
              padding: '10px 20px', 
              backgroundColor: '#6b7280', 
              color: 'white', 
              border: 'none', 
              borderRadius: '6px',
              cursor: 'pointer'
            }}
          >
            ← Back to Home
          </button>
        </div>
        
        <div style={{ backgroundColor: 'white', borderRadius: '8px', border: '1px solid #e0e0e0', overflow: 'hidden' }}>
          <UnifiedChatInterface
            mode="universal"
            height="700px"
            showModeSelector={true}
            showSettings={true}
            apiEndpoint="/api/v1/chat"
          />
        </div>
      </div>
    </div>
  );
};

const TestPage = () => {
  const navigate = useNavigate();
  
  return (
    <div style={{ padding: '20px' }}>
      <h1>Test Page</h1>
      <p>This is a test page to verify routing works.</p>
      <button onClick={() => navigate('/')} style={{ padding: '10px 20px', marginTop: '10px' }}>
        Back to Home
      </button>
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
            <Route path="/test" element={<TestPage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/dashboard/unified" element={<SimpleUnifiedDashboard />} />
          </Routes>
        </div>
      </Router>
    </ErrorBoundary>
  );
}

export default App;


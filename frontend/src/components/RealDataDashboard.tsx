import React, { useState, useEffect } from 'react';

interface HealthData {
  status: string;
  timestamp: string;
  version: string;
  environment: string;
  services: {
    api: {
      status: string;
      uptime_seconds: number;
      total_requests: number;
      success_rate: number;
    };
    chat: {
      status: string;
      active_sessions: number;
      conversation_count: number;
    };
    database: {
      status: string;
      type: string;
      note: string;
    };
  };
}

interface ChatMessage {
  id: string;
  message: string;
  response: string;
  timestamp: string;
}

const RealDataDashboard: React.FC = () => {
  const [healthData, setHealthData] = useState<HealthData | null>(null);
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState(0);

  // Fetch health data
  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const response = await fetch('http://localhost:8000/health');
        const data = await response.json();
        setHealthData(data);
      } catch (error) {
        console.error('Failed to fetch health data:', error);
      }
    };

    fetchHealth();
    const interval = setInterval(fetchHealth, 5000); // Update every 5 seconds

    return () => clearInterval(interval);
  }, []);

  // Send chat message
  const sendMessage = async () => {
    if (!currentMessage.trim()) return;
    
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: currentMessage }),
      });
      
      const data = await response.json();
      
      const newMessage: ChatMessage = {
        id: Date.now().toString(),
        message: currentMessage,
        response: data.response || JSON.stringify(data, null, 2),
        timestamp: new Date().toISOString()
      };
      
      setChatHistory(prev => [...prev, newMessage]);
      setCurrentMessage('');
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)',
      color: 'white',
      padding: '20px',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(10px)',
          borderRadius: '16px',
          padding: '24px',
          marginBottom: '24px',
          border: '1px solid rgba(255, 255, 255, 0.2)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h1 style={{ fontSize: '2.5rem', fontWeight: 'bold', margin: '0 0 8px 0' }}>
                Sophia AI - Real Data Dashboard
              </h1>
              <p style={{ color: 'rgba(255, 255, 255, 0.8)', margin: 0 }}>
                Phase 2.4 Advanced AI Orchestration • Live Backend Integration
              </p>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ 
                fontSize: '1.5rem', 
                fontWeight: 'bold', 
                color: healthData?.status === 'healthy' ? '#10b981' : '#ef4444'
              }}>
                {healthData?.status === 'healthy' ? '✅ OPERATIONAL' : '⚠️ DEGRADED'}
              </div>
              <div style={{ fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.6)' }}>
                {healthData?.environment} • v{healthData?.version}
              </div>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(10px)',
          borderRadius: '16px',
          padding: '24px',
          marginBottom: '24px',
          border: '1px solid rgba(255, 255, 255, 0.2)'
        }}>
          <div style={{ display: 'flex', borderBottom: '1px solid rgba(255, 255, 255, 0.2)', marginBottom: '24px' }}>
            {['System Status', 'AI Chat', 'Performance Metrics'].map((tab, index) => (
              <button
                key={index}
                onClick={() => setActiveTab(index)}
                style={{
                  background: 'none',
                  border: 'none',
                  padding: '12px 24px',
                  color: activeTab === index ? '#3b82f6' : 'rgba(255, 255, 255, 0.7)',
                  cursor: 'pointer',
                  fontSize: '1rem',
                  fontWeight: '500',
                  borderBottom: activeTab === index ? '2px solid #3b82f6' : '2px solid transparent',
                  transition: 'all 0.3s ease'
                }}
              >
                {tab}
              </button>
            ))}
          </div>

          {/* System Status Tab */}
          {activeTab === 0 && healthData && (
            <div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '16px' }}>
                Live System Health
              </h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
                {/* API Service */}
                <div style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  borderRadius: '12px',
                  padding: '20px',
                  border: '1px solid rgba(255, 255, 255, 0.1)'
                }}>
                  <h4 style={{ margin: '0 0 12px 0', color: '#3b82f6' }}>API Service</h4>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span>Status:</span>
                    <span style={{ color: healthData.services.api.status === 'healthy' ? '#10b981' : '#ef4444' }}>
                      {healthData.services.api.status}
                    </span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span>Uptime:</span>
                    <span>{formatUptime(healthData.services.api.uptime_seconds)}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span>Total Requests:</span>
                    <span>{healthData.services.api.total_requests}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Success Rate:</span>
                    <span style={{ color: '#10b981' }}>{healthData.services.api.success_rate}%</span>
                  </div>
                </div>

                {/* Chat Service */}
                <div style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  borderRadius: '12px',
                  padding: '20px',
                  border: '1px solid rgba(255, 255, 255, 0.1)'
                }}>
                  <h4 style={{ margin: '0 0 12px 0', color: '#10b981' }}>Chat Service</h4>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span>Status:</span>
                    <span style={{ color: healthData.services.chat.status === 'healthy' ? '#10b981' : '#ef4444' }}>
                      {healthData.services.chat.status}
                    </span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span>Active Sessions:</span>
                    <span>{healthData.services.chat.active_sessions}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Conversations:</span>
                    <span>{healthData.services.chat.conversation_count}</span>
                  </div>
                </div>

                {/* Database Service */}
                <div style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  borderRadius: '12px',
                  padding: '20px',
                  border: '1px solid rgba(255, 255, 255, 0.1)'
                }}>
                  <h4 style={{ margin: '0 0 12px 0', color: '#f59e0b' }}>Database</h4>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span>Status:</span>
                    <span style={{ color: healthData.services.database.status === 'healthy' ? '#10b981' : '#ef4444' }}>
                      {healthData.services.database.status}
                    </span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span>Type:</span>
                    <span>{healthData.services.database.type}</span>
                  </div>
                  <div style={{ fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.6)', marginTop: '8px' }}>
                    {healthData.services.database.note}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* AI Chat Tab */}
          {activeTab === 1 && (
            <div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '16px' }}>
                Live AI Chat Interface
              </h3>
              
              {/* Chat Input */}
              <div style={{ display: 'flex', gap: '12px', marginBottom: '24px' }}>
                <input
                  type="text"
                  value={currentMessage}
                  onChange={(e) => setCurrentMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                  placeholder="Ask Sophia AI anything..."
                  style={{
                    flex: 1,
                    background: 'rgba(255, 255, 255, 0.1)',
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    borderRadius: '8px',
                    padding: '12px 16px',
                    color: 'white',
                    fontSize: '1rem'
                  }}
                />
                <button
                  onClick={sendMessage}
                  disabled={isLoading}
                  style={{
                    background: 'linear-gradient(135deg, #3b82f6, #1d4ed8)',
                    border: 'none',
                    borderRadius: '8px',
                    color: 'white',
                    padding: '12px 24px',
                    fontSize: '1rem',
                    fontWeight: '600',
                    cursor: isLoading ? 'not-allowed' : 'pointer',
                    opacity: isLoading ? 0.6 : 1
                  }}
                >
                  {isLoading ? 'Sending...' : 'Send'}
                </button>
              </div>

              {/* Chat History */}
              <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
                {chatHistory.length === 0 ? (
                  <div style={{ textAlign: 'center', color: 'rgba(255, 255, 255, 0.6)', padding: '40px' }}>
                    No conversations yet. Start chatting with Sophia AI!
                  </div>
                ) : (
                  chatHistory.map((chat) => (
                    <div key={chat.id} style={{ marginBottom: '24px' }}>
                      <div style={{
                        background: 'rgba(59, 130, 246, 0.1)',
                        borderRadius: '12px',
                        padding: '16px',
                        marginBottom: '8px',
                        border: '1px solid rgba(59, 130, 246, 0.2)'
                      }}>
                        <strong style={{ color: '#3b82f6' }}>You:</strong> {chat.message}
                      </div>
                      <div style={{
                        background: 'rgba(16, 185, 129, 0.1)',
                        borderRadius: '12px',
                        padding: '16px',
                        border: '1px solid rgba(16, 185, 129, 0.2)'
                      }}>
                        <strong style={{ color: '#10b981' }}>Sophia AI:</strong> {chat.response}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'rgba(255, 255, 255, 0.5)', marginTop: '8px' }}>
                        {new Date(chat.timestamp).toLocaleString()}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {/* Performance Metrics Tab */}
          {activeTab === 2 && (
            <div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '16px' }}>
                Real-time Performance Metrics
              </h3>
              
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                <div style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  borderRadius: '12px',
                  padding: '20px',
                  textAlign: 'center',
                  border: '1px solid rgba(255, 255, 255, 0.1)'
                }}>
                  <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#10b981', marginBottom: '8px' }}>
                    {healthData?.services.api.success_rate || 0}%
                  </div>
                  <div style={{ fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.7)' }}>
                    Success Rate
                  </div>
                </div>

                <div style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  borderRadius: '12px',
                  padding: '20px',
                  textAlign: 'center',
                  border: '1px solid rgba(255, 255, 255, 0.1)'
                }}>
                  <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#3b82f6', marginBottom: '8px' }}>
                    {healthData?.services.api.total_requests || 0}
                  </div>
                  <div style={{ fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.7)' }}>
                    Total Requests
                  </div>
                </div>

                <div style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  borderRadius: '12px',
                  padding: '20px',
                  textAlign: 'center',
                  border: '1px solid rgba(255, 255, 255, 0.1)'
                }}>
                  <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#f59e0b', marginBottom: '8px' }}>
                    {healthData?.services.chat.conversation_count || 0}
                  </div>
                  <div style={{ fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.7)' }}>
                    Conversations
                  </div>
                </div>

                <div style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  borderRadius: '12px',
                  padding: '20px',
                  textAlign: 'center',
                  border: '1px solid rgba(255, 255, 255, 0.1)'
                }}>
                  <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#8b5cf6', marginBottom: '8px' }}>
                    {healthData ? formatUptime(healthData.services.api.uptime_seconds) : '0h 0m'}
                  </div>
                  <div style={{ fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.7)' }}>
                    Uptime
                  </div>
                </div>
              </div>

              <div style={{ marginTop: '24px' }}>
                <h4 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '16px' }}>
                  System Information
                </h4>
                <div style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  borderRadius: '12px',
                  padding: '20px',
                  border: '1px solid rgba(255, 255, 255, 0.1)'
                }}>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                    <div>
                      <strong>Environment:</strong> {healthData?.environment}
                    </div>
                    <div>
                      <strong>Version:</strong> {healthData?.version}
                    </div>
                    <div>
                      <strong>Status:</strong> {healthData?.status}
                    </div>
                    <div>
                      <strong>Last Updated:</strong> {healthData ? new Date(healthData.timestamp).toLocaleString() : 'N/A'}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RealDataDashboard; 
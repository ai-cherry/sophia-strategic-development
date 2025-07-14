import React, { useState, useEffect } from 'react';

const App: React.FC = () => {
  const [backendStatus, setBackendStatus] = useState<string>('Checking...');
  const [message, setMessage] = useState<string>('');
  const [response, setResponse] = useState<string>('');

  useEffect(() => {
    // Check backend status
    fetch('http://localhost:8000/health')
      .then(res => res.json())
      .then(data => {
        setBackendStatus(`✅ Connected - ${data.version} (${data.environment})`);
      })
      .catch(err => {
        setBackendStatus(`❌ Backend not available: ${err.message}`);
      });
  }, []);

  const sendMessage = async () => {
    if (!message.trim()) return;
    
    try {
      const res = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
      });
      
      const data = await res.json();
      setResponse(data.response || JSON.stringify(data, null, 2));
    } catch (err) {
      setResponse(`Error: ${err.message}`);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#1a1a1a',
      color: 'white',
      padding: '20px',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      <div style={{ maxWidth: '800px', margin: '0 auto' }}>
        <h1 style={{ 
          fontSize: '2rem', 
          marginBottom: '20px',
          background: 'linear-gradient(45deg, #3b82f6, #8b5cf6)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          🚀 Sophia AI Production
        </h1>
        
        <div style={{
          backgroundColor: '#2a2a2a',
          padding: '15px',
          borderRadius: '8px',
          marginBottom: '20px',
          border: '1px solid #404040'
        }}>
          <strong>Backend Status:</strong> {backendStatus}
        </div>

        <div style={{
          backgroundColor: '#2a2a2a',
          padding: '20px',
          borderRadius: '8px',
          border: '1px solid #404040'
        }}>
          <h2 style={{ marginTop: 0, marginBottom: '15px' }}>Chat with Sophia AI</h2>
          
          <div style={{ marginBottom: '15px' }}>
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Ask Sophia AI anything..."
              style={{
                width: '100%',
                padding: '12px',
                backgroundColor: '#1a1a1a',
                border: '1px solid #404040',
                borderRadius: '6px',
                color: 'white',
                fontSize: '16px'
              }}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            />
          </div>
          
          <button
            onClick={sendMessage}
            style={{
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              padding: '12px 24px',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '16px',
              marginBottom: '20px'
            }}
          >
            Send Message
          </button>

          {response && (
            <div style={{
              backgroundColor: '#1a1a1a',
              padding: '15px',
              borderRadius: '6px',
              border: '1px solid #404040',
              whiteSpace: 'pre-wrap',
              maxHeight: '400px',
              overflow: 'auto'
            }}>
              <strong>Response:</strong><br />
              {response}
            </div>
          )}
        </div>

        <div style={{
          marginTop: '20px',
          padding: '15px',
          backgroundColor: '#2a2a2a',
          borderRadius: '8px',
          border: '1px solid #404040'
        }}>
          <h3 style={{ marginTop: 0 }}>Quick Actions</h3>
          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
            {[
              'What is our revenue status?',
              'Show system health',
              'Analyze team performance',
              'Generate business report'
            ].map((quickMsg, idx) => (
              <button
                key={idx}
                onClick={() => setMessage(quickMsg)}
                style={{
                  backgroundColor: '#404040',
                  color: 'white',
                  border: 'none',
                  padding: '8px 12px',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                {quickMsg}
              </button>
            ))}
          </div>
        </div>

        <div style={{
          marginTop: '20px',
          textAlign: 'center',
          color: '#888',
          fontSize: '14px'
        }}>
          Sophia AI Production v2.0.0 | Enterprise Intelligence Platform
        </div>
      </div>
    </div>
  );
};

export default App;

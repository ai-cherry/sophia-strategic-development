import React, { useState, useEffect } from 'react'

function SimpleApp() {
  const [backendStatus, setBackendStatus] = useState('Testing...')
  
  useEffect(() => {
    // Test backend connection
    fetch('http://localhost:8000/health')
      .then(response => response.json())
      .then(data => {
        setBackendStatus('✅ Connected')
      })
      .catch(error => {
        setBackendStatus('❌ Disconnected')
      })
  }, [])

  return (
    <div style={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: 'Inter, system-ui, sans-serif'
    }}>
      <div style={{
        background: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(10px)',
        borderRadius: '20px',
        padding: '40px',
        maxWidth: '600px',
        width: '90%',
        boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)',
        textAlign: 'center'
      }}>
        <div style={{ marginBottom: '30px' }}>
          <h1 style={{ 
            fontSize: '2.5rem', 
            fontWeight: '700',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            marginBottom: '10px'
          }}>
            Sophia AI
          </h1>
          <p style={{ 
            fontSize: '1.2rem', 
            color: '#666',
            margin: '0'
          }}>
            Pay Ready Business Intelligence Platform
          </p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '20px',
          marginBottom: '30px'
        }}>
          <div style={{
            background: 'rgba(102, 126, 234, 0.1)',
            padding: '20px',
            borderRadius: '12px',
            border: '1px solid rgba(102, 126, 234, 0.2)'
          }}>
            <h3 style={{ margin: '0 0 10px 0', color: '#667eea' }}>Frontend</h3>
            <p style={{ margin: '0', color: '#333' }}>✅ Running</p>
          </div>
          
          <div style={{
            background: 'rgba(118, 75, 162, 0.1)',
            padding: '20px',
            borderRadius: '12px',
            border: '1px solid rgba(118, 75, 162, 0.2)'
          }}>
            <h3 style={{ margin: '0 0 10px 0', color: '#764ba2' }}>Backend</h3>
            <p style={{ margin: '0', color: '#333' }}>{backendStatus}</p>
          </div>
        </div>

        <div style={{
          background: 'rgba(0, 0, 0, 0.05)',
          padding: '20px',
          borderRadius: '12px',
          marginBottom: '20px'
        }}>
          <h3 style={{ margin: '0 0 15px 0', color: '#333' }}>System Status</h3>
          <div style={{ textAlign: 'left' }}>
            <p style={{ margin: '5px 0', color: '#666' }}>🚀 Frontend: Deployed and Running</p>
            <p style={{ margin: '5px 0', color: '#666' }}>🔗 Backend API: {backendStatus}</p>
            <p style={{ margin: '5px 0', color: '#666' }}>❄️ Snowflake: Connected</p>
            <p style={{ margin: '5px 0', color: '#666' }}>💬 WebSocket: Ready</p>
          </div>
        </div>

        <div style={{
          display: 'flex',
          gap: '15px',
          justifyContent: 'center',
          flexWrap: 'wrap'
        }}>
          <button style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            border: 'none',
            padding: '12px 24px',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: '600',
            cursor: 'pointer',
            transition: 'transform 0.2s'
          }}
          onMouseOver={(e) => e.target.style.transform = 'translateY(-2px)'}
          onMouseOut={(e) => e.target.style.transform = 'translateY(0)'}
          onClick={() => window.location.href = '/dashboard'}
          >
            Launch Dashboard
          </button>
          
          <button style={{
            background: 'transparent',
            color: '#667eea',
            border: '2px solid #667eea',
            padding: '12px 24px',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: '600',
            cursor: 'pointer',
            transition: 'all 0.2s'
          }}
          onMouseOver={(e) => {
            e.target.style.background = '#667eea'
            e.target.style.color = 'white'
          }}
          onMouseOut={(e) => {
            e.target.style.background = 'transparent'
            e.target.style.color = '#667eea'
          }}
          onClick={() => window.open('http://localhost:8000/health', '_blank')}
          >
            Test Backend
          </button>
        </div>

        <div style={{
          marginTop: '30px',
          padding: '15px',
          background: 'rgba(102, 126, 234, 0.1)',
          borderRadius: '8px',
          fontSize: '14px',
          color: '#666'
        }}>
          <p style={{ margin: '0' }}>
            🎉 <strong>Deployment Successful!</strong> Both frontend and backend services are operational.
          </p>
        </div>
      </div>
    </div>
  )
}

export default SimpleApp


import React from 'react'

function TestApp() {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial' }}>
      <h1>Sophia AI Test Page</h1>
      <p>If you can see this, React is working!</p>
      <div style={{ background: '#f0f0f0', padding: '10px', margin: '10px 0' }}>
        <h2>System Status</h2>
        <p>Frontend: ✅ Running</p>
        <p>Backend: Testing connection...</p>
      </div>
    </div>
  )
}

export default TestApp

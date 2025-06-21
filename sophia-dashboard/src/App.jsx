import React, { useState } from 'react'
import CEODashboard from './pages/CEODashboard'
import KnowledgeDashboard from './pages/KnowledgeDashboard'
import './App.css'

function App() {
  const [activeView, setActiveView] = useState('ceo') // 'ceo' or 'knowledge'

  const NavButton = ({ view, children }) => (
    <button
      onClick={() => setActiveView(view)}
      style={{
        padding: '10px 20px',
        fontSize: '16px',
        cursor: 'pointer',
        border: 'none',
        backgroundColor: activeView === view ? '#007bff' : '#f0f0f0',
        color: activeView === view ? 'white' : 'black',
        margin: '0 5px',
        borderRadius: '5px'
      }}
    >
      {children}
    </button>
  )

  return (
    <div>
      <header style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        padding: '1rem', 
        backgroundColor: '#fff', 
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        borderBottom: '1px solid #ddd'
      }}>
        <nav>
          <NavButton view="ceo">CEO Command Center</NavButton>
          <NavButton view="knowledge">Knowledge Admin</NavButton>
        </nav>
      </header>

      <main>
        {activeView === 'ceo' && <CEODashboard />}
        {activeView === 'knowledge' && <KnowledgeDashboard />}
      </main>
    </div>
  )
}

export default App

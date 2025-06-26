import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

// Simple error boundary component
function ErrorBoundary({ children }) {
  try {
    return children
  } catch (error) {
    console.error('Error in app:', error)
    return (
      <div style={{ padding: '20px', fontFamily: 'Arial' }}>
        <h1>Something went wrong</h1>
        <p>Please refresh the page or check the console for details.</p>
        <pre>{error.toString()}</pre>
      </div>
    )
  }
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </StrictMode>,
)


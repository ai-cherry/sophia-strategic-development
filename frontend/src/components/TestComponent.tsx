import React from 'react';

const TestComponent: React.FC = () => {
  return (
    <div style={{
      backgroundColor: 'red',
      color: 'white',
      padding: '20px',
      fontSize: '24px',
      textAlign: 'center',
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      <div>
        <h1>🚀 REACT IS WORKING!</h1>
        <p>This is a test component to verify React is mounting properly.</p>
        <p>If you can see this, React is working correctly.</p>
      </div>
    </div>
  );
};

export default TestComponent; 
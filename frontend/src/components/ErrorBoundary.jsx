/**
 * Error Boundary Component
 * 
 * Catches JavaScript errors in child components and displays fallback UI
 * instead of crashing the entire React app.
 */

import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render shows fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log error details
    console.error('Error Boundary caught an error:', error, errorInfo);
    this.setState({
      error,
      errorInfo
    });
  }

  render() {
    if (this.state.hasError) {
      // Fallback UI
      return (
        <div style={{
          padding: '40px',
          textAlign: 'center',
          background: '#fff',
          borderRadius: '8px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          margin: '20px'
        }}>
          <h2 style={{ color: '#dc3545', marginBottom: '16px' }}>
            ⚠️ Something went wrong
          </h2>
          <p style={{ color: '#666', marginBottom: '24px' }}>
            The application encountered an error. Please refresh the page to try again.
          </p>
          
          {this.state.error && (
            <details style={{ 
              textAlign: 'left', 
              background: '#f8f9fa', 
              padding: '16px', 
              borderRadius: '4px',
              marginTop: '16px'
            }}>
              <summary style={{ cursor: 'pointer', fontWeight: 'bold', marginBottom: '8px' }}>
                Error Details
              </summary>
              <pre style={{ 
                whiteSpace: 'pre-wrap', 
                fontSize: '12px',
                color: '#dc3545',
                overflowX: 'auto'
              }}>
                {this.state.error.toString()}
                {this.state.errorInfo && this.state.errorInfo.componentStack}
              </pre>
            </details>
          )}
          
          <button
            onClick={() => window.location.reload()}
            style={{
              marginTop: '24px',
              padding: '12px 24px',
              background: '#6366f1',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: '600'
            }}
          >
            Refresh Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;

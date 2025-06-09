import React, { useEffect, useState } from 'react';

const DebugComponent = () => {
  const [debugInfo, setDebugInfo] = useState({
    reactLoaded: false,
    apiReachable: false,
    trendDataFetch: false,
    jsErrors: []
  });

  useEffect(() => {
    // Mark React as loaded
    setDebugInfo(prev => ({ ...prev, reactLoaded: true }));

    // Test API connectivity
    const testAPI = async () => {
      try {
        const response = await fetch('/api/stats/health', {
          headers: {
            'X-API-Key': 'development_key_for_testing'
          }
        });
        if (response.ok) {
          setDebugInfo(prev => ({ ...prev, apiReachable: true }));
        }
      } catch (error) {
        console.error('API test failed:', error);
      }

      // Test trend data
      try {
        const trendResponse = await fetch('/api/data/trends?period=day&parameter=temperature&location=all', {
          headers: {
            'X-API-Key': 'development_key_for_testing'
          }
        });
        if (trendResponse.ok) {
          setDebugInfo(prev => ({ ...prev, trendDataFetch: true }));
        }
      } catch (error) {
        console.error('Trend API test failed:', error);
      }
    };

    testAPI();

    // Capture JS errors
    const originalError = console.error;
    console.error = (...args) => {
      setDebugInfo(prev => ({
        ...prev,
        jsErrors: [...prev.jsErrors, args.join(' ')]
      }));
      originalError.apply(console, args);
    };

    return () => {
      console.error = originalError;
    };
  }, []);

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      background: 'white',
      border: '2px solid red',
      padding: '10px',
      zIndex: 9999,
      fontSize: '12px',
      fontFamily: 'monospace'
    }}>
      <h3>Debug Info</h3>
      <p>React Loaded: {debugInfo.reactLoaded ? '✅' : '❌'}</p>
      <p>API Reachable: {debugInfo.apiReachable ? '✅' : '❌'}</p>
      <p>Trend Data: {debugInfo.trendDataFetch ? '✅' : '❌'}</p>
      
      {debugInfo.jsErrors.length > 0 && (
        <div>
          <h4>JS Errors:</h4>
          {debugInfo.jsErrors.slice(0, 3).map((error, index) => (
            <p key={index} style={{ color: 'red', fontSize: '10px' }}>
              {error.substring(0, 100)}...
            </p>
          ))}
        </div>
      )}
    </div>
  );
};

export default DebugComponent;

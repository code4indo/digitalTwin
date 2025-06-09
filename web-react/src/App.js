import React, { useState, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Footer from './components/Footer';
import Dashboard from './components/Dashboard';

const App = () => {
  const [isLoading, setIsLoading] = useState(true);
  
  // Simulasi loading aplikasi
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);
    
    return () => clearTimeout(timer);
  }, []);
  
  if (isLoading) {
    return (
      <div className="loading-screen">
        <div className="loading-container">
          <div className="loading-logo">
            <img src="/img/logo_dt.png" alt="Digital Twin Logo" />
          </div>
          <div className="loading-text">Memuat Digital Twin...</div>
          <div className="loading-spinner"></div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="app-container">
      <Header />
      
      <main>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          {/* Tambahkan route lain sesuai kebutuhan */}
          {/* <Route path="/analysis" element={<Analysis />} /> */}
          {/* <Route path="/settings" element={<Settings />} /> */}
        </Routes>
      </main>
      
      <Footer />
    </div>
  );
};

export default App;

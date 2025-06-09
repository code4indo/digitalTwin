import React, { useState, useEffect } from 'react';
import { fetchAlerts } from '../utils/api';

const AlertsPanel = () => {
  const [alerts, setAlerts] = useState([]);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Dummy data jika API belum siap atau gagal
  const dummyAlerts = [
    {
      id: 1,
      type: 'critical',
      message: 'Suhu di Ruang G5 meningkat drastis (+4.5°C dalam 30 menit)',
      timestamp: new Date(Date.now() - 15 * 60000).toISOString(),
      recommendation: 'Periksa AC di ruang G5, kemungkinan tidak berfungsi'
    },
    {
      id: 2,
      type: 'warning',
      message: 'Kelembapan di Ruang F3 di luar batas optimal (62%)',
      timestamp: new Date(Date.now() - 48 * 60000).toISOString(),
      recommendation: 'Sesuaikan pengaturan dehumidifier'
    },
    {
      id: 3,
      type: 'info',
      message: 'Jadwal pemeliharaan AC dalam 3 hari',
      timestamp: new Date(Date.now() - 120 * 60000).toISOString(),
      recommendation: 'Siapkan jadwal teknisi'
    }
  ];
  
  useEffect(() => {
    const loadAlerts = async () => {
      try {
        setLoading(true);
        const data = await fetchAlerts(filter);
        setAlerts(data || dummyAlerts);
        setError(null);
      } catch (err) {
        if (process.env.NODE_ENV === 'development') {
          console.error('Error fetching alerts:', err);
        }
        setAlerts(dummyAlerts);
        setError('Gagal memuat peringatan terbaru');
      } finally {
        setLoading(false);
      }
    };
    
    loadAlerts();
    
    // Refresh alerts every 3 minutes
    const interval = setInterval(loadAlerts, 3 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, [filter]);
  
  // Handle filter change
  const handleFilterChange = (e) => {
    setFilter(e.target.value);
  };
  
  // Format timestamp
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.round(diffMs / 60000);
    
    if (diffMins < 60) {
      return `${diffMins} menit yang lalu`;
    } else if (diffMins < 24 * 60) {
      const hours = Math.floor(diffMins / 60);
      return `${hours} jam yang lalu`;
    } else {
      const options = { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' };
      return date.toLocaleDateString('id-ID', options);
    }
  };
  
  return (
    <div className="card alerts">
      <div className="card-header">
        <h2>Peringatan & Rekomendasi</h2>
        <div className="alert-filter">
          <select 
            id="alert-filter" 
            value={filter} 
            onChange={handleFilterChange}
          >
            <option value="all">Semua</option>
            <option value="critical">Kritis</option>
            <option value="warning">Peringatan</option>
            <option value="info">Informasi</option>
          </select>
        </div>
      </div>
      
      {loading ? (
        <div className="loading-indicator">Memuat peringatan...</div>
      ) : error ? (
        <div className="error-message">{error}</div>
      ) : (
        <div className="alerts-list">
          {alerts.length === 0 ? (
            <div className="no-alerts">
              Tidak ada peringatan {filter !== 'all' ? `untuk filter "${filter}"` : ''}
            </div>
          ) : (
            alerts.map(alert => (
              <div key={alert.id} className={`alert-item ${alert.type}`}>
                <div className="alert-header">
                  <div className={`alert-icon ${alert.type}`}></div>
                  <div className="alert-time">{formatTime(alert.timestamp)}</div>
                </div>
                <div className="alert-content">
                  <div className="alert-message">{alert.message}</div>
                  {alert.recommendation && (
                    <div className="alert-recommendation">
                      <strong>Rekomendasi:</strong> {alert.recommendation}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default AlertsPanel;

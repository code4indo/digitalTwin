import React, { useState, useEffect } from 'react';
import { fetchLatestEnvironmentalStatus, fetchExternalWeatherData, fetchSystemHealth } from '../utils/api';

// Helper function untuk menentukan warna status kesehatan sistem
const getHealthStatusColor = (status) => {
  switch(status) {
    case 'Optimal':
      return '#28a745'; // Green - status sangat baik
    case 'Good':
      return '#17a2b8'; // Blue - status baik
    case 'Warning':
      return '#ffc107'; // Yellow/Amber - perlu perhatian
    case 'Critical':
      return '#dc3545'; // Red - perlu tindakan segera
    default:
      return '#6c757d'; // Gray untuk status loading atau tidak dikenal
  }
};

// Helper function untuk menentukan warna rasio perangkat aktif
const getDeviceRatioColor = (ratio) => {
  if (ratio > 0.9) return '#28a745'; // Green
  if (ratio >= 0.75) return '#17a2b8'; // Blue
  if (ratio >= 0.5) return '#ffc107'; // Yellow/Amber
  return '#dc3545'; // Red
};

// Helper function untuk mengekstrak rasio dari string activeDevices (contoh: "7/12" -> 0.5833)
const extractRatio = (activeDevicesStr) => {
  if (!activeDevicesStr || activeDevicesStr === '...') return 0;
  
  const parts = activeDevicesStr.split('/');
  if (parts.length !== 2) return 0;
  
  const active = parseInt(parts[0], 10);
  const total = parseInt(parts[1], 10);
  
  if (isNaN(active) || isNaN(total) || total === 0) return 0;
  return active / total;
};

// Simple tooltip component
const Tooltip = ({ children }) => {
  const [showTooltip, setShowTooltip] = useState(false);
  
  return (
    <div style={{ position: 'relative', display: 'inline-block', marginLeft: '5px', cursor: 'help' }}
         onMouseEnter={() => setShowTooltip(true)}
         onMouseLeave={() => setShowTooltip(false)}>
      <span style={{ 
        border: '1px solid #ccc', 
        borderRadius: '50%', 
        width: '16px', 
        height: '16px', 
        display: 'inline-flex', 
        justifyContent: 'center', 
        alignItems: 'center',
        fontSize: '12px',
        fontWeight: 'bold'
      }}>?</span>
      
      {showTooltip && (
        <div style={{ 
          position: 'absolute', 
          bottom: '100%', 
          left: '50%', 
          transform: 'translateX(-50%)', 
          backgroundColor: 'rgba(0, 0, 0, 0.8)', 
          color: 'white', 
          padding: '8px', 
          borderRadius: '4px',
          width: '220px',
          zIndex: 100,
          fontSize: '12px',
          lineHeight: '1.4',
          marginBottom: '5px'
        }}>
          {children}
          <div style={{ 
            position: 'absolute', 
            top: '100%', 
            left: '50%', 
            marginLeft: '-5px', 
            borderWidth: '5px', 
            borderStyle: 'solid', 
            borderColor: 'rgba(0, 0, 0, 0.8) transparent transparent transparent' 
          }}></div>
        </div>
      )}
    </div>
  );
};

// Helper component untuk menampilkan penjelasan status sistem
const StatusExplainer = ({ status }) => {
  // Mapping status ke penjelasan
  const explanations = {
    Optimal: 'Semua sistem bekerja dengan baik. Lebih dari 90% perangkat aktif.',
    Good: 'Sistem bekerja dengan baik. 75-90% perangkat aktif.',
    Warning: 'Perhatian dibutuhkan. 50-75% perangkat aktif.',
    Critical: 'Tindakan segera dibutuhkan! Kurang dari 50% perangkat aktif.',
    default: 'Memuat status sistem...'
  };
  
  // Mendapatkan penjelasan berdasarkan status
  const explanation = explanations[status] || explanations.default;
  
  return (
    <div style={{
      fontSize: '0.8em',
      marginTop: '8px',
      fontStyle: 'italic',
      color: '#666'
    }}>
      {explanation}
    </div>
  );
};

const EnvironmentalStatus = () => {
  const [environmentData, setEnvironmentData] = useState({
    temperature: { avg: '...', min: '...', max: '...' },
    humidity: { avg: '...', min: '...', max: '...' },
    weather: { status: 'Memuat...', externalTemp: '...' },
    system: { 
      health: 'Memuat...', 
      activeDevices: '...', 
      healthUpdated: false,
      activeDevicesUpdated: false,
      influxdbConnection: null,
      ratio: 0
    }
  });
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdateTime, setLastUpdateTime] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  // Function to fetch data as useCallback to avoid dependency warnings
  const fetchData = React.useCallback(async () => {
    try {
      setRefreshing(true);
      if (!lastUpdateTime) setLoading(true);
        
      // Fetch sensor data (temperature, humidity)
      const envData = await fetchLatestEnvironmentalStatus();
      
      // Fetch external weather data
      const weatherData = await fetchExternalWeatherData();
      
      // Fetch system health data
      const healthData = await fetchSystemHealth();
      
      // Validasi data yang diterima
      if (!healthData || !healthData.status) {
        console.error('Invalid health data received:', healthData);
        throw new Error('Invalid health data');
      }
      
      // Combine data
      setEnvironmentData({
        temperature: {
          avg: envData.temperature.average.toFixed(1),
          min: envData.temperature.min.toFixed(1),
          max: envData.temperature.max.toFixed(1)
        },
        humidity: {
          avg: envData.humidity.average.toFixed(0),
          min: envData.humidity.min.toFixed(0),
          max: envData.humidity.max.toFixed(0)
        },
        weather: {
          status: weatherData.condition || 'Cerah Berawan',
          externalTemp: weatherData.temperature.toFixed(1) || '29.8'
        },
        system: {
          health: healthData.status,
          healthUpdated: true, // Flag to indicate the data has been updated from API
          activeDevices: `${healthData.active_devices}/${healthData.total_devices}`,
          activeDevicesUpdated: true, // Flag to indicate the data has been updated from API
          influxdbConnection: healthData.influxdb_connection || 'unknown',
          ratio: healthData.ratio_active_to_total
        }
      });
      
      // Set last update time
      setLastUpdateTime(new Date());
      
      setLoading(false);
      setRefreshing(false);
    } catch (err) {
      console.error('Error fetching environmental data:', err);
      setError('Gagal memuat data lingkungan. Mencoba lagi dalam 30 detik.');
      setLoading(false);
      setRefreshing(false);
      
      // Retry after 30 seconds
      setTimeout(fetchData, 30000);
    }
  }, []);
  
  useEffect(() => {
    fetchData();
    
    // Refresh data every 5 minutes
    const interval = setInterval(fetchData, 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, [fetchData]);
  
  // Show loading/error state
  if (loading && !environmentData.temperature.avg) {
    return (
      <div className="card environmental-status">
        <h2>Status Iklim Mikro</h2>
        <div className="loading">Memuat data...</div>
      </div>
    );
  }
  
  // Format the last update time
  const formatUpdateTime = () => {
    if (!lastUpdateTime) return '';
    
    const date = new Date(lastUpdateTime);
    return `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`;
  };

  return (
    <div className="card environmental-status">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>Status Iklim Mikro</h2>
        <div>
          <button 
            onClick={fetchData} 
            disabled={refreshing}
            style={{
              padding: '6px 12px',
              backgroundColor: refreshing ? '#ccc' : '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: refreshing ? 'not-allowed' : 'pointer'
            }}
          >
            {refreshing ? 'Memperbarui...' : 'Perbarui Data'}
          </button>
          {lastUpdateTime && (
            <div style={{ fontSize: '0.8em', marginTop: '4px', textAlign: 'right' }}>
              Terakhir diperbarui: {formatUpdateTime()}
            </div>
          )}
        </div>
      </div>
      {error && <div className="error-message">{error}</div>}
      <div className="status-grid">
        {/* Temperature Status */}
        <div className="status-card">
          <div className="status-icon temperature"></div>
          <div className="status-details">
            <h3>Suhu Rata-rata</h3>
            <div className="status-value" id="avg-temperature">
              {environmentData.temperature.avg}°C
            </div>
            <div className="status-range">
              Min: <span id="min-temperature">{environmentData.temperature.min}°C</span> | 
              Max: <span id="max-temperature">{environmentData.temperature.max}°C</span>
            </div>
          </div>
        </div>
        
        {/* Humidity Status */}
        <div className="status-card">
          <div className="status-icon humidity"></div>
          <div className="status-details">
            <h3>Kelembapan Rata-rata</h3>
            <div className="status-value" id="avg-humidity">
              {environmentData.humidity.avg}%
            </div>
            <div className="status-range">
              Min: <span id="min-humidity">{environmentData.humidity.min}%</span> | 
              Max: <span id="max-humidity">{environmentData.humidity.max}%</span>
            </div>
          </div>
        </div>
        
        {/* External Weather */}
        <div className="status-card">
          <div className="status-icon external"></div>
          <div className="status-details">
            <h3>Cuaca Eksternal (BMKG)</h3>
            <div className="status-value weather-status" id="weather-status">
              {environmentData.weather.status}
            </div>
            <div className="weather-details" id="external-temperature">
              Suhu Luar: {environmentData.weather.externalTemp}°C
            </div>
          </div>
        </div>
        
        {/* System Health */}
        <div className="status-card">
          <div className="status-icon health"></div>
          <div className="status-details">
            <h3>Status Kesehatan Sistem</h3>
            <div 
              className={`status-value health-status ${environmentData.system.healthUpdated ? 'updated-data' : ''}`} 
              id="system-health" 
              style={{
                color: '#fff',
                backgroundColor: getHealthStatusColor(environmentData.system.health),
                padding: '4px 8px',
                borderRadius: '4px',
                display: 'inline-block'
              }}>
              {environmentData.system.health}
              {environmentData.system.healthUpdated && <small style={{fontSize: '0.7em', marginLeft: '5px'}}> ✓</small>}
            </div>
            {environmentData.system.health !== 'Memuat...' && <StatusExplainer status={environmentData.system.health} />}
            <div className="health-details">
              Perangkat Aktif: <span id="active-devices" className={environmentData.system.activeDevicesUpdated ? 'updated-data' : ''}>
                {environmentData.system.activeDevices}
                {environmentData.system.activeDevicesUpdated && <small style={{fontSize: '0.7em', marginLeft: '2px'}}> ✓</small>}
              </span>
              
              {/* Progressive bar for device ratio */}
              {environmentData.system.activeDevices !== '...' && (
                <div style={{marginTop: '6px'}}>
                  <div style={{
                    width: '100%',
                    backgroundColor: '#e9ecef',
                    borderRadius: '4px',
                    height: '8px',
                    marginTop: '4px'
                  }}>
                    <div style={{
                      width: `${extractRatio(environmentData.system.activeDevices) * 100}%`,
                      backgroundColor: getDeviceRatioColor(extractRatio(environmentData.system.activeDevices)),
                      height: '8px',
                      borderRadius: '4px',
                      transition: 'width 0.3s ease'
                    }}></div>
                  </div>
                </div>
              )}
              
              {/* InfluxDB Connection Status */}
              {environmentData.system.influxdbConnection && (
                <div style={{marginTop: '8px', fontSize: '0.85em'}}>
                  InfluxDB: 
                  <span style={{
                    color: environmentData.system.influxdbConnection === 'connected' ? '#28a745' : '#dc3545',
                    fontWeight: 'bold',
                    marginLeft: '5px'
                  }}>
                    {environmentData.system.influxdbConnection === 'connected' ? 'Terhubung ✓' : 'Terputus ✗'}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnvironmentalStatus;

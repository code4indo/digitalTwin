import React, { useState, useEffect } from 'react';
import { fetchLatestEnvironmentalStatus, fetchExternalWeatherData, fetchSystemHealth } from '../utils/api';

// Debug flag untuk development
const DEBUG_ENV = process.env.NODE_ENV === 'development' && process.env.REACT_APP_DEBUG_ENV === 'true';

// Helper function untuk menentukan warna status kesehatan sistem
const getHealthStatusColor = (status) => {
  // Debugging untuk melihat status yang masuk
  if (DEBUG_ENV) console.log('Status received for color:', status);
  
  // Normalize status untuk konsistensi
  const normalizedStatus = status ? status.charAt(0).toUpperCase() + status.slice(1).toLowerCase() : '';
  if (DEBUG_ENV) console.log('Normalized status for color:', normalizedStatus);
  
  switch(normalizedStatus) {
    case 'Optimal':
      return '#28a745'; // Green - status sangat baik
    case 'Good':
      return '#17a2b8'; // Blue - status baik
    case 'Warning':
      return '#ffc107'; // Yellow/Amber - perlu perhatian
    case 'Critical':
      return '#dc3545'; // Red - perlu tindakan segera
    default:
      if (DEBUG_ENV) console.log('Status tidak cocok dengan kasus yang ada, menggunakan default color');
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
  if (DEBUG_ENV) console.log('Status received for explanation:', status);
  
  // Normalize status untuk konsistensi
  const normalizedStatus = status ? status.charAt(0).toUpperCase() + status.slice(1).toLowerCase() : '';
  if (DEBUG_ENV) console.log('Normalized status for explanation:', normalizedStatus);
  
  // Mapping status ke penjelasan
  const explanations = {
    Optimal: 'Semua sistem bekerja dengan baik. Lebih dari 90% perangkat aktif.',
    Good: 'Sistem bekerja dengan baik. 75-90% perangkat aktif.',
    Warning: 'Perhatian dibutuhkan. 50-75% perangkat aktif.',
    Critical: 'Tindakan segera dibutuhkan! Kurang dari 50% perangkat aktif.',
    default: 'Memuat status sistem...'
  };
  
  // Mendapatkan penjelasan berdasarkan status yang dinormalisasi
  const explanation = explanations[normalizedStatus] || explanations.default;
  
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
      
      // Hapus error sebelumnya jika ada
      setError(null);
        
      if (DEBUG_ENV) console.log('Fetching environmental data...');
      
      // Fetch sensor data (temperature, humidity)
      let envData;
      try {
        envData = await fetchLatestEnvironmentalStatus();
        if (DEBUG_ENV) console.log('Environmental data received:', envData);
      } catch (envError) {
        if (DEBUG_ENV) console.error('Error fetching environmental data:', envError);
        throw new Error(`Data lingkungan gagal dimuat: ${envError.message}`);
      }
      
      // Fetch external weather data
      let weatherData;
      try {
        weatherData = await fetchExternalWeatherData();
        if (DEBUG_ENV) console.log('Weather data received:', weatherData);
      } catch (weatherError) {
        if (DEBUG_ENV) console.warn('Warning: Could not fetch weather data:', weatherError);
        // Gunakan data dummy untuk cuaca jika gagal
        weatherData = { condition: 'Tidak Tersedia', temperature: 30.0 };
      }
      
      // Fetch system health data
      let healthData;
      try {
        healthData = await fetchSystemHealth();
        if (DEBUG_ENV) console.log('Health data received in component:', healthData);
      } catch (healthError) {
        if (DEBUG_ENV) console.error('Error fetching health data:', healthError);
        // Gunakan data dummy untuk sistem kesehatan jika gagal
        healthData = { 
          status: 'Unknown', 
          active_devices: 0, 
          total_devices: 0,
          ratio_active_to_total: 0,
          influxdb_connection: 'unknown'
        };
      }
      
      // Validasi data kesehatan sistem
      const normalizedStatus = healthData && healthData.status ? 
        healthData.status.charAt(0).toUpperCase() + healthData.status.slice(1).toLowerCase() : 'Unknown';
      if (DEBUG_ENV) console.log('Normalized status in component:', normalizedStatus);
      
      // Validasi data suhu dan kelembapan
      if (!envData || !envData.temperature || !envData.humidity) {
        if (DEBUG_ENV) console.warn('Invalid environmental data received, using fallback values');
        envData = { 
          temperature: { average: 22.5, min: 19.2, max: 24.8 },
          humidity: { average: 48, min: 42, max: 53 }
        };
      }
      
      // Validasi dan format nilai suhu
      const tempAvg = typeof envData.temperature.average === 'number' ? envData.temperature.average.toFixed(1) : '0.0';
      const tempMin = typeof envData.temperature.min === 'number' ? envData.temperature.min.toFixed(1) : '0.0';
      const tempMax = typeof envData.temperature.max === 'number' ? envData.temperature.max.toFixed(1) : '0.0';
      
      // Validasi dan format nilai kelembapan
      const humAvg = typeof envData.humidity.average === 'number' ? envData.humidity.average.toFixed(0) : '0';
      const humMin = typeof envData.humidity.min === 'number' ? envData.humidity.min.toFixed(0) : '0';
      const humMax = typeof envData.humidity.max === 'number' ? envData.humidity.max.toFixed(0) : '0';
      
      if (DEBUG_ENV) {
        console.log('Processed temperature values:', { tempAvg, tempMin, tempMax });
        console.log('Processed humidity values:', { humAvg, humMin, humMax });
      }
      
      // Combine data
      setEnvironmentData({
        temperature: {
          avg: tempAvg,
          min: tempMin,
          max: tempMax
        },
        humidity: {
          avg: humAvg,
          min: humMin,
          max: humMax
        },
        weather: {
          status: weatherData.condition || 'Cerah Berawan',
          externalTemp: typeof weatherData.temperature === 'number' ? weatherData.temperature.toFixed(1) : '29.8'
        },
        system: {
          health: normalizedStatus, // Menggunakan status yang sudah dinormalisasi
          healthUpdated: true, // Flag to indicate the data has been updated from API
          activeDevices: healthData.active_devices !== undefined ? `${healthData.active_devices}/${healthData.total_devices}` : '...',
          activeDevicesUpdated: true, // Flag to indicate the data has been updated from API
          influxdbConnection: healthData.influxdb_connection || 'unknown',
          ratio: healthData.ratio_active_to_total || 0
        }
      });
      
      // Set last update time
      setLastUpdateTime(new Date());
      
      setLoading(false);
      setRefreshing(false);
    } catch (err) {
      if (DEBUG_ENV) console.error('Error fetching environmental data:', err);
      
      // Informasi error yang lebih detail
      let errorMessage = 'Gagal memuat data lingkungan. Mencoba lagi dalam 30 detik.';
      
      // Jika ada respons error dari API, tampilkan detailnya
      if (err.response) {
        if (DEBUG_ENV) {
          console.error('Error response:', err.response.data);
          console.error('Error status:', err.response.status);
        }
        errorMessage += ` (Status: ${err.response.status})`;
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
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
  if (loading && (!environmentData.temperature || !environmentData.temperature.avg || environmentData.temperature.avg === '...')) {
    return (
      <div className="card environmental-status">
        <h2>Status Iklim Mikro</h2>
        <div className="loading">Memuat data...</div>
      </div>
    );
  }
  
  // Show error state if there is an error
  if (error) {
    return (
      <div className="card environmental-status">
        <h2>Status Iklim Mikro</h2>
        <div className="error" style={{ padding: '15px', backgroundColor: '#ffebee', color: '#c62828', borderRadius: '4px', marginBottom: '15px' }}>
          {error}
        </div>
        <button 
          onClick={fetchData} 
          style={{
            padding: '6px 12px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Coba Lagi
        </button>
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
              {environmentData?.temperature?.avg || '...'}°C
            </div>
            <div className="status-range">
              Min: <span id="min-temperature">{environmentData?.temperature?.min || '...'}°C</span> | 
              Max: <span id="max-temperature">{environmentData?.temperature?.max || '...'}°C</span>
            </div>
          </div>
        </div>
        
        {/* Humidity Status */}
        <div className="status-card">
          <div className="status-icon humidity"></div>
          <div className="status-details">
            <h3>Kelembapan Rata-rata</h3>
            <div className="status-value" id="avg-humidity">
              {environmentData?.humidity?.avg || '...'}%
            </div>
            <div className="status-range">
              Min: <span id="min-humidity">{environmentData?.humidity?.min || '...'}%</span> | 
              Max: <span id="max-humidity">{environmentData?.humidity?.max || '...'}%</span>
            </div>
          </div>
        </div>
        
        {/* External Weather */}
        <div className="status-card">
          <div className="status-icon external"></div>
          <div className="status-details">
            <h3>Cuaca Eksternal (BMKG)</h3>
            <div className="status-value weather-status" id="weather-status">
              {environmentData?.weather?.status || 'Memuat...'}
            </div>
            <div className="weather-details" id="external-temperature">
              Suhu Luar: {environmentData?.weather?.externalTemp || '...'}°C
            </div>
          </div>
        </div>
        
        {/* System Health */}
        <div className="status-card">
          <div className="status-icon health"></div>
          <div className="status-details">
            <h3>Status Kesehatan Sistem</h3>
            <div 
              className={`status-value health-status ${environmentData?.system?.healthUpdated ? 'updated-data' : ''}`} 
              id="system-health" 
              style={{
                color: '#fff',
                backgroundColor: getHealthStatusColor(environmentData?.system?.health),
                padding: '4px 8px',
                borderRadius: '4px',
                display: 'inline-block'
              }}>
              {environmentData?.system?.health || 'Memuat...'}
              {environmentData?.system?.healthUpdated && <small style={{fontSize: '0.7em', marginLeft: '5px'}}> ✓</small>}
            </div>
            {environmentData?.system?.health !== 'Memuat...' && <StatusExplainer status={environmentData?.system?.health} />}
            <div className="health-details">
              Perangkat Aktif: <span id="active-devices" className={environmentData?.system?.activeDevicesUpdated ? 'updated-data' : ''}>
                {environmentData?.system?.activeDevices || '...'}
                {environmentData?.system?.activeDevicesUpdated && <small style={{fontSize: '0.7em', marginLeft: '2px'}}> ✓</small>}
              </span>
              
              {/* Progressive bar for device ratio */}
              {environmentData?.system?.activeDevices !== '...' && (
                <div style={{marginTop: '6px'}}>
                  <div style={{
                    width: '100%',
                    backgroundColor: '#e9ecef',
                    borderRadius: '4px',
                    height: '8px',
                    marginTop: '4px'
                  }}>
                    <div style={{
                      width: `${extractRatio(environmentData?.system?.activeDevices) * 100}%`,
                      backgroundColor: getDeviceRatioColor(extractRatio(environmentData?.system?.activeDevices)),
                      height: '8px',
                      borderRadius: '4px',
                      transition: 'width 0.3s ease'
                    }}></div>
                  </div>
                </div>
              )}
              
              {/* InfluxDB Connection Status */}
              {environmentData?.system?.influxdbConnection && (
                <div style={{marginTop: '8px', fontSize: '0.85em'}}>
                  InfluxDB: 
                  <span style={{
                    color: environmentData?.system?.influxdbConnection === 'connected' ? '#28a745' : '#dc3545',
                    fontWeight: 'bold',
                    marginLeft: '5px'
                  }}>
                    {environmentData?.system?.influxdbConnection === 'connected' ? 'Terhubung ✓' : 'Terputus ✗'}
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

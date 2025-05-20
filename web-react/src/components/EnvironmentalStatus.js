import React, { useState, useEffect } from 'react';
import { fetchLatestEnvironmentalStatus, fetchExternalWeatherData } from '../utils/api';

const EnvironmentalStatus = () => {
  const [environmentData, setEnvironmentData] = useState({
    temperature: { avg: '22.5', min: '19.2', max: '24.8' },
    humidity: { avg: '48', min: '42', max: '53' },
    weather: { status: 'Cerah Berawan', externalTemp: '29.8' },
    system: { health: 'Optimal', activeDevices: '12/12' }
  });
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch sensor data (temperature, humidity)
        const envData = await fetchLatestEnvironmentalStatus();
        
        // Fetch external weather data
        const weatherData = await fetchExternalWeatherData();
        
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
          system: envData.system || { health: 'Optimal', activeDevices: '12/12' }
        });
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching environmental data:', err);
        setError('Gagal memuat data lingkungan. Mencoba lagi dalam 30 detik.');
        setLoading(false);
        
        // Retry after 30 seconds
        setTimeout(fetchData, 30000);
      }
    };
    
    fetchData();
    
    // Refresh data every 5 minutes
    const interval = setInterval(fetchData, 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, []);
  
  // Show loading/error state
  if (loading && !environmentData.temperature.avg) {
    return (
      <div className="card environmental-status">
        <h2>Status Iklim Mikro</h2>
        <div className="loading">Memuat data...</div>
      </div>
    );
  }
  
  return (
    <div className="card environmental-status">
      <h2>Status Iklim Mikro</h2>
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
            <div className="status-value health-status" id="system-health">
              {environmentData.system.health}
            </div>
            <div className="health-details">
              Perangkat Aktif: <span id="active-devices">{environmentData.system.activeDevices}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnvironmentalStatus;

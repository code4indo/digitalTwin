import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import './ComponentStyles.css';

/**
 * Komponen untuk menampilkan visualisasi data lingkungan ruangan dari Grafana
 * 
 * @param {Object} props - Props untuk komponen
 * @param {string} props.roomId - ID ruangan (contoh: F2, G3, dsb)
 * @param {number} props.height - Tinggi iframe dalam piksel (default: 300)
 * @param {string} props.theme - Tema untuk Grafana (light atau dark)
 * @returns {JSX.Element} Komponen chart ruangan
 */
const RoomEnvironmentalChart = ({ roomId, height = 300, theme = 'light' }) => {
  const [grafanaUrl, setGrafanaUrl] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!roomId) {
      setError('Room ID is required');
      setIsLoading(false);
      return;
    }

    try {
      // Konfigurasi URL Grafana - menggunakan URL lengkap sesuai dengan kebutuhan
      // Grafana dapat diakses dari proxy internal (/grafana) atau dari URL langsung (http://10.13.0.4:3001)
      const isProduction = process.env.NODE_ENV === 'production';
      
      // Di production, kita gunakan proxy path yang dikonfigurasi di nginx (/grafana)
      // Di development, kita gunakan URL lengkap ke server Grafana
      let baseUrl = isProduction ? '/grafana' : 'http://10.13.0.4:3001';
      
      // Fallback ke env variable jika tersedia
      if (process.env.REACT_APP_GRAFANA_URL) {
        baseUrl = process.env.REACT_APP_GRAFANA_URL;
      }
      
      // Menggunakan Dashboard ID dari konfigurasi atau nilai default
      const dashboardId = process.env.REACT_APP_GRAFANA_DASHBOARD_ID || '7d1a6a29-626f-4f4d-a997-e7d0a7c3f872';
      
      console.log('Grafana Config:', { baseUrl, dashboardId, roomId, env: process.env.NODE_ENV });

      // Buat URL dengan parameter untuk ruangan yang dipilih
      // Format: {baseUrl}/d/{dashboardId}/?orgId=1&var-location={roomId}&from=now-6h&to=now&theme={theme}
      let embedUrl = `${baseUrl}/d/${dashboardId}?orgId=1&var-location=${roomId}&from=now-6h&to=now&theme=${theme}&kiosk`;
      
      console.log('Generated Grafana URL:', embedUrl);
      setGrafanaUrl(embedUrl);
      setIsLoading(false);
    } catch (err) {
      console.error('Error configuring Grafana URL:', err);
      setError('Gagal mengkonfigurasi URL Grafana. Periksa konfigurasi atau koneksi jaringan.');
      setIsLoading(false);
    }
  }, [roomId, theme]);

  // Handler untuk event loading iframe
  const handleIframeLoad = () => {
    setIsLoading(false);
  };

  // Handler untuk error iframe
  const handleIframeError = () => {
    setError('Failed to load Grafana chart');
    setIsLoading(false);
  };

  return (
    <div className="room-chart-container">
      <h3 className="room-chart-title">Data Lingkungan - Ruangan {roomId}</h3>
      
      {isLoading && <div className="chart-loading">Loading chart...</div>}
      
      {error && (
        <div className="chart-error">
          <p>Error: {error}</p>
          <p>Periksa konfigurasi Grafana atau koneksi jaringan</p>
          <small style={{ color: '#666', marginTop: '10px', display: 'block' }}>
            Debug info: URL yang dicoba: {grafanaUrl || 'tidak ada URL'}
          </small>
        </div>
      )}
      
      {grafanaUrl && !error && (
        <div className="chart-iframe-wrapper" style={{ height: `${height}px` }}>
          <iframe
            src={grafanaUrl}
            title={`Environmental Stats for ${roomId}`}
            width="100%"
            height="100%"
            frameBorder="0"
            onLoad={handleIframeLoad}
            onError={handleIframeError}
            allowTransparency="true"
          ></iframe>
        </div>
      )}
    </div>
  );
};

RoomEnvironmentalChart.propTypes = {
  roomId: PropTypes.string.isRequired,
  height: PropTypes.number,
  theme: PropTypes.oneOf(['light', 'dark'])
};

export default RoomEnvironmentalChart;
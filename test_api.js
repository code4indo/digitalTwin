const axios = require('axios');

// Konstanta API
const API_KEY = 'development_key_for_testing';
const API_BASE_URL = 'http://localhost:8002';

// Buat instance axios
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY
  }
});

// Fungsi untuk mengambil data kesehatan sistem
const fetchSystemHealth = async () => {
  try {
    console.log('Requesting system health data...');
    console.log('URL:', `${API_BASE_URL}/system/health/`);
    console.log('Headers:', { 'X-API-Key': API_KEY });
    
    const response = await api.get('/system/health/');
    console.log('Response received!');
    console.log('Status code:', response.status);
    console.log('System health data:', JSON.stringify(response.data, null, 2));
    return response.data;
  } catch (error) {
    console.error('Error fetching system health:', error.message);
    console.error('Full error:', error);
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
    }
    throw error;
  }
};

// Jalankan pengujian
(async () => {
  try {
    const data = await fetchSystemHealth();
    console.log('Status sistem:', data.status);
    console.log(`Perangkat aktif: ${data.active_devices}/${data.total_devices}`);
    console.log('Ratio aktif:', data.ratio_active_to_total);
    console.log('Status koneksi InfluxDB:', data.influxdb_connection);
    console.log('Testing complete. Data received successfully.');
  } catch (err) {
    console.error('Test failed:', err.message);
    process.exit(1);
  }
})();

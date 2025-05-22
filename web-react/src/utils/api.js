import axios from 'axios';

// Konstanta untuk API
// Ambil API key dari environment variable atau gunakan fallback untuk development
const API_KEY = process.env.REACT_APP_API_KEY || localStorage.getItem('api_key') || 'development_key_for_testing';
console.log('Using API Key:', API_KEY);
  
// Ambil base URL dari environment variable atau gunakan fallback berdasarkan environment
let API_BASE_URL = process.env.REACT_APP_API_URL;

if (!API_BASE_URL) {
  if (process.env.NODE_ENV === 'production') {
    API_BASE_URL = '/api'; // Dalam production, API di-proxy oleh Nginx
  } else {
    // Coba deteksi host otomatis
    const currentHost = window.location.hostname;
    API_BASE_URL = `http://${currentHost}:8002`;
    
    // Fallback jika kita yakin IP server tertentu (untuk development)
    if (currentHost === 'localhost') {
      API_BASE_URL = 'http://localhost:8002';
    } else if (currentHost === '10.13.0.4') {
      API_BASE_URL = 'http://10.13.0.4:8002';
    }
  }
}

console.log('Using API Base URL:', API_BASE_URL);

// Buat instance axios dengan konfigurasi default
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY
  },
  timeout: 10000 // Timeout 10 detik
});

// Tambahkan interceptor untuk request
api.interceptors.request.use(
  config => {
    console.log(`Request [${config.method.toUpperCase()}] to ${config.url}`);
    
    // Pastikan header X-API-Key dikirim pada setiap permintaan
    if (!config.headers['X-API-Key'] && API_KEY) {
      config.headers['X-API-Key'] = API_KEY;
    }
    return config;
  },
  error => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Tambahkan interceptor untuk response untuk debugging
api.interceptors.response.use(
  response => {
    console.log(`Response from ${response.config.url}:`, response.status);
    return response;
  },
  error => {
    if (error.response) {
      // Server merespon dengan kode status diluar rentang 2xx
      console.error(`API error [${error.response.status}] from ${error.config.url}:`, error.response.data);
    } else if (error.request) {
      // Permintaan dibuat tapi tidak menerima respon
      console.error('No response received:', error.request);
    } else {
      // Kesalahan saat menyiapkan permintaan
      console.error('Error setting up request:', error.message);
    }
    return Promise.reject(error);
  }
);

// Fungsi-fungsi untuk mengambil data dari API
export const fetchSensorData = async (params = {}) => {
  try {
    const response = await api.get('/data/sensors', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching sensor data:', error);
    throw error;
  }
};

export const fetchLatestEnvironmentalStatus = async () => {
  try {
    console.log('Fetching environmental data...');
    
    // Tambahkan parameter pada URL untuk mengatasi masalah API key
    const urlParams = {
      params: {
        // Parameter kosong untuk menghindari error 404
      },
      // Jangan tambahkan api_key di sini karena kita menggunakan header
    };
    
    // Ambil statistik suhu dalam 1 jam terakhir (rata-rata, min, max)
    let tempResponse;
    try {
      console.log('Fetching temperature stats...');
      tempResponse = await api.get('/stats/temperature/last-hour/stats/', urlParams);
      console.log('Temperature response:', tempResponse.data);
    } catch (tempError) {
      console.error('Error fetching temperature data:', tempError.message, tempError.code);
      console.log('Temperature request failed with config:', tempError.config);
      console.log('Status:', tempError.response ? tempError.response.status : 'No response');
      // Tetap lanjutkan untuk mencoba endpoint humidity
      tempResponse = { data: null };
    }
    
    // Ambil statistik kelembapan dalam 1 jam terakhir (rata-rata, min, max)
    let humidityResponse;
    try {
      console.log('Fetching humidity stats...');
      humidityResponse = await api.get('/stats/humidity/last-hour/stats/', urlParams);
      console.log('Humidity response:', humidityResponse.data);
    } catch (humidityError) {
      console.error('Error fetching humidity data:', humidityError.message, humidityError.code);
      console.log('Humidity request failed with config:', humidityError.config);
      console.log('Status:', humidityError.response ? humidityError.response.status : 'No response');
      humidityResponse = { data: null };
    }
    
    // Validasi data suhu
    const tempAvg = tempResponse.data && typeof tempResponse.data.avg_temperature === 'number' 
      ? tempResponse.data.avg_temperature 
      : 22.5; // Fallback value
    
    const tempMin = tempResponse.data && typeof tempResponse.data.min_temperature === 'number'
      ? tempResponse.data.min_temperature
      : 19.2; // Fallback value
      
    const tempMax = tempResponse.data && typeof tempResponse.data.max_temperature === 'number'
      ? tempResponse.data.max_temperature
      : 24.8; // Fallback value
      
    // Validasi data kelembapan
    const humidityAvg = humidityResponse.data && typeof humidityResponse.data.avg_humidity === 'number'
      ? humidityResponse.data.avg_humidity
      : 48; // Fallback value
      
    const humidityMin = humidityResponse.data && typeof humidityResponse.data.min_humidity === 'number'
      ? humidityResponse.data.min_humidity
      : 42; // Fallback value
      
    const humidityMax = humidityResponse.data && typeof humidityResponse.data.max_humidity === 'number'
      ? humidityResponse.data.max_humidity
      : 53; // Fallback value
    
    // Kombinasikan data dari kedua endpoint
    return {
      temperature: {
        average: tempAvg,
        min: tempMin,
        max: tempMax
      },
      humidity: {
        average: humidityAvg,
        min: humidityMin,
        max: humidityMax
      }
    };
  } catch (error) {
    console.error('Error fetching environmental status:', error);
    
    // Fallback ke data dummy jika API gagal
    return {
      temperature: {
        average: 22.5,
        min: 19.2,
        max: 24.8
      },
      humidity: {
        average: 48,
        min: 42,
        max: 53
      }
    };
  }
};

export const fetchExternalWeatherData = async () => {
  try {
    const response = await api.get('/external/bmkg/latest');
    return response.data;
  } catch (error) {
    console.error('Error fetching external weather data:', error);
    throw error;
  }
};

export const fetchSystemHealth = async () => {
  try {
    console.log('Requesting system health data...');
    console.log('URL:', `${API_BASE_URL}/system/health/`);
    
    const response = await api.get('/system/health/');
    console.log('System health API response:', response.data);
    
    // Pastikan status yang diterima dalam format yang konsisten
    if (response.data && response.data.status) {
      // Normalize status names to ensure consistency
      const normalizedStatus = response.data.status.charAt(0).toUpperCase() + response.data.status.slice(1).toLowerCase();
      response.data.status = normalizedStatus;
      
      // Logging untuk debuging
      console.log('Normalized status:', response.data.status);
    }
    
    return response.data;
  } catch (error) {
    console.error('Error fetching system health:', error);
    if (error.response) {
      console.error('Status:', error.response.status);
      console.error('Data:', error.response.data);
    }
    throw error;
  }
};

export const fetchAlerts = async (filter = 'all') => {
  try {
    const response = await api.get(`/alerts?filter=${filter}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching alerts:', error);
    throw error;
  }
};

export const fetchRoomData = async (roomId) => {
  try {
    const response = await api.get(`/rooms/${roomId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching room ${roomId} data:`, error);
    throw error;
  }
};

export const fetchTrendData = async (params = {}) => {
  try {
    const response = await api.get('/data/trends', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching trend data:', error);
    throw error;
  }
};

export const fetchPredictions = async (params = {}) => {
  try {
    const response = await api.get('/predictions', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching predictions:', error);
    throw error;
  }
};

// Function untuk mengambil detail ruangan berdasarkan ID
export const fetchRoomDetails = async (roomId) => {
  try {
    const response = await api.get(`/rooms/${roomId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching room details for ${roomId}:`, error);
    throw error;
  }
};

// Function untuk mengambil data analisis prediktif
export const fetchPredictiveAnalysis = async (params = {}) => {
  try {
    const response = await api.get('/analysis/predictive', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching predictive analysis:', error);
    throw error;
  }
};

// Function untuk mengambil rekomendasi proaktif
export const fetchRecommendations = async () => {
  try {
    const response = await api.get('/recommendations/proactive');
    return response.data;
  } catch (error) {
    console.error('Error fetching recommendations:', error);
    throw error;
  }
};

// Function untuk mengambil pengaturan otomasi
export const fetchAutomationSettings = async () => {
  try {
    const response = await api.get('/automation/settings');
    return response.data;
  } catch (error) {
    console.error('Error fetching automation settings:', error);
    throw error;
  }
};

// Function untuk memperbarui pengaturan otomasi
export const updateAutomationSettings = async (settings) => {
  try {
    const response = await api.put('/automation/settings', settings);
    return response.data;
  } catch (error) {
    console.error('Error updating automation settings:', error);
    throw error;
  }
};

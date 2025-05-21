import axios from 'axios';

// Konstanta untuk API
// Ambil API key dari environment variable atau gunakan fallback untuk development
const API_KEY = process.env.REACT_APP_API_KEY || localStorage.getItem('api_key') || 'development_key_for_testing';
console.log('Using API Key:', API_KEY);
  
// Ambil base URL dari environment variable atau gunakan fallback berdasarkan environment
const API_BASE_URL = process.env.REACT_APP_API_URL || 
                   (process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:8002');
console.log('Using API Base URL:', API_BASE_URL);

// Buat instance axios dengan konfigurasi default
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY
  }
});

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
    const response = await api.get('/status/environment/latest');
    return response.data;
  } catch (error) {
    console.error('Error fetching environmental status:', error);
    throw error;
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
    console.log('Headers:', { 'X-API-Key': API_KEY });
    
    const response = await api.get('/system/health/');
    console.log('System health API response:', response.data);
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

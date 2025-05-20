import axios from 'axios';

// Konstanta untuk API
// IMPORTANT: Ganti dengan kunci API yang valid atau implementasi autentikasi yang lebih aman
const API_KEY = 'c5023020a5203c9eb451e2459df2047b9d261a30af1abcd54bd546f3ddb3248d';
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '/api'  // Jika di production gunakan proxy yang diatur di webpack
  : 'http://127.0.0.1:8002'; // URL API di development

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
    const response = await api.get('/system/health');
    return response.data;
  } catch (error) {
    console.error('Error fetching system health:', error);
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

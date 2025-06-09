import axios from 'axios';

// Konstanta untuk API
// Debug flag untuk development
const DEBUG_API = process.env.NODE_ENV === 'development' && process.env.REACT_APP_DEBUG_API === 'true';

// Ambil API key dari environment variable atau gunakan fallback untuk development
const API_KEY = process.env.REACT_APP_API_KEY || localStorage.getItem('api_key') || 'development_key_for_testing';
if (DEBUG_API) console.log('Using API Key:', API_KEY);
  
// Ambil base URL dari environment variable atau gunakan fallback berdasarkan environment
let API_BASE_URL = process.env.REACT_APP_API_URL;

if (!API_BASE_URL) {
  if (process.env.NODE_ENV === 'production') {
    API_BASE_URL = '/api'; // Dalam production, API di-proxy oleh Nginx
  } else {
    // Coba deteksi host otomatis
    const currentHost = window.location.hostname;
    const currentPort = window.location.port;
    
    // Untuk development, gunakan host yang sama dengan port API
    if (currentHost === 'localhost' || currentHost === '127.0.0.1') {
      API_BASE_URL = 'http://localhost:8002';
    } else {
      // Untuk container atau IP lain, gunakan IP yang sama dengan port API
      API_BASE_URL = `http://${currentHost}:8002`;
    }
  }
}

if (DEBUG_API) console.log('Using API Base URL:', API_BASE_URL);

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
    if (DEBUG_API) console.log(`Request [${config.method.toUpperCase()}] to ${config.url}`);
    
    // Pastikan header X-API-Key dikirim pada setiap permintaan
    if (!config.headers['X-API-Key'] && API_KEY) {
      config.headers['X-API-Key'] = API_KEY;
    }
    return config;
  },
  error => {
    if (DEBUG_API) console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Tambahkan interceptor untuk response untuk debugging
api.interceptors.response.use(
  response => {
    if (DEBUG_API) console.log(`Response from ${response.config.url}:`, response.status);
    return response;
  },
  error => {
    if (error.response) {
      // Server merespon dengan kode status diluar rentang 2xx
      if (DEBUG_API) console.error(`API error [${error.response.status}] from ${error.config.url}:`, error.response.data);
    } else if (error.request) {
      // Permintaan dibuat tapi tidak menerima respon
      if (DEBUG_API) console.error('No response received:', error.request);
    } else {
      // Kesalahan saat menyiapkan permintaan
      if (DEBUG_API) console.error('Error setting up request:', error.message);
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
    if (DEBUG_API) console.log('Fetching environmental data...');
    
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
      if (DEBUG_API) console.log('Fetching temperature stats...');
      tempResponse = await api.get('/stats/temperature/last-hour/stats/', urlParams);
      if (DEBUG_API) console.log('Temperature response:', tempResponse.data);
    } catch (tempError) {
      if (DEBUG_API) {
        console.error('Error fetching temperature data:', tempError.message, tempError.code);
        console.log('Temperature request failed with config:', tempError.config);
        console.log('Status:', tempError.response ? tempError.response.status : 'No response');
      }
      // Tetap lanjutkan untuk mencoba endpoint humidity
      tempResponse = { data: null };
    }
    
    // Ambil statistik kelembapan dalam 1 jam terakhir (rata-rata, min, max)
    let humidityResponse;
    try {
      if (DEBUG_API) console.log('Fetching humidity stats...');
      humidityResponse = await api.get('/stats/humidity/last-hour/stats/', urlParams);
      if (DEBUG_API) console.log('Humidity response:', humidityResponse.data);
    } catch (humidityError) {
      if (DEBUG_API) {
        console.error('Error fetching humidity data:', humidityError.message, humidityError.code);
        console.log('Humidity request failed with config:', humidityError.config);
        console.log('Status:', humidityError.response ? humidityError.response.status : 'No response');
      }
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
    if (DEBUG_API) console.error('Error fetching environmental status:', error);
    
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
    if (DEBUG_API) console.error('Error fetching external weather data:', error);
    throw error;
  }
};

export const fetchSystemHealth = async () => {
  try {
    if (DEBUG_API) {
      console.log('Requesting system health data...');
      console.log('URL:', `${API_BASE_URL}/system/health/`);
    }
    
    const response = await api.get('/system/health/');
    if (DEBUG_API) console.log('System health API response:', response.data);
    
    // Pastikan status yang diterima dalam format yang konsisten
    if (response.data && response.data.status) {
      // Normalize status names to ensure consistency
      const normalizedStatus = response.data.status.charAt(0).toUpperCase() + response.data.status.slice(1).toLowerCase();
      response.data.status = normalizedStatus;
      
      // Logging untuk debuging
      if (DEBUG_API) console.log('Normalized status:', response.data.status);
    }
    
    return response.data;
  } catch (error) {
    if (DEBUG_API) {
      console.error('Error fetching system health:', error);
      if (error.response) {
        console.error('Status:', error.response.status);
        console.error('Data:', error.response.data);
      }
    }
    throw error;
  }
};

export const fetchAlerts = async (filter = 'all') => {
  try {
    const response = await api.get(`/alerts?filter=${filter}`);
    return response.data;
  } catch (error) {
    if (DEBUG_API) console.error('Error fetching alerts:', error);
    throw error;
  }
};

export const fetchRoomData = async (roomId) => {
  try {
    const response = await api.get(`/rooms/${roomId}`);
    return response.data;
  } catch (error) {
    if (DEBUG_API) console.error(`Error fetching room ${roomId} data:`, error);
    throw error;
  }
};

export const fetchTrendData = async (params = {}) => {
  try {
    const response = await api.get('/data/trends', { params });
    return response.data;
  } catch (error) {
    if (DEBUG_API) console.error('Error fetching trend data:', error);
    throw error;
  }
};

export const fetchPredictions = async (params = {}) => {
  try {
    const response = await api.get('/predictions', { params });
    return response.data;
  } catch (error) {
    if (DEBUG_API) console.error('Error fetching predictions:', error);
    throw error;
  }
};

// Function untuk mengambil detail ruangan berdasarkan ID
export const fetchRoomDetails = async (roomId) => {
  try {
    const response = await api.get(`/rooms/${roomId}`);
    return response.data;
  } catch (error) {
    if (DEBUG_API) console.error(`Error fetching room details for ${roomId}:`, error);
    throw error;
  }
};

// Function untuk mengambil data analisis prediktif
export const fetchPredictiveAnalysis = async (params = {}) => {
  try {
    const response = await api.get('/analysis/predictive', { params });
    return response.data;
  } catch (error) {
    if (DEBUG_API) console.error('Error fetching predictive analysis:', error);
    throw error;
  }
};

// Function untuk mengambil rekomendasi proaktif
export const fetchRecommendations = async () => {
  try {
    const response = await api.get('/recommendations/proactive');
    return response.data;
  } catch (error) {
    if (DEBUG_API) console.error('Error fetching recommendations:', error);
    throw error;
  }
};

// ML Model Training and Prediction Functions
export const fetchMLTrainingStats = async (days_back = 7) => {
  try {
    const response = await api.get(`/ml/training-data/stats?days_back=${days_back}`);
    return response.data;
  } catch (error) {
    if (DEBUG_API) console.error('Error fetching ML training stats:', error);
    throw error;
  }
};

export const fetchMLPrediction = async (model_name = 'random_forest', hours_ahead = 1, location = null, device = null) => {
  try {
    let url = `/ml/model/predict?model_name=${model_name}&hours_ahead=${hours_ahead}`;
    if (location) url += `&location=${location}`;
    if (device) url += `&device=${device}`;
    
    const response = await api.post(url);
    return response.data;
  } catch (error) {
    if (DEBUG_API) console.error('Error fetching ML prediction:', error);
    throw error;
  }
};

export const fetchMLModelList = async () => {
  try {
    const response = await api.get('/ml/model/list');
    return response.data;
  } catch (error) {
    if (DEBUG_API) console.error('Error fetching ML model list:', error);
    throw error;
  }
};

export const trainMLModel = async (model_type = 'random_forest', days_back = 30, save_model = true) => {
  try {
    const response = await api.post(`/ml/model/train?model_type=${model_type}&days_back=${days_back}&save_model=${save_model}`);
    return response.data;
  } catch (error) {
    if (DEBUG_API) console.error('Error training ML model:', error);
    throw error;
  }
};

export const compareMLModels = async (days_back = 7) => {
  try {
    const response = await api.get(`/ml/model/compare?days_back=${days_back}`);
    return response.data;
  } catch (error) {
    if (DEBUG_API) console.error('Error comparing ML models:', error);
    throw error;
  }
};

// Enhanced Predictive Analysis using ML models
export const fetchEnhancedPredictiveAnalysis = async (params = {}) => {
  try {
    // Use the new ML prediction endpoint for more accurate predictions
    const {
      model = 'random_forest',
      timeframe = '24h',
      location = null,
      device = null
    } = params;
    
    // Generate predictions for multiple time horizons
    const predictions = [];
    const hours = timeframe === '24h' ? 24 : timeframe === '48h' ? 48 : 12;
    
    for (let i = 1; i <= hours; i += 2) { // Every 2 hours
      try {
        const prediction = await fetchMLPrediction(model, i, location, device);
        predictions.push({
          hour: i,
          temperature: prediction.predictions.temperature,
          humidity: prediction.predictions.humidity,
          confidence_temp: prediction.confidence.temperature,
          confidence_humidity: prediction.confidence.humidity,
          timestamp: new Date(prediction.prediction_time).getTime()
        });
      } catch (err) {
        // If ML prediction fails, use fallback data
        console.warn(`Failed to get ML prediction for hour ${i}:`, err);
      }
    }
    
    if (predictions.length === 0) {
      // Fallback to original predictive analysis
      return await fetchPredictiveAnalysis(params);
    }
    
    // Format data for Chart.js
    const labels = predictions.map(p => `+${p.hour}h`);
    const tempData = predictions.map(p => p.temperature);
    const humidityData = predictions.map(p => p.humidity);
    const tempConfidence = predictions.map(p => p.confidence_temp);
    const humidityConfidence = predictions.map(p => p.confidence_humidity);
    
    return {
      model_info: {
        model_name: model,
        version: '1.0.0',
        accuracy: predictions.length > 0 ? Math.min(...tempConfidence, ...humidityConfidence) : 0.85,
        predictions_count: predictions.length,
        generated_at: new Date().toISOString()
      },
      temperature: {
        labels: labels,
        datasets: [{
          label: 'Prediksi Suhu (°C)',
          data: tempData,
          borderColor: 'rgb(239, 68, 68)',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          tension: 0.4,
          fill: true
        }]
      },
      humidity: {
        labels: labels,
        datasets: [{
          label: 'Prediksi Kelembapan (%)',
          data: humidityData,
          borderColor: 'rgb(59, 130, 246)',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.4,
          fill: true
        }]
      },
      predictions: predictions,
      confidence: {
        avg_temperature: tempConfidence.reduce((a, b) => a + b, 0) / tempConfidence.length || 0.85,
        avg_humidity: humidityConfidence.reduce((a, b) => a + b, 0) / humidityConfidence.length || 0.80
      }
    };
    
  } catch (error) {
    if (DEBUG_API) console.error('Error fetching enhanced predictive analysis:', error);
    // Fallback to original method
    return await fetchPredictiveAnalysis(params);
  }
};

// Automation Settings Functions
export const fetchAutomationSettings = async () => {
  try {
    if (DEBUG_API) {
      console.log('Requesting automation settings...');
      console.log('URL:', `${API_BASE_URL}/automation/settings`);
    }
    
    const response = await api.get('/automation/settings');
    return response.data;
  } catch (error) {
    if (DEBUG_API) console.error('Error fetching automation settings:', error);
    
    // Return default settings as fallback
    return {
      temperature_control: true,
      humidity_control: true,
      target_temperature: 24.0,
      target_humidity: 60.0,
      auto_alerts: true,
      alert_threshold_temp: 27.0,
      alert_threshold_humidity: 75.0
    };
  }
};

export const updateAutomationSettings = async (settings) => {
  try {
    if (DEBUG_API) {
      console.log('Updating automation settings...');
      console.log('URL:', `${API_BASE_URL}/automation/settings`);
      console.log('Settings:', settings);
    }
    
    const response = await api.put('/automation/settings', settings);
    return response.data;
  } catch (error) {
    if (DEBUG_API) console.error('Error updating automation settings:', error);
    throw error;
  }
};

import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler } from 'chart.js';
import { Line } from 'react-chartjs-2';
import { fetchPredictiveAnalysis } from '../utils/api';
import ProactiveRecommendations from './ProactiveRecommendations';

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

const PredictiveAnalysis = () => {
  const [selectedModel, setSelectedModel] = useState('default');
  const [selectedTimeframe, setSelectedTimeframe] = useState('24h');
  const [temperatureData, setTemperatureData] = useState(null);
  const [humidityData, setHumidityData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const data = await fetchPredictiveAnalysis({
          model: selectedModel,
          timeframe: selectedTimeframe
        });
        
        setTemperatureData(data.temperature);
        setHumidityData(data.humidity);
        setError(null);
      } catch (err) {
        console.error('Error fetching predictive analysis:', err);
        setError('Gagal memuat analisis prediktif. Silakan coba lagi.');
        // Use dummy data if API fails
        const dummyData = getDummyPredictionData(selectedTimeframe);
        setTemperatureData(dummyData.temperature);
        setHumidityData(dummyData.humidity);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [selectedModel, selectedTimeframe]);
  
  // Generate dummy prediction data for testing
  const getDummyPredictionData = (timeframe) => {
    let hours = 24;
    let step = 1;
    
    switch (timeframe) {
      case '6h':
        hours = 6;
        step = 1;
        break;
      case '24h':
        hours = 24;
        step = 2;
        break;
      case '7d':
        hours = 168; // 7 * 24
        step = 12;
        break;
      default:
        hours = 24;
        step = 2;
    }
    
    const currentHour = new Date().getHours();
    const labels = Array.from({ length: Math.ceil(hours / step) }, (_, i) => {
      const hour = (currentHour + i * step) % 24;
      return `${hour}:00`;
    });
    
    // Generate temperature prediction data with slight upward trend
    const baseTemp = 22;
    const tempData = Array.from({ length: labels.length }, (_, i) => {
      const trend = i / labels.length * 2; // 0-2 degree increase over time
      const random = Math.random() * 1 - 0.5; // -0.5 to 0.5 random variation
      return baseTemp + trend + random;
    });
    
    const temperatureData = {
      labels,
      datasets: [
        {
          label: 'Prediksi Suhu (°C)',
          data: tempData,
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          fill: true,
          tension: 0.4
        },
        {
          label: 'Batas Optimal',
          data: Array(labels.length).fill(24),
          borderColor: 'rgba(255, 99, 132, 0.5)',
          borderDash: [5, 5],
          fill: false,
          pointRadius: 0
        }
      ]
    };
    
    // Generate humidity prediction data
    const baseHumidity = 50;
    const humidityData = Array.from({ length: labels.length }, (_, i) => {
      const trend = i / labels.length * 5; // 0-5% increase over time
      const random = Math.random() * 3 - 1.5; // -1.5 to 1.5 random variation
      return baseHumidity + trend + random;
    });
    
    const humidityChartData = {
      labels,
      datasets: [
        {
          label: 'Prediksi Kelembapan (%)',
          data: humidityData,
          borderColor: 'rgb(53, 162, 235)',
          backgroundColor: 'rgba(53, 162, 235, 0.2)',
          fill: true,
          tension: 0.4
        },
        {
          label: 'Batas Optimal',
          data: Array(labels.length).fill(60),
          borderColor: 'rgba(53, 162, 235, 0.5)',
          borderDash: [5, 5],
          fill: false,
          pointRadius: 0
        }
      ]
    };
    
    return {
      temperature: temperatureData,
      humidity: humidityChartData
    };
  };
  
  // Chart options
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      tooltip: {
        backgroundColor: 'rgba(52, 73, 94, 0.8)',
        titleFont: { size: 14, weight: 'bold' },
        bodyFont: { size: 13 },
        padding: 12,
        cornerRadius: 6
      }
    },
    scales: {
      y: {
        beginAtZero: false,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)'
        }
      },
      x: {
        grid: {
          display: false
        }
      }
    }
  };
  
  // Handle model selection
  const handleModelChange = (e) => {
    setSelectedModel(e.target.value);
  };
  
  // Handle timeframe selection
  const handleTimeframeChange = (e) => {
    setSelectedTimeframe(e.target.value);
  };
  
  return (
    <section className="predictive-section">
      <div className="section-header">
        <h2>Analisis Prediktif</h2>
        <div className="prediction-controls">
          <select id="prediction-model" value={selectedModel} onChange={handleModelChange}>
            <option value="default">Model Default</option>
            <option value="optimized">Model Optimasi</option>
            <option value="seasonal">Model Musiman</option>
          </select>
          <select id="prediction-timeframe" value={selectedTimeframe} onChange={handleTimeframeChange}>
            <option value="6h">6 Jam Kedepan</option>
            <option value="24h">24 Jam Kedepan</option>
            <option value="7d">7 Hari Kedepan</option>
          </select>
        </div>
      </div>
      
      {loading ? (
        <div className="loading-indicator">Memuat analisis prediktif...</div>
      ) : error && !temperatureData ? (
        <div className="error-message">{error}</div>
      ) : (
        <div className="prediction-grid">
          <div className="prediction-card">
            <h3>Prediksi Suhu</h3>
            <div className="prediction-chart-container">
              {temperatureData && (
                <Line data={temperatureData} options={options} />
              )}
            </div>
          </div>
          <div className="prediction-card">
            <h3>Prediksi Kelembapan</h3>
            <div className="prediction-chart-container">
              {humidityData && (
                <Line data={humidityData} options={options} />
              )}
            </div>
          </div>
          <ProactiveRecommendations />
        </div>
      )}
    </section>
  );
};

export default PredictiveAnalysis;

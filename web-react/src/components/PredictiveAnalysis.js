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
  const getDummyPredictionData = (timeframe = '24h') => {
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
    
    try {
      const currentHour = new Date().getHours();
      const dataPoints = Math.ceil(hours / step);
      const labels = Array.from({ length: dataPoints }, (_, i) => {
        const hour = (currentHour + i * step) % 24;
        return `${hour.toString().padStart(2, '0')}:00`;
      });
      
      // Generate temperature prediction data with slight upward trend
      const baseTemp = 22;
      const tempData = Array.from({ length: labels.length }, (_, i) => {
        const trend = (i / (labels.length - 1)) * 2; // 0-2 degree increase over time
        const random = (Math.random() - 0.5) * 1; // -0.5 to 0.5 random variation
        return Math.round((baseTemp + trend + random) * 10) / 10;
      });
      
      const temperatureData = {
        labels: labels,
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
        const trend = (i / (labels.length - 1)) * 5; // 0-5% increase over time
        const random = (Math.random() - 0.5) * 3; // -1.5 to 1.5 random variation
        return Math.round((baseHumidity + trend + random) * 10) / 10;
      });
      
      const humidityChartData = {
        labels: labels,
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
    } catch (error) {
      console.error('Error generating dummy prediction data:', error);
      // Return minimal fallback data
      return {
        temperature: {
          labels: ['00:00', '06:00', '12:00', '18:00'],
          datasets: [{
            label: 'Prediksi Suhu (°C)',
            data: [22, 23, 24, 23],
            borderColor: 'rgb(255, 99, 132)',
            backgroundColor: 'rgba(255, 99, 132, 0.2)'
          }]
        },
        humidity: {
          labels: ['00:00', '06:00', '12:00', '18:00'],
          datasets: [{
            label: 'Prediksi Kelembapan (%)',
            data: [50, 52, 55, 53],
            borderColor: 'rgb(53, 162, 235)',
            backgroundColor: 'rgba(53, 162, 235, 0.2)'
          }]
        }
      };
    }
  };
  
  // Chart options with better error handling
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      intersect: false,
      mode: 'index'
    },
    plugins: {
      legend: {
        position: 'top',
        labels: {
          usePointStyle: true,
          padding: 20
        }
      },
      tooltip: {
        backgroundColor: 'rgba(52, 73, 94, 0.9)',
        titleFont: { size: 14, weight: 'bold' },
        bodyFont: { size: 12 },
        padding: 12,
        cornerRadius: 8,
        displayColors: true,
        callbacks: {
          label: function(context) {
            try {
              const label = context.dataset.label || '';
              const value = typeof context.parsed?.y === 'number' ? 
                context.parsed.y.toFixed(1) : 
                (context.raw || 0).toString();
              return `${label}: ${value}`;
            } catch (error) {
              console.warn('Tooltip callback error:', error);
              return 'Data tidak tersedia';
            }
          }
        }
      }
    },
    scales: {
      x: {
        display: true,
        grid: {
          display: false
        },
        ticks: {
          maxRotation: 45,
          minRotation: 0
        }
      },
      y: {
        beginAtZero: false,
        display: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)'
        },
        ticks: {
          callback: function(value) {
            return typeof value === 'number' ? value.toFixed(1) : value;
          }
        }
      }
    },
    elements: {
      line: {
        tension: 0.4
      },
      point: {
        radius: 3,
        hoverRadius: 6
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
              {temperatureData && temperatureData.datasets && temperatureData.datasets.length > 0 ? (
                <Line data={temperatureData} options={options} />
              ) : (
                <div className="no-data">Data prediksi suhu tidak tersedia</div>
              )}
            </div>
          </div>
          <div className="prediction-card">
            <h3>Prediksi Kelembapan</h3>
            <div className="prediction-chart-container">
              {humidityData && humidityData.datasets && humidityData.datasets.length > 0 ? (
                <Line data={humidityData} options={options} />
              ) : (
                <div className="no-data">Data prediksi kelembapan tidak tersedia</div>
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

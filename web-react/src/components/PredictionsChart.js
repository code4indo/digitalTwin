import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler } from 'chart.js';
import { Line } from 'react-chartjs-2';
import { fetchPredictions } from '../utils/api';

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

const PredictionsChart = () => {
  const [selectedModel, setSelectedModel] = useState('ml_model_1');
  const [selectedTimeframe, setSelectedTimeframe] = useState('24h');
  const [predictionData, setPredictionData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const loadPredictions = async () => {
      try {
        setLoading(true);
        const data = await fetchPredictions({
          model: selectedModel,
          timeframe: selectedTimeframe
        });
        
        setPredictionData(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching predictions:', err);
        setError('Gagal memuat prediksi. Silakan coba lagi.');
        // Use dummy data if API fails
        setPredictionData(getDummyPredictionData());
      } finally {
        setLoading(false);
      }
    };
    
    loadPredictions();
  }, [selectedModel, selectedTimeframe]);
  
  // Generate dummy prediction data for testing
  const getDummyPredictionData = () => {
    const now = new Date();
    const hours = selectedTimeframe === '24h' ? 24 : 48;
    
    const labels = Array.from({ length: hours }, (_, i) => {
      const date = new Date(now);
      date.setHours(date.getHours() + i);
      return date.getHours() + ':00';
    });
    
    // Generate realistic temperature prediction data
    const actualTemp = Array.from({ length: 6 }, (_, i) => 22 + Math.random() * 3);
    const predictedTemp = Array.from({ length: hours }, (_, i) => {
      // Start with the last actual value and add daily cycle
      const baseTemp = i < actualTemp.length ? 
        actualTemp[i] : 
        actualTemp[actualTemp.length - 1];
      
      // Add daily temperature cycle (cooler at night, warmer in day)
      const hour = (now.getHours() + i) % 24;
      const dayCycle = Math.sin(((hour - 6) / 24) * Math.PI * 2) * 2;
      
      // Add some randomness
      const randomFactor = Math.random() * 0.5 - 0.25;
      
      return baseTemp + dayCycle + randomFactor;
    });
    
    // Generate realistic humidity prediction based on temperature
    const predictedHumidity = predictedTemp.map(temp => {
      // Higher temperature often means lower humidity
      const baseHumidity = 70 - (temp - 20) * 3;
      // Add some randomness
      return baseHumidity + (Math.random() * 8 - 4);
    });
    
    // Create confidence interval (upper and lower bounds)
    const upperBoundTemp = predictedTemp.map(val => val + 0.8 + Math.random() * 0.4);
    const lowerBoundTemp = predictedTemp.map(val => val - 0.8 - Math.random() * 0.4);
    
    return {
      labels,
      datasets: [
        {
          label: 'Prediksi Suhu (°C)',
          data: predictedTemp,
          borderColor: 'rgb(231, 76, 60)',
          backgroundColor: 'rgba(231, 76, 60, 0.7)',
          tension: 0.4,
          borderWidth: 2
        },
        {
          label: 'Batas Atas',
          data: upperBoundTemp,
          borderColor: 'rgba(231, 76, 60, 0.3)',
          backgroundColor: 'transparent',
          borderDash: [5, 5],
          borderWidth: 1,
          tension: 0.4,
          pointRadius: 0
        },
        {
          label: 'Batas Bawah',
          data: lowerBoundTemp,
          borderColor: 'rgba(231, 76, 60, 0.3)',
          backgroundColor: 'transparent',
          borderDash: [5, 5],
          borderWidth: 1,
          tension: 0.4,
          pointRadius: 0,
          fill: {
            target: '+1',
            above: 'rgba(231, 76, 60, 0.1)'
          }
        },
        {
          label: 'Prediksi Kelembapan (%)',
          data: predictedHumidity,
          borderColor: 'rgb(52, 152, 219)',
          backgroundColor: 'rgba(52, 152, 219, 0.7)',
          tension: 0.4,
          borderWidth: 2,
          hidden: true
        }
      ]
    };
  };
  
  // Chart options
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          filter: (item) => {
            // Hide the confidence interval labels
            return !item.text.includes('Batas');
          }
        }
      },
      tooltip: {
        backgroundColor: 'rgba(52, 73, 94, 0.8)',
        callbacks: {
          title: function(tooltipItems) {
            return 'Prediksi untuk ' + tooltipItems[0].label;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: false,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)'
        },
        title: {
          display: true,
          text: 'Nilai'
        }
      },
      x: {
        grid: {
          display: false
        },
        title: {
          display: true,
          text: 'Waktu'
        }
      }
    }
  };
  
  // Handle model selection change
  const handleModelChange = (e) => {
    setSelectedModel(e.target.value);
  };
  
  // Handle timeframe selection change
  const handleTimeframeChange = (e) => {
    setSelectedTimeframe(e.target.value);
  };
  
  return (
    <div className="card predictions">
      <div className="card-header">
        <h2>Prediksi Iklim Mikro</h2>
        <div className="prediction-controls">
          <select 
            id="prediction-model" 
            value={selectedModel} 
            onChange={handleModelChange}
          >
            <option value="ml_model_1">Model Machine Learning 1</option>
            <option value="ml_model_2">Model Machine Learning 2</option>
            <option value="statistical">Model Statistik</option>
          </select>
          
          <select 
            id="prediction-timeframe" 
            value={selectedTimeframe} 
            onChange={handleTimeframeChange}
          >
            <option value="24h">24 Jam</option>
            <option value="48h">48 Jam</option>
          </select>
        </div>
      </div>
      
      <div className="prediction-chart">
        <div className="chart-container" style={{ position: 'relative', height: '300px' }}>
          {loading ? (
            <div className="loading-indicator">Memuat prediksi...</div>
          ) : error ? (
            <div className="error-message">{error}</div>
          ) : predictionData ? (
            <Line data={predictionData} options={options} />
          ) : null}
        </div>
        <div className="prediction-notes">
          <p>Prediksi diperbarui setiap jam, berdasarkan data sensor terkini dan data historis.</p>
          <p className="confidence-note">
            <span className="confidence-indicator"></span>
            Area yang diarsir menunjukkan interval kepercayaan 95%.
          </p>
        </div>
      </div>
    </div>
  );
};

export default PredictionsChart;

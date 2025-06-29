import React, { useState, useEffect, useRef } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import { Line } from 'react-chartjs-2';
import { fetchTrendData } from '../utils/api';

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const TrendAnalysis = () => {
  const [activePeriod, setActivePeriod] = useState('day');
  const [selectedLocation, setSelectedLocation] = useState('all');
  const [selectedParameter, setSelectedParameter] = useState('temperature');
  const [trendData, setTrendData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const chartRef = useRef(null);
  
  // Fetch trend data when parameters change
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const data = await fetchTrendData({
          period: activePeriod,
          location: selectedLocation,
          parameter: selectedParameter
        });
        
        // Transform API response to Chart.js format
        const transformedData = transformApiDataToChartFormat(data, selectedParameter);
        setTrendData(transformedData);
        setError(null);
      } catch (err) {
        // Silent error handling in production, log only in debug mode
        if (process.env.NODE_ENV === 'development') {
          console.error('Error fetching trend data:', err);
        }
        setError('Gagal memuat data tren. Silakan coba lagi.');
        // Use dummy data if API fails
        setTrendData(getDummyTrendData(activePeriod, selectedParameter));
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [activePeriod, selectedLocation, selectedParameter]);

  // Transform API response data to Chart.js format
  const transformApiDataToChartFormat = (apiData, parameter) => {
    if (!apiData || !Array.isArray(apiData.timestamps) || !Array.isArray(apiData.values)) {
      console.warn('Invalid API data structure:', apiData);
      return getDummyTrendData(activePeriod, parameter);
    }

    // Use timestamps as labels, but simplify for better readability
    const labels = apiData.timestamps.map((timestamp, index) => {
      // For day view, show every few hours to avoid clutter
      if (activePeriod === 'day' && index % 7 === 0) {
        return timestamp;
      } else if (activePeriod === 'day') {
        return ''; // Hide some labels to avoid overcrowding
      }
      return timestamp;
    });

    return {
      labels,
      datasets: [
        {
          label: parameter === 'temperature' ? 'Suhu (°C)' : 'Kelembapan (%)',
          data: apiData.values,
          borderColor: parameter === 'temperature' ? 'rgb(231, 76, 60)' : 'rgb(52, 152, 219)',
          backgroundColor: parameter === 'temperature' ? 'rgba(231, 76, 60, 0.5)' : 'rgba(52, 152, 219, 0.5)',
          tension: 0.4,
          pointRadius: 1, // Small points to avoid clutter
          pointHoverRadius: 4
        }
      ]
    };
  };
  
  // Generate dummy trend data for testing
  const getDummyTrendData = (period, parameter) => {
    let labels = [];
    let count = 0;
    
    switch (period) {
      case 'day':
        labels = Array.from({ length: 24 }, (_, i) => `${i}:00`);
        count = 24;
        break;
      case 'week':
        labels = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'];
        count = 7;
        break;
      case 'month':
        labels = Array.from({ length: 30 }, (_, i) => `${i + 1} Mei`);
        count = 30;
        break;
      default:
        labels = Array.from({ length: 24 }, (_, i) => `${i}:00`);
        count = 24;
    }
    
    // Generate random data based on parameter
    const minValue = parameter === 'temperature' ? 20 : 40;
    const maxValue = parameter === 'temperature' ? 28 : 60;
    const values = Array.from({ length: count }, () => 
      Math.floor(Math.random() * (maxValue - minValue + 1)) + minValue
    );
    
    // Add some realistic fluctuations
    for (let i = 1; i < values.length; i++) {
      // Make changes more gradual
      values[i] = values[i-1] + (Math.random() * 2 - 1);
      
      // Keep within realistic range
      if (values[i] > maxValue) values[i] = maxValue;
      if (values[i] < minValue) values[i] = minValue;
    }
    
    return {
      labels,
      datasets: [
        {
          label: parameter === 'temperature' ? 'Suhu (°C)' : 'Kelembapan (%)',
          data: values,
          borderColor: parameter === 'temperature' ? 'rgb(231, 76, 60)' : 'rgb(52, 152, 219)',
          backgroundColor: parameter === 'temperature' ? 'rgba(231, 76, 60, 0.5)' : 'rgba(52, 152, 219, 0.5)',
          tension: 0.4
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
        align: 'end',
      },
      title: {
        display: false
      },
      tooltip: {
        backgroundColor: 'rgba(52, 73, 94, 0.8)',
        titleFont: {
          size: 14,
          weight: 'bold'
        },
        bodyFont: {
          size: 13
        },
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
  
  // Handle period button clicks
  const handlePeriodChange = (period) => {
    setActivePeriod(period);
  };
  
  // Handle parameter selection
  const handleParameterChange = (e) => {
    setSelectedParameter(e.target.value);
  };
  
  // Handle location selection
  const handleLocationChange = (e) => {
    setSelectedLocation(e.target.value);
  };
  
  return (
    <div className="card trends">
      <div className="card-header">
        <h2>Analisis Tren</h2>
        <div className="trend-controls">
          <select id="trend-location" value={selectedLocation} onChange={handleLocationChange}>
            <option value="all">Semua Ruangan</option>
            <option value="F2">Ruang F2</option>
            <option value="F3">Ruang F3</option>
            <option value="F4">Ruang F4</option>
            <option value="F5">Ruang F5</option>
            <option value="F6">Ruang F6</option>
            <option value="G2">Ruang G2</option>
            <option value="G3">Ruang G3</option>
            <option value="G4">Ruang G4</option>
            <option value="G5">Ruang G5</option>
            <option value="G6">Ruang G6</option>
            <option value="G7">Ruang G7</option>
            <option value="G8">Ruang G8</option>
          </select>
          
          <select id="trend-parameter" value={selectedParameter} onChange={handleParameterChange}>
            <option value="temperature">Suhu</option>
            <option value="humidity">Kelembapan</option>
          </select>
        </div>
      </div>
      
      <div className="trend-chart">
        <div className="chart-container" style={{ position: 'relative', height: '300px' }}>
          {loading ? (
            <div className="loading-indicator">Memuat data tren...</div>
          ) : error ? (
            <div className="error-message">{error}</div>
          ) : trendData && trendData.datasets && trendData.datasets.length > 0 ? (
            <Line ref={chartRef} data={trendData} options={options} />
          ) : (
            <div className="no-data">Data tren tidak tersedia</div>
          )}
        </div>
        
        <div className="period-selector">
          <button 
            className={`period-btn ${activePeriod === 'day' ? 'active' : ''}`} 
            data-period="day"
            onClick={() => handlePeriodChange('day')}
          >
            Hari Ini
          </button>
          <button 
            className={`period-btn ${activePeriod === 'week' ? 'active' : ''}`} 
            data-period="week"
            onClick={() => handlePeriodChange('week')}
          >
            Mingguan
          </button>
          <button 
            className={`period-btn ${activePeriod === 'month' ? 'active' : ''}`} 
            data-period="month"
            onClick={() => handlePeriodChange('month')}
          >
            Bulanan
          </button>
        </div>
      </div>
    </div>
  );
};

export default TrendAnalysis;

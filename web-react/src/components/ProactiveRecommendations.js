import React, { useState, useEffect } from 'react';
import { fetchRecommendations } from '../utils/api';

const ProactiveRecommendations = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const data = await fetchRecommendations();
        setRecommendations(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching recommendations:', err);
        setError('Gagal memuat rekomendasi. Silakan coba lagi.');
        // Use dummy data if API fails
        setRecommendations(getDummyRecommendations());
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);
  
  // Generate dummy recommendations for testing
  const getDummyRecommendations = () => {
    const currentDate = new Date();
    const tomorrow = new Date();
    tomorrow.setDate(currentDate.getDate() + 1);
    
    return [
      {
        id: 1,
        timeframe: '16:00 - 20:00',
        title: 'Antisipasi Kenaikan Kelembapan',
        description: 'Prakiraan hujan akan meningkatkan kelembapan di area G7. Aktifkan dehumidifier mulai pukul 16:00.',
        type: 'humidity',
        priority: 'medium'
      },
      {
        id: 2,
        timeframe: `Besok, 06:00 - 10:00`,
        title: 'Antisipasi Peningkatan Suhu',
        description: 'Prakiraan cerah berawan dengan suhu eksternal mencapai 31°C. Persiapkan sistem pendingin di area F5-F6.',
        type: 'temperature',
        priority: 'medium'
      },
      {
        id: 3,
        timeframe: 'Maintenance',
        title: 'Jadwal Perawatan Optimal',
        description: 'Waktu optimal untuk perawatan AC adalah hari Rabu, 21 Mei 2025 pukul 10:00-14:00 saat beban sistem minimal.',
        type: 'maintenance',
        priority: 'low'
      }
    ];
  };
  
  const handleAction = (recommendationId) => {
    console.log(`Tindakan untuk rekomendasi ID: ${recommendationId}`);
    // Implementasi aksi untuk rekomendasi
  };
  
  return (
    <div className="prediction-card prediction-recommendations">
      <h3>Rekomendasi Proaktif</h3>
      
      {loading ? (
        <div className="loading-indicator">Memuat rekomendasi...</div>
      ) : error ? (
        <div className="error-message">{error}</div>
      ) : (
        <div className="recommendations-list">
          {recommendations.map(recommendation => (
            <div className="recommendation-item" key={recommendation.id}>
              <div className="recommendation-time">{recommendation.timeframe}</div>
              <div className="recommendation-content">
                <div className="recommendation-title">{recommendation.title}</div>
                <div className="recommendation-description">
                  {recommendation.description}
                </div>
              </div>
              <div className="recommendation-actions">
                <button 
                  className="action-btn" 
                  onClick={() => handleAction(recommendation.id)}
                >
                  Tindak Lanjut
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ProactiveRecommendations;

import React, { useState, useEffect } from 'react';
import { fetchProactiveRecommendations } from '../utils/api';
import './ComponentStyles.css';

const ProactiveRecommendations = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const data = await fetchProactiveRecommendations();
        
        // Handle new API response structure
        if (data && data.priority_recommendations) {
          // Combine priority and general recommendations
          const allRecommendations = [
            ...data.priority_recommendations,
            ...data.general_recommendations || []
          ];
          setRecommendations(allRecommendations);
        } else if (Array.isArray(data)) {
          setRecommendations(data);
        } else if (data && Array.isArray(data.recommendations)) {
          setRecommendations(data.recommendations);
        } else {
          setRecommendations(getDummyRecommendations());
        }
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
          {Array.isArray(recommendations) && recommendations.map(recommendation => (
            <div className={`recommendation-item priority-${recommendation.priority || 'low'}`} key={recommendation.id}>
              <div className="recommendation-header">
                <div className="recommendation-priority">
                  <span className={`priority-badge priority-${recommendation.priority || 'low'}`}>
                    {recommendation.priority?.toUpperCase() || 'INFO'}
                  </span>
                  {recommendation.category && (
                    <span className="category-badge">{recommendation.category}</span>
                  )}
                </div>
                {recommendation.created_at && (
                  <div className="recommendation-time">
                    {new Date(recommendation.created_at).toLocaleString('id-ID')}
                  </div>
                )}
              </div>
              <div className="recommendation-content">
                <div className="recommendation-title">{recommendation.title}</div>
                <div className="recommendation-description">
                  {recommendation.description}
                </div>
                {recommendation.room && (
                  <div className="recommendation-room">
                    <strong>Ruangan:</strong> {recommendation.room}
                  </div>
                )}
                {recommendation.estimated_impact && (
                  <div className="recommendation-impact">
                    <strong>Estimasi Dampak:</strong> {recommendation.estimated_impact}
                  </div>
                )}
                {recommendation.preservation_risk && (
                  <div className="recommendation-risk">
                    <strong>Risiko Preservasi:</strong> {recommendation.preservation_risk}
                  </div>
                )}
                {recommendation.specific_actions && Array.isArray(recommendation.specific_actions) && (
                  <div className="recommendation-actions-list">
                    <strong>Langkah-langkah:</strong>
                    <ul>
                      {recommendation.specific_actions.map((action, index) => (
                        <li key={index}>{action}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
              <div className="recommendation-footer">
                <button 
                  className={`action-btn action-btn-${recommendation.priority || 'low'}`}
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

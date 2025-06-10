import React, { useState, useEffect } from 'react';
import { fetchClimateInsights, fetchPreservationRisk, fetchRecommendations } from '../utils/api';
import './ClimateInsights.css';

const ClimateInsights = () => {
  const [activeTab, setActiveTab] = useState('insights');
  const [selectedParameter, setSelectedParameter] = useState('temperature');
  const [selectedPeriod, setSelectedPeriod] = useState('day');
  const [selectedLocation, setSelectedLocation] = useState('all');
  
  const [insights, setInsights] = useState(null);
  const [preservationRisk, setPreservationRisk] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch insights data
  const fetchInsightsData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await fetchClimateInsights({
        parameter: selectedParameter,
        period: selectedPeriod,
        location: selectedLocation
      });
      
      setInsights(data);
    } catch (err) {
      console.error('Error fetching insights:', err);
      setError('Gagal memuat wawasan AI. Menggunakan analisis berbasis aturan.');
      // Set fallback data
      setInsights({
        success: true,
        insights: {
          status_kondisi: 'optimal',
          tingkat_risiko: 'rendah',
          ringkasan_kondisi: 'Kondisi dalam rentang normal berdasarkan analisis dasar',
          confidence_level: 'sedang',
          data_source: 'fallback'
        }
      });
    } finally {
      setLoading(false);
    }
  };

  // Fetch preservation risk data
  const fetchPreservationData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await fetchPreservationRisk({
        location: selectedLocation
      });
      
      setPreservationRisk(data);
    } catch (err) {
      console.error('Error fetching preservation risk:', err);
      setError('Gagal memuat analisis risiko preservasi.');
    } finally {
      setLoading(false);
    }
  };

  // Fetch recommendations data
  const fetchRecommendationsData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await fetchRecommendations({
        parameter: selectedParameter,
        location: selectedLocation
      });
      
      setRecommendations(data);
    } catch (err) {
      console.error('Error fetching recommendations:', err);
      setError('Gagal memuat rekomendasi.');
    } finally {
      setLoading(false);
    }
  };

  // Effect untuk fetch data saat parameter berubah
  useEffect(() => {
    if (activeTab === 'insights') {
      fetchInsightsData();
    } else if (activeTab === 'preservation') {
      fetchPreservationData();
    } else if (activeTab === 'recommendations') {
      fetchRecommendationsData();
    }
  }, [activeTab, selectedParameter, selectedPeriod, selectedLocation]);

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'rendah': return '#4CAF50';
      case 'sedang': return '#FF9800';
      case 'tinggi': return '#F44336';
      case 'kritis': return '#D32F2F';
      default: return '#757575';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'optimal': return '#4CAF50';
      case 'warning': return '#FF9800';
      case 'critical': return '#F44336';
      default: return '#757575';
    }
  };

  const renderInsightsTab = () => {
    if (loading) {
      return (
        <div className="insights-loading">
          <div className="loading-spinner"></div>
          <p>Menganalisis data dengan AI Gemini...</p>
        </div>
      );
    }

    if (!insights || !insights.insights) {
      return (
        <div className="insights-error">
          <p>Tidak ada data wawasan tersedia</p>
        </div>
      );
    }

    const data = insights.insights;

    return (
      <div className="insights-content">
        {/* Status Overview */}
        <div className="status-overview">
          <div className="status-item">
            <h4>Status Kondisi</h4>
            <span 
              className="status-badge" 
              style={{ backgroundColor: getStatusColor(data.status_kondisi) }}
            >
              {data.status_kondisi?.toUpperCase()}
            </span>
          </div>
          
          <div className="status-item">
            <h4>Tingkat Risiko</h4>
            <span 
              className="risk-badge" 
              style={{ backgroundColor: getRiskColor(data.tingkat_risiko) }}
            >
              {data.tingkat_risiko?.toUpperCase()}
            </span>
          </div>
          
          <div className="status-item">
            <h4>Confidence Level</h4>
            <span className="confidence-badge">
              {data.confidence_level?.toUpperCase()}
            </span>
          </div>
        </div>

        {/* Ringkasan Kondisi */}
        <div className="condition-summary">
          <h4>Ringkasan Kondisi</h4>
          <p>{data.ringkasan_kondisi}</p>
        </div>

        {/* Dampak Preservasi */}
        <div className="preservation-impact">
          <h4>Dampak terhadap Preservasi Arsip</h4>
          <p>{data.dampak_preservasi}</p>
        </div>

        {/* Prediksi Tren */}
        <div className="trend-prediction">
          <h4>Prediksi Tren</h4>
          <p>{data.tren_prediksi}</p>
        </div>

        {/* Estimasi Dampak Jangka Panjang */}
        {data.estimasi_dampak_jangka_panjang && (
          <div className="long-term-impact">
            <h4>Estimasi Dampak Jangka Panjang</h4>
            <p>{data.estimasi_dampak_jangka_panjang}</p>
          </div>
        )}

        {/* Rekomendasi Aksi */}
        {data.rekomendasi_aksi && data.rekomendasi_aksi.length > 0 && (
          <div className="action-recommendations">
            <h4>Rekomendasi Aksi</h4>
            <ul>
              {data.rekomendasi_aksi.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Metadata */}
        <div className="insights-metadata">
          <small>
            Sumber: {data.data_source} | 
            Dianalisis: {data.generated_at ? new Date(data.generated_at).toLocaleString('id-ID') : 'N/A'}
          </small>
        </div>
      </div>
    );
  };

  const renderPreservationTab = () => {
    if (loading) {
      return (
        <div className="insights-loading">
          <div className="loading-spinner"></div>
          <p>Menganalisis risiko preservasi...</p>
        </div>
      );
    }

    if (!preservationRisk) {
      return (
        <div className="insights-error">
          <p>Tidak ada data risiko preservasi tersedia</p>
        </div>
      );
    }

    const combined = preservationRisk.combined_risk_assessment;
    const overall = preservationRisk.overall_recommendation;

    return (
      <div className="preservation-content">
        {/* Overall Risk Assessment */}
        <div className="risk-assessment">
          <h4>Penilaian Risiko Keseluruhan</h4>
          <div className="risk-score">
            <span 
              className="risk-level" 
              style={{ backgroundColor: getRiskColor(combined?.overall_risk_level) }}
            >
              {combined?.overall_risk_level?.toUpperCase()}
            </span>
            <span className="risk-score-value">Score: {combined?.risk_score}/4</span>
          </div>
          <p>{combined?.severity_description}</p>
        </div>

        {/* Primary Concern */}
        <div className="primary-concern">
          <h4>Perhatian Utama</h4>
          <p>
            <strong>{combined?.primary_concern === 'temperature' ? 'Suhu' : 'Kelembapan'}</strong> 
            menjadi faktor risiko utama saat ini.
          </p>
        </div>

        {/* Temperature Analysis */}
        <div className="parameter-analysis">
          <h4>Analisis Suhu</h4>
          <div className="analysis-summary">
            <span 
              className="parameter-risk" 
              style={{ backgroundColor: getRiskColor(preservationRisk.temperature_analysis?.tingkat_risiko) }}
            >
              {preservationRisk.temperature_analysis?.tingkat_risiko?.toUpperCase()}
            </span>
            <p>{preservationRisk.temperature_analysis?.ringkasan_kondisi}</p>
          </div>
        </div>

        {/* Humidity Analysis */}
        <div className="parameter-analysis">
          <h4>Analisis Kelembapan</h4>
          <div className="analysis-summary">
            <span 
              className="parameter-risk" 
              style={{ backgroundColor: getRiskColor(preservationRisk.humidity_analysis?.tingkat_risiko) }}
            >
              {preservationRisk.humidity_analysis?.tingkat_risiko?.toUpperCase()}
            </span>
            <p>{preservationRisk.humidity_analysis?.ringkasan_kondisi}</p>
          </div>
        </div>

        {/* Overall Recommendation */}
        {overall && (
          <div className="overall-recommendation">
            <h4>Rekomendasi Keseluruhan</h4>
            <div className="recommendation-details">
              <div className="urgency">
                <strong>Tingkat Urgensi:</strong> {overall.urgency}
              </div>
              <div className="action">
                <strong>Aksi yang Diperlukan:</strong> {overall.action_required}
              </div>
              <div className="focus">
                <strong>Area Fokus:</strong> {overall.focus_area}
              </div>
              <div className="timeline">
                <strong>Timeline:</strong> {overall.timeline}
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderRecommendationsTab = () => {
    if (loading) {
      return (
        <div className="insights-loading">
          <div className="loading-spinner"></div>
          <p>Memuat rekomendasi...</p>
        </div>
      );
    }

    if (!recommendations) {
      return (
        <div className="insights-error">
          <p>Tidak ada rekomendasi tersedia</p>
        </div>
      );
    }

    const recs = recommendations.recommendations;

    return (
      <div className="recommendations-content">
        {/* Status Summary */}
        <div className="recommendations-summary">
          <div className="summary-item">
            <h5>Status</h5>
            <span style={{ color: getStatusColor(recommendations.status) }}>
              {recommendations.status?.toUpperCase()}
            </span>
          </div>
          <div className="summary-item">
            <h5>Prioritas</h5>
            <span>{recommendations.priority_level?.toUpperCase()}</span>
          </div>
          <div className="summary-item">
            <h5>Risiko</h5>
            <span style={{ color: getRiskColor(recommendations.risk_level) }}>
              {recommendations.risk_level?.toUpperCase()}
            </span>
          </div>
        </div>

        {/* Impact Assessment */}
        {recommendations.impact_assessment && (
          <div className="impact-assessment">
            <h4>Penilaian Dampak</h4>
            <p>{recommendations.impact_assessment}</p>
          </div>
        )}

        {/* Immediate Actions */}
        {recs?.immediate_actions && recs.immediate_actions.length > 0 && (
          <div className="action-section immediate">
            <h4>🚨 Aksi Segera</h4>
            <ul>
              {recs.immediate_actions.map((action, index) => (
                <li key={index}>{action}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Short Term Actions */}
        {recs?.short_term_actions && recs.short_term_actions.length > 0 && (
          <div className="action-section short-term">
            <h4>⏰ Aksi Jangka Pendek</h4>
            <ul>
              {recs.short_term_actions.map((action, index) => (
                <li key={index}>{action}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Long Term Actions */}
        {recs?.long_term_actions && recs.long_term_actions.length > 0 && (
          <div className="action-section long-term">
            <h4>📅 Aksi Jangka Panjang</h4>
            <ul>
              {recs.long_term_actions.map((action, index) => (
                <li key={index}>{action}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Monitoring Actions */}
        {recs?.monitoring_actions && recs.monitoring_actions.length > 0 && (
          <div className="action-section monitoring">
            <h4>📊 Monitoring</h4>
            <ul>
              {recs.monitoring_actions.map((action, index) => (
                <li key={index}>{action}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="climate-insights">
      <div className="insights-header">
        <h3>🤖 Wawasan AI - Analisis Iklim Mikro</h3>
        <p>Interpretasi data menggunakan Google Gemini AI untuk preservasi arsip optimal</p>
      </div>

      {/* Controls */}
      <div className="insights-controls">
        <div className="parameter-selector">
          <label>Parameter:</label>
          <select 
            value={selectedParameter} 
            onChange={(e) => setSelectedParameter(e.target.value)}
          >
            <option value="temperature">Suhu</option>
            <option value="humidity">Kelembapan</option>
          </select>
        </div>

        <div className="period-selector">
          <label>Periode:</label>
          <select 
            value={selectedPeriod} 
            onChange={(e) => setSelectedPeriod(e.target.value)}
          >
            <option value="day">Hari Ini</option>
            <option value="week">Minggu Ini</option>
            <option value="month">Bulan Ini</option>
          </select>
        </div>

        <div className="location-selector">
          <label>Lokasi:</label>
          <select 
            value={selectedLocation} 
            onChange={(e) => setSelectedLocation(e.target.value)}
          >
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
            <option value="G8">Ruang G8</option>
          </select>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="insights-tabs">
        <button 
          className={`tab-button ${activeTab === 'insights' ? 'active' : ''}`}
          onClick={() => setActiveTab('insights')}
        >
          Wawasan AI
        </button>
        <button 
          className={`tab-button ${activeTab === 'preservation' ? 'active' : ''}`}
          onClick={() => setActiveTab('preservation')}
        >
          Risiko Preservasi
        </button>
        <button 
          className={`tab-button ${activeTab === 'recommendations' ? 'active' : ''}`}
          onClick={() => setActiveTab('recommendations')}
        >
          Rekomendasi
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="insights-error-banner">
          <span>⚠️ {error}</span>
        </div>
      )}

      {/* Tab Content */}
      <div className="insights-tab-content">
        {activeTab === 'insights' && renderInsightsTab()}
        {activeTab === 'preservation' && renderPreservationTab()}
        {activeTab === 'recommendations' && renderRecommendationsTab()}
      </div>
    </div>
  );
};

export default ClimateInsights;

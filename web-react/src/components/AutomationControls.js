import React, { useState, useEffect } from 'react';
import { fetchAutomationSettings, updateAutomationSettings } from '../utils/api';

const AutomationControls = () => {
  const [automationEnabled, setAutomationEnabled] = useState(true);
  const [settings, setSettings] = useState({
    temperature: {
      min: 22,  // Selaras dengan backend: target_temperature - tolerance (24-2)
      max: 26,  // Selaras dengan backend: target_temperature + tolerance (24+2)
    },
    humidity: {
      min: 50,  // Selaras dengan backend: target_humidity - tolerance (60-10)
      max: 70,  // Selaras dengan backend: target_humidity + tolerance (60+10)
    },
    responseSensitivity: 'medium', // low, medium, high
  });
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Fetch automation settings
  useEffect(() => {
    const fetchSettings = async () => {
      try {
        setLoading(true);
        const data = await fetchAutomationSettings();
        
        if (data && typeof data === 'object') {
          setSettings(data.settings || settings);
          setDevices(Array.isArray(data.devices) ? data.devices : getDummyDevices());
          setAutomationEnabled(data.enabled !== undefined ? data.enabled : true);
        } else {
          setDevices(getDummyDevices());
        }
        setError(null);
      } catch (err) {
        console.error('Error fetching automation settings:', err);
        setError('Gagal memuat pengaturan otomasi. Silakan coba lagi.');
        // Use dummy data
        setDevices(getDummyDevices());
      } finally {
        setLoading(false);
      }
    };
    
    fetchSettings();
  }, []);

  // Generate dummy devices for testing
  const getDummyDevices = () => {
    return [
      {
        id: 'ac-f3',
        name: 'AC F3',
        type: 'ac',
        location: 'F3',
        status: 'active',
        mode: 'auto',
        error: null
      },
      {
        id: 'ac-f5',
        name: 'AC F5',
        type: 'ac',
        location: 'F5',
        status: 'active',
        mode: 'auto',
        error: null
      },
      {
        id: 'ac-g2',
        name: 'AC G2',
        type: 'ac',
        location: 'G2',
        status: 'active', 
        mode: 'manual',
        error: null
      },
      {
        id: 'dehum-g7',
        name: 'Dehumidifier G7',
        type: 'dehumidifier',
        location: 'G7',
        status: 'active',
        mode: 'auto',
        error: null
      },
      {
        id: 'dehum-f6',
        name: 'Dehumidifier F6',
        type: 'dehumidifier',
        location: 'F6',
        status: 'inactive',
        mode: 'auto',
        error: 'connection_lost'
      },
      {
        id: 'vent-g5',
        name: 'Ventilasi G5',
        type: 'ventilation',
        location: 'G5',
        status: 'active',
        mode: 'auto',
        error: null
      }
    ];
  };

  // Handle toggle automation
  const toggleAutomation = () => {
    setAutomationEnabled(prev => !prev);
  };

  // Handle temperature range change
  const handleTemperatureChange = (value, type) => {
    setSettings(prev => ({
      ...prev,
      temperature: {
        ...prev.temperature,
        [type]: parseInt(value)
      }
    }));
  };

  // Handle humidity range change
  const handleHumidityChange = (value, type) => {
    setSettings(prev => ({
      ...prev,
      humidity: {
        ...prev.humidity,
        [type]: parseInt(value)
      }
    }));
  };

  // Handle sensitivity change
  const handleSensitivityChange = (e) => {
    setSettings(prev => ({
      ...prev,
      responseSensitivity: e.target.value
    }));
  };

  // Handle device mode change
  const handleDeviceModeChange = (deviceId, newMode) => {
    setDevices(prev => 
      prev.map(device => 
        device.id === deviceId ? { ...device, mode: newMode } : device
      )
    );
  };

  // Handle device status toggle
  const handleDeviceToggle = (deviceId) => {
    setDevices(prev => 
      prev.map(device => 
        device.id === deviceId ? 
          { ...device, status: device.status === 'active' ? 'inactive' : 'active' } 
          : device
      )
    );
  };

  // Save settings
  const saveSettings = async () => {
    try {
      await updateAutomationSettings({
        enabled: automationEnabled,
        settings,
        devices
      });
      
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      console.error('Error saving automation settings:', err);
      setError('Gagal menyimpan pengaturan. Silakan coba lagi.');
    }
  };

  return (
    <section className="automation-section">
      <div className="section-header">
        <h2>Kontrol Otomasi</h2>
        <div className="automation-status">
          <span className={`status-indicator ${automationEnabled ? 'active' : 'inactive'}`}></span>
          <span>Sistem Otomasi {automationEnabled ? 'Aktif' : 'Tidak Aktif'}</span>
          <button className="toggle-btn" onClick={toggleAutomation}>
            {automationEnabled ? 'Matikan' : 'Hidupkan'}
          </button>
        </div>
      </div>
      
      {loading ? (
        <div className="loading-indicator">Memuat pengaturan otomasi...</div>
      ) : error ? (
        <div className="error-message">{error}</div>
      ) : (
        <div className="automation-grid">
          <div className="automation-card">
            <h3>Parameter Otomasi</h3>
            <div className="parameter-list">
              <div className="parameter-item">
                <div className="parameter-name">Rentang Suhu Optimal</div>
                <div className="parameter-value">
                  <div className="range-slider">
                    <span className="range-min">{settings.temperature.min}°C</span>
                    <input 
                      type="range" 
                      min="20" 
                      max="24" 
                      value={settings.temperature.min}
                      onChange={(e) => handleTemperatureChange(e.target.value, 'min')}
                    />
                    <span className="range-max">{settings.temperature.max}°C</span>
                    <input 
                      type="range" 
                      min="24" 
                      max="28" 
                      value={settings.temperature.max}
                      onChange={(e) => handleTemperatureChange(e.target.value, 'max')}
                    />
                  </div>
                </div>
              </div>

              <div className="parameter-item">
                <div className="parameter-name">Rentang Kelembapan Optimal</div>
                <div className="parameter-value">
                  <div className="range-slider">
                    <span className="range-min">{settings.humidity.min}%</span>
                    <input 
                      type="range" 
                      min="45" 
                      max="60" 
                      value={settings.humidity.min}
                      onChange={(e) => handleHumidityChange(e.target.value, 'min')}
                    />
                    <span className="range-max">{settings.humidity.max}%</span>
                    <input 
                      type="range" 
                      min="60" 
                      max="75" 
                      value={settings.humidity.max}
                      onChange={(e) => handleHumidityChange(e.target.value, 'max')}
                    />
                  </div>
                </div>
              </div>

              <div className="parameter-item">
                <div className="parameter-name">Sensitivitas Respons</div>
                <div className="parameter-value">
                  <select 
                    value={settings.responseSensitivity} 
                    onChange={handleSensitivityChange}
                  >
                    <option value="low">Rendah (Respons lambat)</option>
                    <option value="medium">Medium (Seimbang)</option>
                    <option value="high">Tinggi (Respons cepat)</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="parameter-actions">
              <button 
                className={`primary-btn ${saveSuccess ? 'success' : ''}`} 
                onClick={saveSettings}
              >
                {saveSuccess ? 'Tersimpan!' : 'Simpan Parameter'}
              </button>
            </div>
          </div>
          
          {/* Kontrol Perangkat disembunyikan sesuai permintaan */}
          {/* 
          <div className="automation-card device-control">
            <h3>Kontrol Perangkat</h3>
            <div className="device-grid">
              {Array.isArray(devices) && devices.map(device => (
                <div key={device.id} className={`device-item ${device.status} ${device.error ? 'error' : ''}`}>
                  <div className="device-header">
                    <span className="device-name">{device.name}</span>
                    <span className="device-location">{device.location}</span>
                  </div>
                  
                  <div className="device-status-indicator">
                    {device.error ? (
                      <div className="device-error">{device.error === 'connection_lost' ? 'Koneksi Terputus' : 'Error'}</div>
                    ) : (
                      <>
                        <span className={`status-dot ${device.status}`}></span>
                        <span className="status-text">{device.status === 'active' ? 'Aktif' : 'Tidak Aktif'}</span>
                      </>
                    )}
                  </div>
                  
                  <div className="device-controls">
                    <div className="mode-selector">
                      <button 
                        className={`mode-btn ${device.mode === 'auto' ? 'active' : ''}`}
                        onClick={() => handleDeviceModeChange(device.id, 'auto')}
                        disabled={!!device.error}
                      >
                        Auto
                      </button>
                      <button 
                        className={`mode-btn ${device.mode === 'manual' ? 'active' : ''}`}
                        onClick={() => handleDeviceModeChange(device.id, 'manual')}
                        disabled={!!device.error}
                      >
                        Manual
                      </button>
                    </div>
                    <button 
                      className="power-btn" 
                      onClick={() => handleDeviceToggle(device.id)}
                      disabled={!!device.error}
                    >
                      {device.status === 'active' ? 'Matikan' : 'Hidupkan'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
          */}
        </div>
      )}
    </section>
  );
};

export default AutomationControls;

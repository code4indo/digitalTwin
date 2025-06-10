import React, { useState, useEffect } from 'react';
import { fetchRoomDetails } from '../utils/api';
import RoomEnvironmentalChart from './RoomEnvironmentalChart';

const RoomDetails = () => {
  const [selectedRoom, setSelectedRoom] = useState('');
  const [roomData, setRoomData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch room details when room selection changes
  useEffect(() => {
    if (!selectedRoom) return;

    const fetchData = async () => {
      try {
        setLoading(true);
        const data = await fetchRoomDetails(selectedRoom);
        console.log('Room data from API:', data);
        setRoomData(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching room details:', err);
        setError('Gagal memuat data ruangan. Silakan coba lagi.');
        
        // Fallback ke data dummy jika API gagal
        console.warn('Menggunakan data dummy sebagai fallback');
        setRoomData(getDummyRoomData(selectedRoom));
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [selectedRoom]);

  // Generate dummy room data for testing
  const getDummyRoomData = (roomId) => {
    const floor = roomId.charAt(0);
    const roomNumber = roomId.substring(1);
    
    return {
      id: roomId,
      name: `Ruang ${roomId}`,
      floor: floor,
      area: Math.floor(Math.random() * 30) + 20, // 20-50 m²
      currentConditions: {
        temperature: parseFloat((Math.random() * 4 + 20).toFixed(1)), // 20-24°C
        humidity: parseFloat((Math.random() * 15 + 45).toFixed(1)), // 45-60%
        co2: Math.floor(Math.random() * 300 + 400), // 400-700 ppm
        light: Math.floor(Math.random() * 300 + 300) // 300-600 lux
      },
      devices: [
        {
          id: `ac-${roomId.toLowerCase()}`,
          name: 'AC',
          status: Math.random() > 0.2 ? 'active' : 'inactive',
          setPoint: Math.floor(Math.random() * 4) + 19 // 19-22°C
        },
        {
          id: `dh-${roomId.toLowerCase()}`,
          name: 'Dehumidifier',
          status: Math.random() > 0.3 ? 'active' : 'inactive',
          setPoint: Math.floor(Math.random() * 10) + 45 // 45-55%
        }
      ],
      statistics: {
        dailyAvg: {
          temperature: parseFloat((Math.random() * 3 + 21).toFixed(1)), // 21-24°C
          humidity: parseFloat((Math.random() * 10 + 48).toFixed(1)) // 48-58%
        },
        timeInOptimalRange: {
          temperature: Math.floor(Math.random() * 30) + 70, // 70-100%
          humidity: Math.floor(Math.random() * 40) + 60 // 60-100%
        }
      }
    };
  };

  // Handle room selection change
  const handleRoomChange = (e) => {
    setSelectedRoom(e.target.value);
  };

  return (
    <section className="room-details-section">
      <div className="section-header">
        <h2>Detail Ruangan</h2>
        <div className="room-selector">
          <select id="room-selector" value={selectedRoom} onChange={handleRoomChange}>
            <option value="">Pilih Ruangan...</option>
            <optgroup label="Lantai F">
              <option value="F2">F2</option>
              <option value="F3">F3</option>
              <option value="F4">F4</option>
              <option value="F5">F5</option>
              <option value="F6">F6</option>
            </optgroup>
            <optgroup label="Lantai G">
              <option value="G2">G2</option>
              <option value="G3">G3</option>
              <option value="G4">G4</option>
              <option value="G5">G5</option>
              <option value="G6">G6</option>
              <option value="G7">G7</option>
              <option value="G8">G8</option>
            </optgroup>
          </select>
        </div>
      </div>
      
      <div className="room-details-container" id="room-details">
        {!selectedRoom && (
          <div className="placeholder-message">Pilih ruangan untuk melihat detail</div>
        )}
        
        {loading && (
          <div className="loading-indicator">Memuat data ruangan...</div>
        )}
        
        {error && (
          <div className="error-message">{error}</div>
        )}
        
        {roomData && !loading && (
          <div className="room-data">
            <div className="room-header">
              <h3>{roomData.name}</h3>
              <div className="room-meta">
                <span>Lantai {roomData.floor}</span>
                <span>{roomData.area} m²</span>
              </div>
            </div>
            
            <div className="room-stats">
              <div className="stat-card">
                <div className="stat-title">Suhu</div>
                <div className="stat-value temperature">{roomData.currentConditions.temperature}°C</div>
                <div className="stat-meta">
                  <div>Rata-rata harian: {roomData.statistics.dailyAvg.temperature}°C</div>
                  <div>Waktu dalam rentang optimal: {roomData.statistics.timeInOptimalRange.temperature}%</div>
                </div>
              </div>
              
              <div className="stat-card">
                <div className="stat-title">Kelembapan</div>
                <div className="stat-value humidity">{roomData.currentConditions.humidity}%</div>
                <div className="stat-meta">
                  <div>Rata-rata harian: {roomData.statistics.dailyAvg.humidity}%</div>
                  <div>Waktu dalam rentang optimal: {roomData.statistics.timeInOptimalRange.humidity}%</div>
                </div>
              </div>
              
              <div className="stat-card">
                <div className="stat-title">CO₂</div>
                <div className="stat-value">{roomData.currentConditions.co2} ppm</div>
                <div className="stat-meta">
                  <div className={roomData.currentConditions.co2 < 600 ? 'optimal' : 'warning'}>
                    {roomData.currentConditions.co2 < 600 ? 'Optimal' : 'Di atas optimal'}
                  </div>
                </div>
              </div>
              
              <div className="stat-card">
                <div className="stat-title">Pencahayaan</div>
                <div className="stat-value">{roomData.currentConditions.light} lux</div>
                <div className="stat-meta">
                  <div className={roomData.currentConditions.light > 300 && roomData.currentConditions.light < 500 ? 'optimal' : 'warning'}>
                    {roomData.currentConditions.light > 300 && roomData.currentConditions.light < 500 ? 'Optimal' : 'Di luar rentang optimal'}
                  </div>
                </div>
              </div>
            </div>
            
            {/* Kontrol Perangkat disembunyikan sesuai permintaan */}
            {/*
            <div className="devices-control">
              <h4>Kontrol Perangkat</h4>
              <div className="device-list">
                {Array.isArray(roomData.devices) && roomData.devices.map(device => (
                  <div key={device.id} className={`device-item ${device.status}`}>
                    <div className="device-info">
                      <div className="device-name">{device.name}</div>
                      <div className="device-status">{device.status === 'active' ? 'Aktif' : 'Tidak Aktif'}</div>
                    </div>
                    <div className="device-controls">
                      <div className="device-setting">
                        <span>Set Point: </span>
                        <span className="setting-value">
                          {device.name === 'AC' ? `${device.setPoint}°C` : `${device.setPoint}%`}
                        </span>
                      </div>
                      <button className="control-btn">
                        {device.status === 'active' ? 'Matikan' : 'Hidupkan'}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            */}
            
            {/* Grafana Dashboard Integration */}
            <div className="room-environmental-trends">
              <h4>Tren Data Lingkungan</h4>
              <RoomEnvironmentalChart 
                roomId={selectedRoom} 
                height={350}
                theme="light"
              />
            </div>
          </div>
        )}
      </div>
    </section>
  );
};

export default RoomDetails;

import React, { useEffect, useRef, useState, useCallback } from 'react';
import * as THREE from 'three';
import { fetchExternalWeatherData, fetchSystemHealth } from '../utils/api';

const EnhancedBuildingModel = () => {
  const containerRef = useRef(null);
  const sceneRef = useRef(null);
  const cameraRef = useRef(null);
  const rendererRef = useRef(null);
  const buildingModelRef = useRef(null);
  const raycasterRef = useRef(new THREE.Raycaster());
  const mouseRef = useRef(new THREE.Vector2());
  
  const [activeRoom, setActiveRoom] = useState('F2');
  const [showHeatMap, setShowHeatMap] = useState(true);
  const [predictiveMode, setPredictiveMode] = useState(false);
  const [timeSlider, setTimeSlider] = useState(0);
  const [roomData, setRoomData] = useState({});
  const [systemHealth, setSystemHealth] = useState(null);
  const [hoveredRoom, setHoveredRoom] = useState(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  // State for real environmental data from API
  const [realEnvironmentalData, setRealEnvironmentalData] = useState(null);

  // Fetch real environmental data from API
  const fetchRealEnvironmentalData = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:8002/stats/environmental/', {
        headers: {
          'X-API-Key': 'development_key_for_testing',
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setRealEnvironmentalData(data);
      console.log('Real environmental data fetched:', data);
      return data;
    } catch (error) {
      console.error('Failed to fetch real environmental data:', error);
      // Return fallback data if API fails
      return {
        temperature: { avg: 22.0, min: 19.0, max: 25.0 },
        humidity: { avg: 50.0, min: 40.0, max: 60.0 },
        timestamp: new Date().toISOString()
      };
    }
  }, []);

  // Generate room data using real environmental data as base
  const generateRoomData = useCallback((roomId) => {
    // Use real environmental data as base, with room-specific variations
    const baseTemp = realEnvironmentalData?.temperature?.avg || 22.0;
    const baseHumidity = realEnvironmentalData?.humidity?.avg || 50.0;
    
    // Create unique seed for each room for consistent but varied values
    const roomSeed = roomId.split('').reduce((acc, char, index) => acc + char.charCodeAt(0) * (index + 1), 0);
    
    // Create deterministic but varied room-specific variations
    // Use sine and cosine for different variation patterns
    const tempSeedA = (roomSeed * 7) % 360;
    const tempSeedB = (roomSeed * 13) % 360;
    const humiditySeedA = (roomSeed * 11) % 360;
    const humiditySeedB = (roomSeed * 17) % 360;
    
    // Generate variations: ±3°C for temperature, ±8% for humidity
    const roomTempVariation = (Math.sin(tempSeedA * Math.PI / 180) + Math.cos(tempSeedB * Math.PI / 180)) * 1.5;
    const roomHumidityVariation = (Math.sin(humiditySeedA * Math.PI / 180) + Math.cos(humiditySeedB * Math.PI / 180)) * 4;
    
    // Add some floor-based variation (F floors vs G floors)
    const floorFactor = roomId.startsWith('F') ? -0.5 : +0.5; // F floors slightly cooler, G floors slightly warmer
    
    const currentTemp = Math.max(18, Math.min(26, baseTemp + roomTempVariation + floorFactor));
    const currentHumidity = Math.max(35, Math.min(65, baseHumidity + roomHumidityVariation));
    
    return {
      id: roomId,
      currentConditions: {
        temperature: parseFloat(currentTemp.toFixed(1)),
        humidity: parseFloat(currentHumidity.toFixed(1)),
        co2: 400 + Math.random() * 200,
        light: 300 + Math.random() * 300
      },
      devices: [
        {
          id: `ac-${roomId.toLowerCase()}`,
          name: 'AC',
          status: Math.random() > 0.2 ? 'active' : 'inactive',
          setPoint: Math.floor(Math.random() * 4) + 19
        },
        {
          id: `dh-${roomId.toLowerCase()}`,
          name: 'Dehumidifier',
          status: Math.random() > 0.3 ? 'active' : 'inactive',
          setPoint: Math.floor(Math.random() * 10) + 45
        }
      ],
      sensorStatus: Math.random() > 0.1 ? 'active' : 'offline',
      lastUpdate: realEnvironmentalData?.timestamp || new Date().toISOString()
    };
  }, [realEnvironmentalData]);

  // Get room status based on temperature and humidity
  const getRoomStatus = useCallback((roomData) => {
    if (!roomData) return 'unknown';
    
    const { temperature, humidity } = roomData.currentConditions;
    
    // Optimal ranges for archive storage
    const tempOptimal = temperature >= 18 && temperature <= 24;
    const humidityOptimal = humidity >= 40 && humidity <= 60;
    
    if (tempOptimal && humidityOptimal) return 'optimal';
    if ((temperature >= 16 && temperature <= 26) && (humidity >= 35 && humidity <= 65)) return 'warning';
    return 'critical';
  }, []);

  // Get color based on room status
  const getStatusColor = useCallback((status) => {
    switch (status) {
      case 'optimal': return 0x4CAF50; // Green
      case 'warning': return 0xFF9800; // Orange
      case 'critical': return 0xF44336; // Red
      case 'unknown': return 0x9E9E9E; // Gray
      default: return 0x9E9E9E;
    }
  }, []);

  // Fetch real environmental data on component mount and periodically
  useEffect(() => {
    // Initial fetch
    fetchRealEnvironmentalData();
    
    // Update data every 5 minutes to get fresh real data
    const dataInterval = setInterval(() => {
      fetchRealEnvironmentalData();
    }, 300000); // 5 minutes
    
    return () => clearInterval(dataInterval);
  }, [fetchRealEnvironmentalData]);

  // Initialize room data
  // Initialize room data (only after real environmental data is available)
  useEffect(() => {
    // Only generate room data if we have real environmental data
    if (!realEnvironmentalData) return;
    
    const rooms = ['F2', 'F3', 'F4', 'F5', 'F6', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8'];
    const data = {};
    
    rooms.forEach(room => {
      data[room] = generateRoomData(room);
    });
    
    setRoomData(data);
    
    // Update data every 30 seconds using real environmental data as base
    const interval = setInterval(() => {
      const updatedData = {};
      rooms.forEach(room => {
        updatedData[room] = generateRoomData(room);
      });
      setRoomData(updatedData);
    }, 30000);
    
    return () => clearInterval(interval);
  }, [generateRoomData, realEnvironmentalData]);

  // Fetch system health data
  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const health = await fetchSystemHealth();
        setSystemHealth(health);
      } catch (error) {
        console.error('Failed to fetch system health:', error);
        setSystemHealth({
          status: 'Unknown',
          active_devices: 8,
          total_devices: 12,
          influxdb_connection: 'connected'
        });
      }
    };
    
    fetchHealth();
    const interval = setInterval(fetchHealth, 60000); // Update every minute
    
    return () => clearInterval(interval);
  }, []);

  // Initialize 3D scene
  useEffect(() => {
    if (!containerRef.current) return;

    // Create scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf5f5f5);
    sceneRef.current = scene;

    // Create camera
    const camera = new THREE.PerspectiveCamera(
      60,
      containerRef.current.clientWidth / containerRef.current.clientHeight,
      0.1,
      1000
    );
    camera.position.set(8, 6, 8);
    camera.lookAt(0, 0, 0);
    cameraRef.current = camera;

    // Create renderer
    const renderer = new THREE.WebGLRenderer({ 
      antialias: true,
      alpha: true,
      powerPreference: "high-performance"
    });
    renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    containerRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // Add lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5, 10, 5);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    scene.add(directionalLight);

    // Create building model
    createEnhancedBuildingModel();

    // Handle window resize
    const handleResize = () => {
      if (!containerRef.current || !cameraRef.current || !rendererRef.current) return;
      
      const width = containerRef.current.clientWidth;
      const height = containerRef.current.clientHeight;
      
      cameraRef.current.aspect = width / height;
      cameraRef.current.updateProjectionMatrix();
      
      rendererRef.current.setSize(width, height);
    };

    window.addEventListener('resize', handleResize);

    // Animation loop
    const animate = () => {
      requestAnimationFrame(animate);
      if (rendererRef.current && sceneRef.current && cameraRef.current) {
        rendererRef.current.render(sceneRef.current, cameraRef.current);
      }
    };

    animate();

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      
      if (containerRef.current && rendererRef.current && rendererRef.current.domElement) {
        containerRef.current.removeChild(rendererRef.current.domElement);
      }
      
      if (sceneRef.current) {
        sceneRef.current.clear();
      }
    };
  }, []);

  // Update room colors when data changes
  useEffect(() => {
    if (!buildingModelRef.current || !showHeatMap) return;

    buildingModelRef.current.traverse((child) => {
      if (child.userData && child.userData.type === 'room') {
        const roomId = child.userData.id;
        const data = roomData[roomId];
        const status = getRoomStatus(data);
        const color = getStatusColor(status);
        
        if (child.material) {
          child.material.color.setHex(color);
          child.material.opacity = 0.8;
          child.material.transparent = true;
        }
      }
    });
  }, [roomData, showHeatMap, getRoomStatus, getStatusColor]);

  // Create enhanced building model
  const createEnhancedBuildingModel = () => {
    if (!sceneRef.current) return;

    const buildingModel = new THREE.Group();
    sceneRef.current.add(buildingModel);
    buildingModelRef.current = buildingModel;

    // Ground floor base
    const groundGeometry = new THREE.BoxGeometry(6, 0.2, 6);
    const groundMaterial = new THREE.MeshStandardMaterial({ color: 0x8D6E63 });
    const ground = new THREE.Mesh(groundGeometry, groundMaterial);
    ground.position.set(0, -0.1, 0);
    ground.receiveShadow = true;
    buildingModel.add(ground);

    // Room positions and configurations
    const roomConfigs = [
      // Floor F
      { id: 'F2', position: { x: -2, y: 1.5, z: -2 }, size: { x: 1.5, y: 0.3, z: 1.5 } },
      { id: 'F3', position: { x: 0, y: 1.5, z: -2 }, size: { x: 1.5, y: 0.3, z: 1.5 } },
      { id: 'F4', position: { x: 2, y: 1.5, z: -2 }, size: { x: 1.5, y: 0.3, z: 1.5 } },
      { id: 'F5', position: { x: -1, y: 1.5, z: 0 }, size: { x: 1.5, y: 0.3, z: 1.5 } },
      { id: 'F6', position: { x: 1, y: 1.5, z: 0 }, size: { x: 1.5, y: 0.3, z: 1.5 } },
      
      // Floor G
      { id: 'G2', position: { x: -2.5, y: 0.5, z: -2.5 }, size: { x: 1.2, y: 0.3, z: 1.2 } },
      { id: 'G3', position: { x: -0.8, y: 0.5, z: -2.5 }, size: { x: 1.2, y: 0.3, z: 1.2 } },
      { id: 'G4', position: { x: 0.8, y: 0.5, z: -2.5 }, size: { x: 1.2, y: 0.3, z: 1.2 } },
      { id: 'G5', position: { x: 2.5, y: 0.5, z: -2.5 }, size: { x: 1.2, y: 0.3, z: 1.2 } },
      { id: 'G6', position: { x: -2, y: 0.5, z: 0 }, size: { x: 1.2, y: 0.3, z: 1.2 } },
      { id: 'G7', position: { x: 0, y: 0.5, z: 0 }, size: { x: 1.2, y: 0.3, z: 1.2 } },
      { id: 'G8', position: { x: 2, y: 0.5, z: 0 }, size: { x: 1.2, y: 0.3, z: 1.2 } },
    ];

    // Create rooms
    roomConfigs.forEach(config => {
      createEnhancedRoom(config, buildingModel);
    });
  };

  // Create enhanced room with sensors and devices
  const createEnhancedRoom = (config, parent) => {
    const group = new THREE.Group();
    
    // Base room geometry
    const roomGeometry = new THREE.BoxGeometry(config.size.x, config.size.y, config.size.z);
    const roomMaterial = new THREE.MeshStandardMaterial({ 
      color: showHeatMap ? getStatusColor(getRoomStatus(roomData[config.id])) : 0xEEEEEE,
      transparent: true,
      opacity: 0.8
    });
    
    const room = new THREE.Mesh(roomGeometry, roomMaterial);
    room.position.set(config.position.x, config.position.y, config.position.z);
    room.castShadow = true;
    room.receiveShadow = true;
    room.userData = { type: 'room', id: config.id };
    group.add(room);

    // Add sensor indicator
    const sensorGeometry = new THREE.SphereGeometry(0.06);
    const sensorData = roomData[config.id];
    const sensorActive = sensorData && sensorData.sensorStatus === 'active';
    const sensorMaterial = new THREE.MeshBasicMaterial({ 
      color: sensorActive ? 0x00FF00 : 0xFF0000 
    });
    
    const sensor = new THREE.Mesh(sensorGeometry, sensorMaterial);
    sensor.position.set(
      config.position.x, 
      config.position.y + config.size.y/2 + 0.15, 
      config.position.z
    );
    sensor.userData = { type: 'sensor', roomId: config.id };
    group.add(sensor);

    // Add device indicators
    if (sensorData && sensorData.devices) {
      sensorData.devices.forEach((device, index) => {
        const deviceGeometry = new THREE.BoxGeometry(0.08, 0.08, 0.08);
        const deviceMaterial = new THREE.MeshBasicMaterial({ 
          color: device.status === 'active' ? 0x2196F3 : 0x757575 
        });
        
        const deviceMesh = new THREE.Mesh(deviceGeometry, deviceMaterial);
        deviceMesh.position.set(
          config.position.x + (index * 0.15 - 0.075), 
          config.position.y + config.size.y/2 + 0.25, 
          config.position.z
        );
        deviceMesh.userData = { type: 'device', device, roomId: config.id };
        group.add(deviceMesh);
      });
    }

    // Add temperature/humidity indicators (floating text would be added in real implementation)
    if (sensorData && showHeatMap) {
      // Create a small info panel above the room
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');
      canvas.width = 256;
      canvas.height = 128;
      
      context.fillStyle = 'rgba(0, 0, 0, 0.8)';
      context.fillRect(0, 0, 256, 128);
      
      context.fillStyle = 'white';
      context.font = '20px Arial';
      context.textAlign = 'center';
      context.fillText(config.id, 128, 30);
      context.fillText(`${sensorData.currentConditions.temperature.toFixed(1)}°C`, 128, 60);
      context.fillText(`${sensorData.currentConditions.humidity.toFixed(0)}%`, 128, 90);
      
      const texture = new THREE.CanvasTexture(canvas);
      const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
      const sprite = new THREE.Sprite(spriteMaterial);
      sprite.position.set(
        config.position.x,
        config.position.y + config.size.y/2 + 0.4,
        config.position.z
      );
      sprite.scale.set(0.5, 0.25, 1);
      sprite.userData = { type: 'info', roomId: config.id };
      group.add(sprite);
    }

    parent.add(group);
  };

  // Handle mouse events for interaction
  const handleMouseMove = (event) => {
    if (!rendererRef.current || !cameraRef.current || !sceneRef.current) return;

    const rect = rendererRef.current.domElement.getBoundingClientRect();
    mouseRef.current.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouseRef.current.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    
    setMousePosition({ x: event.clientX, y: event.clientY });

    raycasterRef.current.setFromCamera(mouseRef.current, cameraRef.current);
    const intersects = raycasterRef.current.intersectObjects(sceneRef.current.children, true);

    if (intersects.length > 0) {
      const object = intersects[0].object;
      if (object.userData.type === 'room') {
        setHoveredRoom(object.userData.id);
        rendererRef.current.domElement.style.cursor = 'pointer';
      } else {
        setHoveredRoom(null);
        rendererRef.current.domElement.style.cursor = 'default';
      }
    } else {
      setHoveredRoom(null);
      rendererRef.current.domElement.style.cursor = 'default';
    }
  };

  const handleClick = (event) => {
    if (!raycasterRef.current || !cameraRef.current || !sceneRef.current) return;

    const rect = rendererRef.current.domElement.getBoundingClientRect();
    mouseRef.current.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouseRef.current.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

    raycasterRef.current.setFromCamera(mouseRef.current, cameraRef.current);
    const intersects = raycasterRef.current.intersectObjects(sceneRef.current.children, true);

    if (intersects.length > 0) {
      const object = intersects[0].object;
      if (object.userData.type === 'room') {
        setActiveRoom(object.userData.id);
      }
    }
  };

  // Room info tooltip component
  const renderRoomTooltip = () => {
    if (!hoveredRoom || !roomData[hoveredRoom]) return null;

    const data = roomData[hoveredRoom];
    const status = getRoomStatus(data);

    return (
      <div 
        className="room-info-panel"
        style={{
          left: mousePosition.x + 10,
          top: mousePosition.y - 100
        }}
      >
        <h4>{hoveredRoom}</h4>
        <div className="condition">
          Status: <span className={`status ${status}`}>{status.toUpperCase()}</span>
        </div>
        <div className="condition">
          Suhu: {data.currentConditions.temperature.toFixed(1)}°C
        </div>
        <div className="condition">
          Kelembapan: {data.currentConditions.humidity.toFixed(1)}%
        </div>
        <div className="condition">
          Sensor: <span className={`sensor-status ${data.sensorStatus}`}>
            {data.sensorStatus === 'active' ? 'Aktif' : 'Offline'}
          </span>
        </div>
        <div className="devices" style={{display: 'none'}}>
          <strong>Perangkat:</strong>
          {data.devices.map((device, index) => (
            <div key={index}>
              <span className={`device-status ${device.status}`}></span>
              {device.name}: {device.status === 'active' ? 'ON' : 'OFF'}
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="card enhanced-building-view">
      <h2>Digital Twin - Manajemen Iklim Mikro</h2>
      
      <div className="model-controls">
        <button 
          onClick={() => setShowHeatMap(!showHeatMap)}
          className={showHeatMap ? 'active' : ''}
          title="Toggle heat map visualization"
        >
          🌡️ Heat Map
        </button>
        
        <button 
          onClick={() => setPredictiveMode(!predictiveMode)}
          className={predictiveMode ? 'active' : ''}
          title="Toggle predictive mode"
        >
          🔮 Prediksi
        </button>
        
        {predictiveMode && (
          <div className="prediction-controls">
            <label>Prediksi +{timeSlider}h:</label>
            <input
              type="range"
              min="0"
              max="24"
              value={timeSlider}
              onChange={(e) => setTimeSlider(e.target.value)}
              title={`Prediksi ${timeSlider} jam ke depan`}
            />
          </div>
        )}
        
        <div className="system-status">
          {systemHealth && (
            <span className={`health-indicator ${systemHealth.status?.toLowerCase()}`}>
              🏥 Sistem: {systemHealth.status}
            </span>
          )}
        </div>
      </div>

      <div className="model-container">
        <div 
          ref={containerRef} 
          className="building-model-3d"
          onMouseMove={handleMouseMove}
          onClick={handleClick}
        ></div>
        
        {renderRoomTooltip()}
      </div>

      <div className="legend">
        <div className="legend-title">Status Ruangan:</div>
        <div className="legend-item">
          <span className="color-box optimal"></span>
          Optimal (18-24°C, 40-60% RH)
        </div>
        <div className="legend-item">
          <span className="color-box warning"></span>
          Warning (16-26°C, 35-65% RH)
        </div>
        <div className="legend-item">
          <span className="color-box critical"></span>
          Critical (Di luar rentang)
        </div>
        <div className="legend-item">
          <span className="color-box unknown"></span>
          Tidak Diketahui
        </div>
      </div>

      <div className="active-room-info">
        {activeRoom && roomData[activeRoom] && (
          <div className="selected-room-details">
            <h3>Ruangan Aktif: {activeRoom}</h3>
            <div className="room-stats">
              <div className="stat">
                <span className="label">Suhu:</span>
                <span className="value">{roomData[activeRoom].currentConditions.temperature.toFixed(1)}°C</span>
              </div>
              <div className="stat">
                <span className="label">Kelembapan:</span>
                <span className="value">{roomData[activeRoom].currentConditions.humidity.toFixed(1)}%</span>
              </div>
              <div className="stat">
                <span className="label">Status:</span>
                <span className={`value status ${getRoomStatus(roomData[activeRoom])}`}>
                  {getRoomStatus(roomData[activeRoom]).toUpperCase()}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default EnhancedBuildingModel;

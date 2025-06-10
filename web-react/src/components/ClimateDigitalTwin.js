import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import './ClimateDigitalTwin.css';

const ClimateDigitalTwin = () => {
  const containerRef = useRef(null);
  const sceneRef = useRef(null);
  const cameraRef = useRef(null);
  const rendererRef = useRef(null);
  const buildingModelRef = useRef(null);
  const controlsRef = useRef(null);
  
  const [activeRoom, setActiveRoom] = useState('F2');
  const [showHeatMap, setShowHeatMap] = useState(true);
  const [climateData, setClimateData] = useState({});
  const [viewMode, setViewMode] = useState('temperature'); // temperature, humidity, air_quality
  const [apiStatus, setApiStatus] = useState('loading'); // loading, connected, disconnected
  const [lastUpdate, setLastUpdate] = useState(null);

  // Fetch real climate data from API
  const fetchRealClimateData = async () => {
    const rooms = ['F2', 'F3', 'F4', 'F5', 'F6', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8'];
    const data = {};
    
    const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';
    const API_KEY = process.env.REACT_APP_API_KEY || 'development_key_for_testing';
    
    try {
      // Fetch data for all rooms in parallel
      const promises = rooms.map(async (room) => {
        try {
          const response = await fetch(`${API_BASE_URL}/rooms/${room}`, {
            headers: {
              'X-API-Key': API_KEY,
              'Content-Type': 'application/json'
            }
          });
          
          if (response.ok) {
            const roomData = await response.json();
            return {
              room,
              data: {
                temperature: roomData.current_conditions?.temperature || 22.0,
                humidity: roomData.current_conditions?.humidity || 50.0,
                airQuality: roomData.current_conditions?.air_quality || 85,
                devices: {
                  hvac: roomData.devices?.find(d => d.type === 'AC')?.status === 'active' || false,
                  dehumidifier: roomData.devices?.find(d => d.type === 'Dehumidifier')?.status === 'active' || false,
                  airPurifier: roomData.devices?.find(d => d.type === 'Fan')?.status === 'active' || false
                },
                get status() {
                  return determineRoomStatus(
                    roomData.current_conditions?.temperature || 22.0,
                    roomData.current_conditions?.humidity || 50.0,
                    this.devices
                  );
                }
              }
            };
          } else {
            console.warn(`Failed to fetch data for room ${room}:`, response.status);
            return { room, data: generateFallbackData(room) };
          }
        } catch (error) {
          console.warn(`Error fetching data for room ${room}:`, error);
          return { room, data: generateFallbackData(room) };
        }
      });
      
      const results = await Promise.all(promises);
      results.forEach(({ room, data: roomData }) => {
        data[room] = roomData;
      });
      
      console.log('Successfully fetched real climate data for', Object.keys(data).length, 'rooms');
      return data;
      
    } catch (error) {
      console.error('Error fetching climate data:', error);
      return generateFallbackClimateData();
    }
  };

  // Determine room status based on temperature, humidity, and device status
  const determineRoomStatus = (temperature, humidity, devices = null) => {
    // Optimal ranges: temperature 20-26°C, humidity 40-60%
    const tempOk = temperature >= 20 && temperature <= 26;
    const humidityOk = humidity >= 40 && humidity <= 60;
    
    // Critical conditions based on environment
    const tempCritical = temperature < 18 || temperature > 28;
    const humidityCritical = humidity < 30 || humidity > 70;
    
    // Check device status if available
    let deviceIssues = false;
    if (devices) {
      // If temperature is too high and HVAC is off, that's a problem
      if (temperature > 26 && !devices.hvac) {
        deviceIssues = true;
      }
      // If humidity is too high and dehumidifier is off, that's a problem
      if (humidity > 60 && !devices.dehumidifier) {
        deviceIssues = true;
      }
      // If air quality devices are all off in critical conditions
      if ((tempCritical || humidityCritical) && !devices.hvac && !devices.dehumidifier && !devices.airPurifier) {
        deviceIssues = true;
      }
    }
    
    // Determine status with device consideration
    if (tempCritical || humidityCritical || deviceIssues) {
      return 'critical';
    }
    
    if (!tempOk || !humidityOk) {
      return 'warning';
    }
    
    return 'normal';
  };

  // Generate fallback data for individual room when API fails
  const generateFallbackData = (room) => {
    const baseTemp = room.startsWith('F') ? 23 : 22; // Slight variation between buildings
    const temperature = baseTemp + (Math.random() - 0.5) * 4;
    const humidity = 50 + (Math.random() - 0.5) * 20;
    const devices = {
      hvac: Math.random() > 0.5,
      dehumidifier: Math.random() > 0.7,
      airPurifier: Math.random() > 0.6
    };
    
    return {
      temperature,
      humidity,
      airQuality: 80 + Math.random() * 20,
      devices,
      status: determineRoomStatus(temperature, humidity, devices)
    };
  };

  // Fallback when entire API is unavailable
  const generateFallbackClimateData = () => {
    const rooms = ['F2', 'F3', 'F4', 'F5', 'F6', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8'];
    const data = {};
    
    rooms.forEach(room => {
      data[room] = generateFallbackData(room);
    });
    
    console.warn('Using fallback climate data - API unavailable');
    return data;
  };

  // Initialize 3D scene
  useEffect(() => {
    if (!containerRef.current) return;
    
    // Create scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf8f9fa);
    sceneRef.current = scene;
    
    // Create camera
    const camera = new THREE.PerspectiveCamera(
      60,
      containerRef.current.clientWidth / containerRef.current.clientHeight,
      0.1,
      1000
    );
    camera.position.set(15, 15, 15);
    camera.lookAt(0, 8, 0);
    cameraRef.current = camera;
    
    // Create renderer
    const renderer = new THREE.WebGLRenderer({ 
      antialias: true,
      alpha: true 
    });
    renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    containerRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;
    
    // Initialize OrbitControls for interactive navigation
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.1;
    controls.enableZoom = true;
    controls.enablePan = true;
    controls.enableRotate = true;
    
    // Set control limits for larger building model
    controls.minDistance = 5;
    controls.maxDistance = 50;
    controls.minPolarAngle = 0;
    controls.maxPolarAngle = Math.PI / 2;
    
    // Set auto rotation (optional)
    controls.autoRotate = false;
    controls.autoRotateSpeed = 2.0;
    
    controlsRef.current = controls;
    
    // Add lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5, 10, 5);
    directionalLight.castShadow = true;
    scene.add(directionalLight);
    
    // Create building model with climate visualization
    createClimateModel();
    
    // Initialize climate data from API
    loadClimateData();
    
    // Animation loop
    const animate = () => {
      requestAnimationFrame(animate);
      
      // Update controls
      if (controlsRef.current) {
        controlsRef.current.update();
      }
      
      if (rendererRef.current && sceneRef.current && cameraRef.current) {
        rendererRef.current.render(sceneRef.current, cameraRef.current);
      }
    };
    animate();
    
    // Handle resize
    const handleResize = () => {
      if (!containerRef.current || !cameraRef.current || !rendererRef.current) return;
      
      const width = containerRef.current.clientWidth;
      const height = containerRef.current.clientHeight;
      
      cameraRef.current.aspect = width / height;
      cameraRef.current.updateProjectionMatrix();
      rendererRef.current.setSize(width, height);
    };
    
    window.addEventListener('resize', handleResize);
    
    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      if (controlsRef.current) {
        controlsRef.current.dispose();
      }
      if (containerRef.current && rendererRef.current) {
        containerRef.current.removeChild(rendererRef.current.domElement);
      }
      if (sceneRef.current) {
        sceneRef.current.clear();
      }
    };
  }, []);

  // Load climate data from API with automatic refresh
  const loadClimateData = async () => {
    try {
      setApiStatus('loading');
      const data = await fetchRealClimateData();
      setClimateData(data);
      setApiStatus('connected');
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Failed to load climate data:', error);
      setClimateData(generateFallbackClimateData());
      setApiStatus('disconnected');
    }
  };

  // Auto-refresh data every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      loadClimateData();
    }, 30000); // 30 seconds

    return () => clearInterval(interval);
  }, []);

  // Update climate visualization when data or view mode changes
  useEffect(() => {
    if (buildingModelRef.current && Object.keys(climateData).length > 0) {
      updateClimateVisualization();
    }
  }, [climateData, viewMode, showHeatMap]);

  // Camera preset functions
  const setCameraPreset = (preset) => {
    if (!cameraRef.current || !controlsRef.current) return;
    
    const camera = cameraRef.current;
    const controls = controlsRef.current;
    
    switch (preset) {
      case 'top':
        camera.position.set(0, 25, 0);
        controls.target.set(0, 10, 0);
        break;
      case 'front':
        camera.position.set(0, 12, 20);
        controls.target.set(0, 10, 0);
        break;
      case 'side':
        camera.position.set(20, 12, 0);
        controls.target.set(0, 10, 0);
        break;
      case 'isometric':
        camera.position.set(15, 15, 15);
        controls.target.set(0, 8, 0);
        break;
      case 'overview':
        camera.position.set(0, 30, 25);
        controls.target.set(0, 8, 0);
        break;
      default:
        camera.position.set(15, 15, 15);
        controls.target.set(0, 8, 0);
    }
    
    controls.update();
  };

  const toggleAutoRotate = () => {
    if (controlsRef.current) {
      controlsRef.current.autoRotate = !controlsRef.current.autoRotate;
    }
  };

  const resetCamera = () => {
    setCameraPreset('isometric');
  };

  const createClimateModel = () => {
    if (!sceneRef.current) return;
    
    const buildingGroup = new THREE.Group();
    sceneRef.current.add(buildingGroup);
    buildingModelRef.current = buildingGroup;
    
    // Create two separate buildings positioned side by side
    // Building G (Arsip Fisik) - 7 floors (G2-G8)
    createBuilding('G', -6, ['G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8'], 0x3498db, 'Gedung G - Arsip Fisik');
    
    // Building F (Arsip Digital) - 5 floors (F2-F6)  
    createBuilding('F', 6, ['F2', 'F3', 'F4', 'F5', 'F6'], 0x2ecc71, 'Gedung F - Arsip Digital');
    
    // Add ground plane
    createGroundPlane();
    
    // Add building labels
    createBuildingLabels();
  };

  const createBuilding = (buildingName, xOffset, floors, baseColor, label) => {
    if (!buildingModelRef.current) return;
    
    const floorHeight = 3; // Height between floors
    const buildingWidth = 8;
    const buildingDepth = 6;
    const wallThickness = 0.2;
    
    floors.forEach((floorId, index) => {
      const yPosition = index * floorHeight;
      
      // Create floor structure
      createFloorStructure(floorId, buildingName, xOffset, yPosition, buildingWidth, buildingDepth, baseColor, index === 0);
      
      // Create room on this floor
      createRoomVisualization(floorId, buildingName, xOffset, yPosition + 0.1, buildingWidth, buildingDepth);
    });
    
    // Create building exterior walls
    createBuildingExterior(buildingName, xOffset, floors.length * floorHeight, buildingWidth, buildingDepth, baseColor);
  };

  const createFloorStructure = (floorId, buildingName, xOffset, yPosition, width, depth, baseColor, isGround) => {
    if (!buildingModelRef.current) return;
    
    // Floor slab
    const floorGeometry = new THREE.BoxGeometry(width, 0.3, depth);
    const floorMaterial = new THREE.MeshStandardMaterial({ 
      color: isGround ? 0x95a5a6 : baseColor,
      transparent: true,
      opacity: 0.9
    });
    const floor = new THREE.Mesh(floorGeometry, floorMaterial);
    floor.position.set(xOffset, yPosition, 0);
    floor.receiveShadow = true;
    floor.castShadow = true;
    floor.userData = { type: 'floor', floorId, buildingName };
    buildingModelRef.current.add(floor);
    
    // Ceiling (except for top floor)
    const ceilingGeometry = new THREE.BoxGeometry(width - 0.4, 0.2, depth - 0.4);
    const ceilingMaterial = new THREE.MeshStandardMaterial({ 
      color: 0xf8f9fa,
      transparent: true,
      opacity: 0.6
    });
    const ceiling = new THREE.Mesh(ceilingGeometry, ceilingMaterial);
    ceiling.position.set(xOffset, yPosition + 2.8, 0);
    ceiling.receiveShadow = true;
    buildingModelRef.current.add(ceiling);
  };

  const createBuildingExterior = (buildingName, xOffset, totalHeight, width, depth, baseColor) => {
    if (!buildingModelRef.current) return;
    
    const wallThickness = 0.2;
    const windowColor = 0x85c1e9;
    
    // Front and back walls
    for (let side = 0; side < 2; side++) {
      const wallGeometry = new THREE.BoxGeometry(width, totalHeight, wallThickness);
      const wallMaterial = new THREE.MeshStandardMaterial({ 
        color: baseColor,
        transparent: true,
        opacity: 0.8
      });
      const wall = new THREE.Mesh(wallGeometry, wallMaterial);
      wall.position.set(xOffset, totalHeight / 2, side === 0 ? depth/2 : -depth/2);
      wall.castShadow = true;
      wall.receiveShadow = true;
      buildingModelRef.current.add(wall);
      
      // Add windows
      createWindows(xOffset, totalHeight, side === 0 ? depth/2 + 0.1 : -depth/2 - 0.1, width, windowColor);
    }
    
    // Side walls
    for (let side = 0; side < 2; side++) {
      const wallGeometry = new THREE.BoxGeometry(wallThickness, totalHeight, depth);
      const wallMaterial = new THREE.MeshStandardMaterial({ 
        color: baseColor,
        transparent: true,
        opacity: 0.8
      });
      const wall = new THREE.Mesh(wallGeometry, wallMaterial);
      wall.position.set(xOffset + (side === 0 ? width/2 : -width/2), totalHeight / 2, 0);
      wall.castShadow = true;
      wall.receiveShadow = true;
      buildingModelRef.current.add(wall);
    }
  };

  const createWindows = (xOffset, totalHeight, zPosition, buildingWidth, windowColor) => {
    if (!buildingModelRef.current) return;
    
    const windowWidth = 1.2;
    const windowHeight = 1.5;
    const windowsPerFloor = 4;
    const floorHeight = 3;
    const floors = Math.floor(totalHeight / floorHeight);
    
    for (let floor = 0; floor < floors; floor++) {
      for (let i = 0; i < windowsPerFloor; i++) {
        const windowGeometry = new THREE.PlaneGeometry(windowWidth, windowHeight);
        const windowMaterial = new THREE.MeshStandardMaterial({ 
          color: windowColor,
          transparent: true,
          opacity: 0.7,
          emissive: windowColor,
          emissiveIntensity: 0.1
        });
        const window = new THREE.Mesh(windowGeometry, windowMaterial);
        
        const xPos = xOffset + (i - (windowsPerFloor - 1) / 2) * (buildingWidth / windowsPerFloor);
        const yPos = floor * floorHeight + floorHeight / 2 + 0.5;
        
        window.position.set(xPos, yPos, zPosition);
        buildingModelRef.current.add(window);
      }
    }
  };

  const createGroundPlane = () => {
    if (!buildingModelRef.current) return;
    
    const groundGeometry = new THREE.PlaneGeometry(30, 20);
    const groundMaterial = new THREE.MeshStandardMaterial({ 
      color: 0x7fb069,
      transparent: true,
      opacity: 0.8
    });
    const ground = new THREE.Mesh(groundGeometry, groundMaterial);
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = -0.5;
    ground.receiveShadow = true;
    buildingModelRef.current.add(ground);
  };

  const createBuildingLabels = () => {
    if (!buildingModelRef.current) return;
    
    // Label for Building G
    createBuildingLabel('GEDUNG G\nArsip Fisik\n(G2-G8)', -6, 21, 0x3498db);
    
    // Label for Building F  
    createBuildingLabel('GEDUNG F\nArsip Digital\n(F2-F6)', 6, 15, 0x2ecc71);
  };

  const createBuildingLabel = (text, xPos, yPos, color) => {
    if (!buildingModelRef.current) return;
    
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = 256;
    canvas.height = 128;
    
    // Background
    context.fillStyle = 'rgba(255, 255, 255, 0.9)';
    context.fillRect(0, 0, 256, 128);
    
    // Border
    context.strokeStyle = `#${color.toString(16)}`;
    context.lineWidth = 4;
    context.strokeRect(2, 2, 252, 124);
    
    // Text
    context.fillStyle = `#${color.toString(16)}`;
    context.font = 'bold 18px Arial';
    context.textAlign = 'center';
    
    const lines = text.split('\n');
    lines.forEach((line, index) => {
      context.fillText(line, 128, 30 + index * 25);
    });
    
    const texture = new THREE.CanvasTexture(canvas);
    const labelMaterial = new THREE.MeshBasicMaterial({ 
      map: texture,
      transparent: true
    });
    const labelGeometry = new THREE.PlaneGeometry(4, 2);
    const label = new THREE.Mesh(labelGeometry, labelMaterial);
    label.position.set(xPos, yPos, 0);
    
    if (cameraRef.current) {
      label.lookAt(cameraRef.current.position);
    }
    
    buildingModelRef.current.add(label);
  };

  const createRoomVisualization = (roomId, buildingName, xOffset, yPosition, buildingWidth, buildingDepth) => {
    if (!buildingModelRef.current) return;
    
    // Room interior representation
    const roomWidth = buildingWidth - 1;
    const roomDepth = buildingDepth - 1; 
    const roomHeight = 2.5;
    
    // Room volume visualization (transparent box)
    const roomGeometry = new THREE.BoxGeometry(roomWidth, roomHeight, roomDepth);
    const roomMaterial = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      transparent: true,
      opacity: 0.2,
      wireframe: false
    });
    
    const room = new THREE.Mesh(roomGeometry, roomMaterial);
    room.position.set(xOffset, yPosition + roomHeight/2, 0);
    room.userData = { roomId, buildingName, type: 'room' };
    room.castShadow = true;
    room.receiveShadow = true;
    buildingModelRef.current.add(room);
    
    // Room label (floating above room)
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = 128;
    canvas.height = 64;
    
    // Background
    context.fillStyle = 'rgba(255, 255, 255, 0.9)';
    context.fillRect(0, 0, 128, 64);
    
    // Border based on building
    context.strokeStyle = buildingName === 'G' ? '#3498db' : '#2ecc71';
    context.lineWidth = 2;
    context.strokeRect(1, 1, 126, 62);
    
    // Text
    context.fillStyle = buildingName === 'G' ? '#3498db' : '#2ecc71';
    context.font = 'bold 20px Arial';
    context.textAlign = 'center';
    context.fillText(roomId, 64, 40);
    
    const texture = new THREE.CanvasTexture(canvas);
    const labelMaterial = new THREE.MeshBasicMaterial({ 
      map: texture,
      transparent: true
    });
    const labelGeometry = new THREE.PlaneGeometry(1.5, 0.75);
    const label = new THREE.Mesh(labelGeometry, labelMaterial);
    label.position.set(xOffset, yPosition + roomHeight + 0.5, 0);
    
    // Make label always face camera
    if (cameraRef.current) {
      label.lookAt(cameraRef.current.position);
    }
    
    buildingModelRef.current.add(label);
    
    // Add some interior details
    createRoomInterior(roomId, xOffset, yPosition, roomWidth, roomDepth, roomHeight);
  };

  const createRoomInterior = (roomId, xOffset, yPosition, roomWidth, roomDepth, roomHeight) => {
    if (!buildingModelRef.current) return;
    
    // Add some furniture/equipment representations
    const equipmentColor = 0x34495e;
    
    // HVAC unit representation
    const hvacGeometry = new THREE.BoxGeometry(0.5, 0.3, 0.5);
    const hvacMaterial = new THREE.MeshStandardMaterial({ color: equipmentColor });
    const hvac = new THREE.Mesh(hvacGeometry, hvacMaterial);
    hvac.position.set(xOffset - roomWidth/3, yPosition + 0.15, roomDepth/3);
    hvac.userData = { type: 'hvac', roomId };
    buildingModelRef.current.add(hvac);
    
    // Sensor representation
    const sensorGeometry = new THREE.SphereGeometry(0.1, 8, 8);
    const sensorMaterial = new THREE.MeshStandardMaterial({ 
      color: 0xe74c3c,
      emissive: 0xe74c3c,
      emissiveIntensity: 0.2
    });
    const sensor = new THREE.Mesh(sensorGeometry, sensorMaterial);
    sensor.position.set(xOffset, yPosition + roomHeight - 0.2, 0);
    sensor.userData = { type: 'sensor', roomId };
    buildingModelRef.current.add(sensor);
  };

  const updateClimateVisualization = () => {
    if (!buildingModelRef.current) return;
    
    buildingModelRef.current.traverse((child) => {
      if (child.userData && child.userData.roomId && child.userData.type === 'room') {
        const roomId = child.userData.roomId;
        const data = climateData[roomId];
        
        if (data && child.material) {
          const color = getClimateColor(data, viewMode);
          child.material.color.setHex(color);
          child.material.opacity = showHeatMap ? 0.6 : 0.2;
        }
      }
    });
  };

  const getClimateColor = (data, mode) => {
    let value, min, max;
    
    switch (mode) {
      case 'temperature':
        value = data.temperature;
        min = 18;
        max = 30;
        break;
      case 'humidity':
        value = data.humidity;
        min = 30;
        max = 80;
        break;
      case 'air_quality':
        value = data.airQuality;
        min = 0;
        max = 100;
        break;
      default:
        return 0xcccccc;
    }
    
    // Normalize value to 0-1
    const normalized = Math.max(0, Math.min(1, (value - min) / (max - min)));
    
    // Priority 1: Status-based coloring (critical conditions)
    if (data.status === 'critical') {
      return 0xe74c3c; // Red - critical issues
    } else if (data.status === 'warning') {
      return 0xf39c12; // Orange - warning conditions
    }
    
    // Priority 2: Device malfunction indication
    if (data.devices) {
      // Temperature issues with HVAC off
      if (mode === 'temperature' && data.temperature > 26 && !data.devices.hvac) {
        return 0xff6b6b; // Light red - HVAC should be on
      }
      // Humidity issues with dehumidifier off
      if (mode === 'humidity' && data.humidity > 60 && !data.devices.dehumidifier) {
        return 0x74b9ff; // Light blue - dehumidifier should be on
      }
      // All devices off in poor conditions
      if (!data.devices.hvac && !data.devices.dehumidifier && !data.devices.airPurifier) {
        if (data.temperature > 25 || data.humidity > 65) {
          return 0xff7675; // Pink/red - devices should be running
        }
      }
    }
    
    // Priority 3: Normal heat map coloring
    if (mode === 'temperature') {
      // Blue (cold) to Red (hot)
      const r = Math.floor(255 * normalized);
      const b = Math.floor(255 * (1 - normalized));
      return (r << 16) | b;
    } else if (mode === 'humidity') {
      // Green (low) to Blue (high)
      const g = Math.floor(255 * (1 - normalized));
      const b = Math.floor(255 * normalized);
      return (g << 8) | b;
    } else {
      // Air quality: Green (good) to Red (poor)
      const r = Math.floor(255 * (1 - normalized));
      const g = Math.floor(255 * normalized);
      return (r << 16) | (g << 8);
    }
  };

  const refreshData = () => {
    loadClimateData();
  };

  const getRoomInfo = (roomId) => {
    const data = climateData[roomId];
    if (!data) return null;
    
    return (
      <div className="room-info-popup">
        <h4>{roomId}</h4>
        <div className="climate-metrics">
          <div className="metric">
            <span className="label">Suhu:</span>
            <span className="value">{data.temperature.toFixed(1)}°C</span>
          </div>
          <div className="metric">
            <span className="label">Kelembaban:</span>
            <span className="value">{data.humidity.toFixed(1)}%</span>
          </div>
          <div className="metric">
            <span className="label">Kualitas Udara:</span>
            <span className="value">{data.airQuality.toFixed(0)} AQI</span>
          </div>
          <div className="metric">
            <span className="label">Status:</span>
            <span className={`status ${data.status}`}>{data.status}</span>
          </div>
        </div>
        {/* Status Perangkat disembunyikan sesuai permintaan */}
        {/*
        <div className="device-status">
          <h5>Status Perangkat:</h5>
          <div className={`device-item ${data.devices.hvac ? 'active' : 'inactive'}`}>
            <span className="device-icon">❄️</span>
            <span className="device-name">HVAC/AC</span>
            <span className="device-indicator">{data.devices.hvac ? '✓ Aktif' : '✗ Mati'}</span>
            {!data.devices.hvac && data.temperature > 26 && (
              <span className="device-warning">⚠️ Suhu tinggi!</span>
            )}
          </div>
          <div className={`device-item ${data.devices.dehumidifier ? 'active' : 'inactive'}`}>
            <span className="device-icon">💧</span>
            <span className="device-name">Dehumidifier</span>
            <span className="device-indicator">{data.devices.dehumidifier ? '✓ Aktif' : '✗ Mati'}</span>
            {!data.devices.dehumidifier && data.humidity > 60 && (
              <span className="device-warning">⚠️ Kelembaban tinggi!</span>
            )}
          </div>
          <div className={`device-item ${data.devices.airPurifier ? 'active' : 'inactive'}`}>
            <span className="device-icon">🌪️</span>
            <span className="device-name">Air Purifier</span>
            <span className="device-indicator">{data.devices.airPurifier ? '✓ Aktif' : '✗ Mati'}</span>
          </div>
        </div>
        */}
      </div>
    );
  };

  return (
    <div className="card climate-digital-twin">
      <div className="card-header">
        <h2>🌡️ Digital Twin - Manajemen Iklim Mikro</h2>
        <div className="climate-controls">
          {/* API Status Indicator */}
          <div className={`api-status ${apiStatus}`}>
            <span className="status-indicator"></span>
            <span className="status-text">
              {apiStatus === 'loading' && 'Memuat...'}
              {apiStatus === 'connected' && 'Data Real-time'}
              {apiStatus === 'disconnected' && 'Mode Simulasi'}
            </span>
            {lastUpdate && apiStatus === 'connected' && (
              <span className="last-update">
                Update: {lastUpdate.toLocaleTimeString()}
              </span>
            )}
          </div>
          
          <button
            className={`control-btn ${showHeatMap ? 'active' : ''}`}
            onClick={() => setShowHeatMap(!showHeatMap)}
          >
            Heat Map
          </button>
          <select 
            value={viewMode} 
            onChange={(e) => setViewMode(e.target.value)}
            className="view-selector"
          >
            <option value="temperature">Suhu</option>
            <option value="humidity">Kelembaban</option>
            <option value="air_quality">Kualitas Udara</option>
          </select>
          
          <button onClick={refreshData} className="refresh-btn">
            🔄 Refresh
          </button>
        </div>
      </div>
      
      {/* Dedicated 3D Navigation Controls */}
      <div className="navigation-controls-panel">
        <h4>🎮 Kontrol Navigasi 3D</h4>
        <div className="camera-controls-inline">
          <button onClick={() => setCameraPreset('isometric')} title="Tampilan Isometrik">
            🏢 Isometrik
          </button>
          <button onClick={() => setCameraPreset('top')} title="Tampilan Atas">
            ⬆️ Atas
          </button>
          <button onClick={() => setCameraPreset('front')} title="Tampilan Depan">
            ➡️ Depan
          </button>
          <button onClick={() => setCameraPreset('side')} title="Tampilan Samping">
            ↗️ Samping
          </button>
          <button onClick={resetCamera} title="Reset Kamera">
            🔄 Reset
          </button>
          <button onClick={toggleAutoRotate} title="Auto Rotasi">
            🔁 Auto
          </button>
          <button onClick={() => setCameraPreset('overview')} title="Tampilan Overview">
            🌐 Overview
          </button>
        </div>
      </div>
      
      <div className="climate-model-container">
        <div ref={containerRef} className="climate-3d-view"></div>
        
        <div className="climate-legend">
          <h4>Legenda {viewMode === 'temperature' ? 'Suhu' : viewMode === 'humidity' ? 'Kelembaban' : 'Kualitas Udara'}</h4>
          <div className="legend-items">
            {viewMode === 'temperature' && (
              <>
                <div className="legend-item">
                  <div className="color-box" style={{backgroundColor: '#0000ff'}}></div>
                  <span>Dingin (&lt;20°C)</span>
                </div>
                <div className="legend-item">
                  <div className="color-box" style={{backgroundColor: '#00ff00'}}></div>
                  <span>Normal (20-25°C)</span>
                </div>
                <div className="legend-item">
                  <div className="color-box" style={{backgroundColor: '#ff0000'}}></div>
                  <span>Panas (&gt;25°C)</span>
                </div>
                <div className="legend-item">
                  <div className="color-box" style={{backgroundColor: '#ff6b6b'}}></div>
                  <span>Panas + AC Mati</span>
                </div>
              </>
            )}
            {viewMode === 'humidity' && (
              <>
                <div className="legend-item">
                  <div className="color-box" style={{backgroundColor: '#00ff00'}}></div>
                  <span>Rendah (&lt;50%)</span>
                </div>
                <div className="legend-item">
                  <div className="color-box" style={{backgroundColor: '#0000ff'}}></div>
                  <span>Tinggi (&gt;60%)</span>
                </div>
                <div className="legend-item">
                  <div className="color-box" style={{backgroundColor: '#74b9ff'}}></div>
                  <span>Tinggi + Dehumidifier Mati</span>
                </div>
              </>
            )}
            <div className="legend-item">
              <div className="color-box" style={{backgroundColor: '#e74c3c'}}></div>
              <span>Status Kritis</span>
            </div>
            <div className="legend-item">
              <div className="color-box" style={{backgroundColor: '#f39c12'}}></div>
              <span>Status Peringatan</span>
            </div>
            <div className="legend-item">
              <div className="color-box" style={{backgroundColor: '#ff7675'}}></div>
              <span>Perangkat Perlu Diaktifkan</span>
            </div>
          </div>
        </div>
        
        <div className="navigation-instructions">
          <h4>Navigasi 3D</h4>
          <div className="instruction-items">
            <div className="instruction-item">
              <span className="key">🖱️ Drag</span>
              <span>Rotasi model</span>
            </div>
            <div className="instruction-item">
              <span className="key">⚙️ Scroll</span>
              <span>Zoom in/out</span>
            </div>
            <div className="instruction-item">
              <span className="key">🤏 Right-click</span>
              <span>Pan kamera</span>
            </div>
            <div className="instruction-item">
              <span className="key">🏢 Preset</span>
              <span>Gunakan tombol di atas</span>
            </div>
          </div>
        </div>
        
        {activeRoom && climateData[activeRoom] && (
          <div className="room-details-panel">
            {getRoomInfo(activeRoom)}
          </div>
        )}
      </div>
      
      <div className="room-selector-grid">
        <div className="floor-section">
          <h4>Lantai F (Arsip Digital)</h4>
          <div className="room-buttons">
            {['F2', 'F3', 'F4', 'F5', 'F6'].map(room => (
              <button
                key={room}
                className={`room-btn ${activeRoom === room ? 'active' : ''} ${climateData[room]?.status || ''}`}
                onClick={() => setActiveRoom(room)}
              >
                {room}
                {climateData[room] && (
                  <div className="room-status-indicator">
                    <span>{climateData[room].temperature.toFixed(0)}°C</span>
                    <span>{climateData[room].humidity.toFixed(0)}%</span>
                  </div>
                )}
              </button>
            ))}
          </div>
        </div>
        
        <div className="floor-section">
          <h4>Lantai G (Arsip Fisik)</h4>
          <div className="room-buttons">
            {['G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8'].map(room => (
              <button
                key={room}
                className={`room-btn ${activeRoom === room ? 'active' : ''} ${climateData[room]?.status || ''}`}
                onClick={() => setActiveRoom(room)}
              >
                {room}
                {climateData[room] && (
                  <div className="room-status-indicator">
                    <span>{climateData[room].temperature.toFixed(0)}°C</span>
                    <span>{climateData[room].humidity.toFixed(0)}%</span>
                  </div>
                )}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ClimateDigitalTwin;

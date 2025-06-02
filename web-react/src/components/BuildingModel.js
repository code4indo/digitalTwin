import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';

const BuildingModel = () => {
  const containerRef = useRef(null);
  const [activeRoom, setActiveRoom] = useState('F2'); // Changed from activeFloor to activeRoom
  
  // References to Three.js objects
  const sceneRef = useRef(null);
  const cameraRef = useRef(null);
  const rendererRef = useRef(null);
  const buildingModelRef = useRef(null);
  
  // Initialize the 3D model
  useEffect(() => {
    if (!containerRef.current) return;
    
    // Create scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf0f0f0);
    sceneRef.current = scene;
    
    // Create camera with optimal settings for building visualization
    const camera = new THREE.PerspectiveCamera(
      60, // Reduced field of view for better proportions
      containerRef.current.clientWidth / containerRef.current.clientHeight, // Aspect ratio
      0.1, // Near clipping plane
      1000 // Far clipping plane
    );
    camera.position.set(6, 4, 6); // Better initial position for building view
    camera.lookAt(0, 0, 0); // Point camera at center of building
    cameraRef.current = camera;
    
    // Create renderer with enhanced settings
    const renderer = new THREE.WebGLRenderer({ 
      antialias: true,
      alpha: true,
      powerPreference: "high-performance"
    });
    renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)); // Support high DPI displays
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    containerRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;
    
    // Add lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(1, 1, 1);
    scene.add(directionalLight);
    
    // Create building model
    createBuildingModel();
    
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
      
      if (containerRef.current && rendererRef.current) {
        containerRef.current.removeChild(rendererRef.current.domElement);
      }
      
      if (sceneRef.current) {
        sceneRef.current.clear();
      }
    };
  }, []);
  
  // Create a simple building model
  const createBuildingModel = () => {
    if (!sceneRef.current) return;
    
    // Create a group for the building
    const buildingModel = new THREE.Group();
    sceneRef.current.add(buildingModel);
    buildingModelRef.current = buildingModel;
    
    // Create ground floor (G)
    const gFloorGeometry = new THREE.BoxGeometry(4, 0.2, 4);
    const gFloorMaterial = new THREE.MeshStandardMaterial({ color: 0x95a5a6 });
    const gFloor = new THREE.Mesh(gFloorGeometry, gFloorMaterial);
    gFloor.position.set(0, -0.1, 0);
    gFloor.userData.floor = 'G';
    buildingModel.add(gFloor);
    
    // Create first floor (F)
    const fFloorGeometry = new THREE.BoxGeometry(3.6, 0.2, 3.6);
    const fFloorMaterial = new THREE.MeshStandardMaterial({ color: 0xecf0f1 });
    const fFloor = new THREE.Mesh(fFloorGeometry, fFloorMaterial);
    fFloor.position.set(0, 1.1, 0);
    fFloor.userData.floor = 'F';
    buildingModel.add(fFloor);
    
    // Create walls for G floor
    const createWall = (width, height, depth, x, y, z, color) => {
      const geometry = new THREE.BoxGeometry(width, height, depth);
      const material = new THREE.MeshStandardMaterial({ color });
      const wall = new THREE.Mesh(geometry, material);
      wall.position.set(x, y, z);
      return wall;
    };
    
    // Ground floor walls
    const gWallColor = 0xbdc3c7;
    const gWalls = new THREE.Group();
    gWalls.userData.floor = 'G';
    
    // Front wall with a gap for door
    const frontWallLeft = createWall(1.5, 1, 0.1, -1.25, 0.5, -2, gWallColor);
    const frontWallRight = createWall(1.5, 1, 0.1, 1.25, 0.5, -2, gWallColor);
    const frontWallTop = createWall(4, 0.2, 0.1, 0, 1.1, -2, gWallColor);
    gWalls.add(frontWallLeft, frontWallRight, frontWallTop);
    
    // Other walls
    const backWall = createWall(4, 1.2, 0.1, 0, 0.6, 2, gWallColor);
    const leftWall = createWall(0.1, 1.2, 4, -2, 0.6, 0, gWallColor);
    const rightWall = createWall(0.1, 1.2, 4, 2, 0.6, 0, gWallColor);
    gWalls.add(backWall, leftWall, rightWall);
    
    buildingModel.add(gWalls);
    
    // First floor walls
    const fWallColor = 0x3498db;
    const fWalls = new THREE.Group();
    fWalls.userData.floor = 'F';
    
    // First floor walls (slightly smaller footprint)
    const fBackWall = createWall(3.6, 1.2, 0.1, 0, 1.8, 1.8, fWallColor);
    const fFrontWall = createWall(3.6, 1.2, 0.1, 0, 1.8, -1.8, fWallColor);
    const fLeftWall = createWall(0.1, 1.2, 3.6, -1.8, 1.8, 0, fWallColor);
    const fRightWall = createWall(0.1, 1.2, 3.6, 1.8, 1.8, 0, fWallColor);
    fWalls.add(fBackWall, fFrontWall, fLeftWall, fRightWall);
    
    buildingModel.add(fWalls);
    
    // Set initial room visibility based on active room
    updateFloorVisibility(activeRoom);
  };
  
  // Update floor visibility when active room changes
  useEffect(() => {
    updateFloorVisibility(activeRoom);
  }, [activeRoom]);
  
  // Function to update which floor is visible
  const updateFloorVisibility = (selectedRoom) => {
    if (!buildingModelRef.current) return;
    
    // Show all floors when no specific room is selected
    if (!selectedRoom) {
      buildingModelRef.current.traverse(child => {
        if (child.userData && child.userData.floor) {
          child.visible = true;
        }
      });
      return;
    }
    
    // Get floor from room (F2 -> F, G3 -> G)
    const floor = selectedRoom.charAt(0);
    
    buildingModelRef.current.traverse(child => {
      if (child.userData && child.userData.floor) {
        // Show only the floor that contains the selected room
        child.visible = child.userData.floor === floor;
      }
      
      // Highlight specific room if room models exist
      if (child.userData && child.userData.room) {
        child.visible = child.userData.room === selectedRoom;
      }
    });
  };
  
  // Model control functions
  const rotateModel = (direction) => {
    if (!buildingModelRef.current) return;
    
    const rotationAmount = direction === 'left' ? 0.2 : -0.2;
    buildingModelRef.current.rotation.y += rotationAmount;
  };
  
  const zoomModel = (direction) => {
    if (!cameraRef.current) return;
    
    const zoomFactor = direction === 'in' ? 0.9 : 1.1;
    const currentDistance = cameraRef.current.position.length();
    
    // Limit zoom range for better usability
    if ((direction === 'in' && currentDistance > 3) || (direction === 'out' && currentDistance < 15)) {
      cameraRef.current.position.multiplyScalar(zoomFactor);
      cameraRef.current.updateProjectionMatrix();
    }
  };
  
  const resetModelView = () => {
    if (!cameraRef.current || !buildingModelRef.current) return;
    
    cameraRef.current.position.set(6, 4, 6);
    cameraRef.current.lookAt(0, 0, 0);
    cameraRef.current.updateProjectionMatrix();
    
    buildingModelRef.current.rotation.x = 0;
    buildingModelRef.current.rotation.y = 0;
    buildingModelRef.current.rotation.z = 0;
  };
  
  const switchFloor = (room) => {
    setActiveRoom(room);
  };
  
  return (
    <div className="card building-view">
      <h2>Visualisasi Digital Twin</h2>
      <div className="model-container">
        <div ref={containerRef} id="building-model"></div>
        <div className="model-controls">
          <button onClick={() => rotateModel('left')}>
            <img src="/img/icons/rotate-left.svg" alt="Rotate Left" />
          </button>
          <button onClick={() => zoomModel('in')}>
            <img src="/img/icons/zoom-in.svg" alt="Zoom In" />
          </button>
          <button onClick={() => zoomModel('out')}>
            <img src="/img/icons/zoom-out.svg" alt="Zoom Out" />
          </button>
          <button onClick={() => rotateModel('right')}>
            <img src="/img/icons/rotate-right.svg" alt="Rotate Right" />
          </button>
          <button onClick={resetModelView}>
            <img src="/img/icons/reset.svg" alt="Reset View" />
          </button>
        </div>
        <div className="floor-selector">
          <div className="floor-group">
            <label>Lantai F</label>
            <div className="room-buttons">
              <button 
                className={`room-btn ${activeRoom === 'F2' ? 'active' : ''}`} 
                onClick={() => switchFloor('F2')}
              >
                F2
              </button>
              <button 
                className={`room-btn ${activeRoom === 'F3' ? 'active' : ''}`} 
                onClick={() => switchFloor('F3')}
              >
                F3
              </button>
              <button 
                className={`room-btn ${activeRoom === 'F4' ? 'active' : ''}`} 
                onClick={() => switchFloor('F4')}
              >
                F4
              </button>
              <button 
                className={`room-btn ${activeRoom === 'F5' ? 'active' : ''}`} 
                onClick={() => switchFloor('F5')}
              >
                F5
              </button>
              <button 
                className={`room-btn ${activeRoom === 'F6' ? 'active' : ''}`} 
                onClick={() => switchFloor('F6')}
              >
                F6
              </button>
            </div>
          </div>
          <div className="floor-group">
            <label>Lantai G</label>
            <div className="room-buttons">
              <button 
                className={`room-btn ${activeRoom === 'G2' ? 'active' : ''}`} 
                onClick={() => switchFloor('G2')}
              >
                G2
              </button>
              <button 
                className={`room-btn ${activeRoom === 'G3' ? 'active' : ''}`} 
                onClick={() => switchFloor('G3')}
              >
                G3
              </button>
              <button 
                className={`room-btn ${activeRoom === 'G4' ? 'active' : ''}`} 
                onClick={() => switchFloor('G4')}
              >
                G4
              </button>
              <button 
                className={`room-btn ${activeRoom === 'G5' ? 'active' : ''}`} 
                onClick={() => switchFloor('G5')}
              >
                G5
              </button>
              <button 
                className={`room-btn ${activeRoom === 'G6' ? 'active' : ''}`} 
                onClick={() => switchFloor('G6')}
              >
                G6
              </button>
              <button 
                className={`room-btn ${activeRoom === 'G7' ? 'active' : ''}`} 
                onClick={() => switchFloor('G7')}
              >
                G7
              </button>
              <button 
                className={`room-btn ${activeRoom === 'G8' ? 'active' : ''}`} 
                onClick={() => switchFloor('G8')}
              >
                G8
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BuildingModel;

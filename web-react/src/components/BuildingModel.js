import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';

const BuildingModel = () => {
  const containerRef = useRef(null);
  const [activeFloor, setActiveFloor] = useState('G');
  
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
    
    // Create camera
    const camera = new THREE.PerspectiveCamera(
      75, // Field of view
      containerRef.current.clientWidth / containerRef.current.clientHeight, // Aspect ratio
      0.1, // Near clipping plane
      1000 // Far clipping plane
    );
    camera.position.z = 5;
    camera.position.y = 2;
    cameraRef.current = camera;
    
    // Create renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
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
    
    // Set initial floor visibility based on active floor
    updateFloorVisibility(activeFloor);
  };
  
  // Update floor visibility when active floor changes
  useEffect(() => {
    updateFloorVisibility(activeFloor);
  }, [activeFloor]);
  
  // Function to update which floor is visible
  const updateFloorVisibility = (floor) => {
    if (!buildingModelRef.current) return;
    
    buildingModelRef.current.traverse(child => {
      if (child.userData && child.userData.floor) {
        child.visible = child.userData.floor === floor;
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
    
    const zoomAmount = direction === 'in' ? -0.5 : 0.5;
    cameraRef.current.position.z += zoomAmount;
    cameraRef.current.updateProjectionMatrix();
  };
  
  const resetModelView = () => {
    if (!cameraRef.current || !buildingModelRef.current) return;
    
    cameraRef.current.position.z = 5;
    cameraRef.current.position.y = 2;
    cameraRef.current.updateProjectionMatrix();
    
    buildingModelRef.current.rotation.x = 0;
    buildingModelRef.current.rotation.y = 0;
    buildingModelRef.current.rotation.z = 0;
  };
  
  const switchFloor = (floor) => {
    setActiveFloor(floor);
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
          <button 
            className={`floor-btn ${activeFloor === 'G' ? 'active' : ''}`} 
            onClick={() => switchFloor('G')}
          >
            Lantai G
          </button>
          <button 
            className={`floor-btn ${activeFloor === 'F' ? 'active' : ''}`} 
            onClick={() => switchFloor('F')}
          >
            Lantai F
          </button>
        </div>
      </div>
    </div>
  );
};

export default BuildingModel;

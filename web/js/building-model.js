// Building Model Visualization using Three.js
let scene, camera, renderer, controls;
let buildingModel;
let currentFloor = 'G';

// Initialize the 3D model
function initializeBuildingModel() {
    const container = document.getElementById('building-model');
    if (!container) return;

    // Create scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf0f0f0);

    // Create camera
    camera = new THREE.PerspectiveCamera(
        75, // Field of view
        container.clientWidth / container.clientHeight, // Aspect ratio
        0.1, // Near clipping plane
        1000 // Far clipping plane
    );
    camera.position.z = 5;
    camera.position.y = 2;

    // Create renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    // Add lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(1, 1, 1);
    scene.add(directionalLight);

    // Create simple building model
    createBuildingModel();

    // Add window resize handler
    window.addEventListener('resize', onWindowResize);

    // Start animation loop
    animate();
}

function createBuildingModel() {
    // Create a group for the building
    buildingModel = new THREE.Group();
    
    // Create floors
    createFloorG();
    createFloorF();
    
    // Add building to scene
    scene.add(buildingModel);
    
    // Position camera to view building
    camera.position.set(0, 2, 10);
    camera.lookAt(0, 0, 0);
}

function createFloorG() {
    const floorGroup = new THREE.Group();
    floorGroup.name = 'floor-G';
    
    // Base floor
    const floorGeometry = new THREE.BoxGeometry(8, 0.2, 6);
    const floorMaterial = new THREE.MeshStandardMaterial({ color: 0xcccccc });
    const floor = new THREE.Mesh(floorGeometry, floorMaterial);
    floor.position.y = -0.1;
    floorGroup.add(floor);
    
    // Walls
    const wallMaterial = new THREE.MeshStandardMaterial({ color: 0xe8e8e8 });
    
    // Outer walls
    const outerWallGeometry1 = new THREE.BoxGeometry(8, 1, 0.1);
    const outerWall1 = new THREE.Mesh(outerWallGeometry1, wallMaterial);
    outerWall1.position.set(0, 0.5, -3);
    floorGroup.add(outerWall1);
    
    const outerWallGeometry2 = new THREE.BoxGeometry(8, 1, 0.1);
    const outerWall2 = new THREE.Mesh(outerWallGeometry2, wallMaterial);
    outerWall2.position.set(0, 0.5, 3);
    floorGroup.add(outerWall2);
    
    const outerWallGeometry3 = new THREE.BoxGeometry(0.1, 1, 6);
    const outerWall3 = new THREE.Mesh(outerWallGeometry3, wallMaterial);
    outerWall3.position.set(-4, 0.5, 0);
    floorGroup.add(outerWall3);
    
    const outerWallGeometry4 = new THREE.BoxGeometry(0.1, 1, 6);
    const outerWall4 = new THREE.Mesh(outerWallGeometry4, wallMaterial);
    outerWall4.position.set(4, 0.5, 0);
    floorGroup.add(outerWall4);
    
    // Interior walls to create rooms
    const interiorWallGeometry1 = new THREE.BoxGeometry(3.9, 1, 0.1);
    const interiorWall1 = new THREE.Mesh(interiorWallGeometry1, wallMaterial);
    interiorWall1.position.set(0, 0.5, -1);
    floorGroup.add(interiorWall1);
    
    const interiorWallGeometry2 = new THREE.BoxGeometry(0.1, 1, 2);
    const interiorWall2 = new THREE.Mesh(interiorWallGeometry2, wallMaterial);
    interiorWall2.position.set(2, 0.5, 0);
    floorGroup.add(interiorWall2);
    
    const interiorWallGeometry3 = new THREE.BoxGeometry(0.1, 1, 2);
    const interiorWall3 = new THREE.Mesh(interiorWallGeometry3, wallMaterial);
    interiorWall3.position.set(-2, 0.5, 0);
    floorGroup.add(interiorWall3);
    
    // Add room labels - these would be better as sprites with text textures
    // but we'll use colored cubes for simplicity
    const roomColors = {
        'G2': 0x27ae60, // Green
        'G3': 0x3498db, // Blue
        'G4': 0xe74c3c, // Red
        'G5': 0xf39c12, // Orange
        'G6': 0x9b59b6, // Purple
        'G7': 0x1abc9c, // Teal
        'G8': 0xd35400  // Dark Orange
    };
    
    // Add colored markers for each room
    createRoomMarker(floorGroup, -3, 1.5, 'G2', roomColors['G2']);
    createRoomMarker(floorGroup, 0, -2, 'G3', roomColors['G3']);
    createRoomMarker(floorGroup, 3, -2, 'G4', roomColors['G4']);
    createRoomMarker(floorGroup, -3, -2, 'G5', roomColors['G5']);
    createRoomMarker(floorGroup, 0, 1.5, 'G6', roomColors['G6']);
    createRoomMarker(floorGroup, 3, 1.5, 'G7', roomColors['G7']);
    createRoomMarker(floorGroup, -1, 1.5, 'G8', roomColors['G8']);
    
    // Add a label for the floor
    const floorLabel = createTextLabel('Lantai G', 0x333333);
    floorLabel.position.set(0, 1.2, -3.5);
    floorGroup.add(floorLabel);
    
    // Add floor to building
    buildingModel.add(floorGroup);
}

function createFloorF() {
    const floorGroup = new THREE.Group();
    floorGroup.name = 'floor-F';
    
    // Base floor
    const floorGeometry = new THREE.BoxGeometry(8, 0.2, 6);
    const floorMaterial = new THREE.MeshStandardMaterial({ color: 0xcccccc });
    const floor = new THREE.Mesh(floorGeometry, floorMaterial);
    floor.position.y = 1.9; // Position above Floor G
    floorGroup.add(floor);
    
    // Walls
    const wallMaterial = new THREE.MeshStandardMaterial({ color: 0xe8e8e8 });
    
    // Outer walls
    const outerWallGeometry1 = new THREE.BoxGeometry(8, 1, 0.1);
    const outerWall1 = new THREE.Mesh(outerWallGeometry1, wallMaterial);
    outerWall1.position.set(0, 2.5, -3);
    floorGroup.add(outerWall1);
    
    const outerWallGeometry2 = new THREE.BoxGeometry(8, 1, 0.1);
    const outerWall2 = new THREE.Mesh(outerWallGeometry2, wallMaterial);
    outerWall2.position.set(0, 2.5, 3);
    floorGroup.add(outerWall2);
    
    const outerWallGeometry3 = new THREE.BoxGeometry(0.1, 1, 6);
    const outerWall3 = new THREE.Mesh(outerWallGeometry3, wallMaterial);
    outerWall3.position.set(-4, 2.5, 0);
    floorGroup.add(outerWall3);
    
    const outerWallGeometry4 = new THREE.BoxGeometry(0.1, 1, 6);
    const outerWall4 = new THREE.Mesh(outerWallGeometry4, wallMaterial);
    outerWall4.position.set(4, 2.5, 0);
    floorGroup.add(outerWall4);
    
    // Interior walls
    const interiorWallGeometry1 = new THREE.BoxGeometry(8, 1, 0.1);
    const interiorWall1 = new THREE.Mesh(interiorWallGeometry1, wallMaterial);
    interiorWall1.position.set(0, 2.5, 0);
    floorGroup.add(interiorWall1);
    
    const interiorWallGeometry2 = new THREE.BoxGeometry(0.1, 1, 3);
    const interiorWall2 = new THREE.Mesh(interiorWallGeometry2, wallMaterial);
    interiorWall2.position.set(2, 2.5, -1.5);
    floorGroup.add(interiorWall2);
    
    const interiorWallGeometry3 = new THREE.BoxGeometry(0.1, 1, 3);
    const interiorWall3 = new THREE.Mesh(interiorWallGeometry3, wallMaterial);
    interiorWall3.position.set(-2, 2.5, -1.5);
    floorGroup.add(interiorWall3);
    
    // Room markers for Floor F
    const roomColors = {
        'F2': 0x27ae60, // Green
        'F3': 0x3498db, // Blue
        'F4': 0xe74c3c, // Red
        'F5': 0xf39c12, // Orange
        'F6': 0x9b59b6  // Purple
    };
    
    // Add colored markers for each room
    createRoomMarker(floorGroup, -3, 1.5, 'F2', roomColors['F2'], 2);
    createRoomMarker(floorGroup, 0, 1.5, 'F3', roomColors['F3'], 2);
    createRoomMarker(floorGroup, 3, 1.5, 'F4', roomColors['F4'], 2);
    createRoomMarker(floorGroup, -3, -1.5, 'F5', roomColors['F5'], 2);
    createRoomMarker(floorGroup, 3, -1.5, 'F6', roomColors['F6'], 2);
    
    // Add a label for the floor
    const floorLabel = createTextLabel('Lantai F', 0x333333);
    floorLabel.position.set(0, 3.2, -3.5);
    floorGroup.add(floorLabel);
    
    // Initially hide floor F
    floorGroup.visible = false;
    
    // Add floor to building
    buildingModel.add(floorGroup);
}

function createRoomMarker(floorGroup, x, z, roomId, color, yOffset = 0) {
    const markerGeometry = new THREE.BoxGeometry(0.5, 0.5, 0.5);
    const markerMaterial = new THREE.MeshStandardMaterial({ color: color });
    const marker = new THREE.Mesh(markerGeometry, markerMaterial);
    marker.position.set(x, 0.5 + yOffset, z);
    marker.userData = { roomId: roomId };
    floorGroup.add(marker);
    
    // Add room label
    const roomLabel = createTextLabel(roomId, 0xffffff);
    roomLabel.position.set(0, 0, 0);
    marker.add(roomLabel);
}

function createTextLabel(text, color) {
    // This is a placeholder function
    // In a real implementation, we'd create a sprite with text texture
    // But for simplicity, we'll just create a small colored cube
    const labelGeometry = new THREE.BoxGeometry(0.3, 0.3, 0.3);
    const labelMaterial = new THREE.MeshBasicMaterial({ color: color });
    return new THREE.Mesh(labelGeometry, labelMaterial);
}

function switchFloor(floor) {
    // Hide all floors
    buildingModel.getObjectByName('floor-G').visible = false;
    buildingModel.getObjectByName('floor-F').visible = false;
    
    // Show selected floor
    buildingModel.getObjectByName(`floor-${floor}`).visible = true;
    
    // Update current floor
    currentFloor = floor;
    
    // Update camera position for better view
    if (floor === 'G') {
        camera.position.y = 2;
    } else {
        camera.position.y = 4;
    }
}

function onWindowResize() {
    const container = document.getElementById('building-model');
    if (!container) return;
    
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
}

function animate() {
    requestAnimationFrame(animate);
    
    // Slowly rotate the building for demonstration
    if (buildingModel) {
        buildingModel.rotation.y += 0.002;
    }
    
    renderer.render(scene, camera);
}

// Model control functions
function rotateModel(direction) {
    if (direction === 'left') {
        buildingModel.rotation.y += 0.3;
    } else {
        buildingModel.rotation.y -= 0.3;
    }
}

function zoomModel(direction) {
    if (direction === 'in') {
        camera.position.z -= 0.5;
    } else {
        camera.position.z += 0.5;
    }
    
    // Prevent zooming too close or too far
    if (camera.position.z < 3) camera.position.z = 3;
    if (camera.position.z > 15) camera.position.z = 15;
}

function resetModelView() {
    camera.position.set(0, currentFloor === 'G' ? 2 : 4, 10);
    camera.lookAt(0, 0, 0);
    buildingModel.rotation.y = 0;
}

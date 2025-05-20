// Main application script for Digital Twin Dashboard
document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    initializeCurrentTime();
    initializeCharts();
    initializeEventListeners();
    initializeBuildingModel();
    fetchInitialData();
});

// IMPORTANT: Replace 'YOUR_API_KEY_HERE' with your actual valid API key
const API_KEY = 'c5023020a5203c9eb451e2459df2047b9d261a30af1abcd54bd546f3ddb3248d'; 

// Update current time
function initializeCurrentTime() {
    const updateTime = () => {
        const now = new Date();
        const options = { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric',
            hour: '2-digit', 
            minute: '2-digit',
            second: '2-digit'
        };
        document.getElementById('current-time').textContent = now.toLocaleDateString('id-ID', options);
    };
    
    updateTime();
    setInterval(updateTime, 1000);
}

// Set up event listeners
function initializeEventListeners() {
    // Floor selector buttons
    document.querySelectorAll('.floor-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.floor-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            const floor = this.getAttribute('data-floor');
            switchFloor(floor);
        });
    });
    
    // Period buttons for trend analysis
    document.querySelectorAll('.period-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.period-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            const period = this.getAttribute('data-period');
            updateTrendChart(period);
        });
    });
    
    // Tab buttons for schedules/scenarios
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            
            // Update active tab button
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // Show selected tab content
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.getElementById(`${tabName}-tab`).classList.add('active');
        });
    });
    
    // Room selector
    document.getElementById('room-selector').addEventListener('change', function() {
        const roomId = this.value;
        if (roomId) {
            loadRoomDetails(roomId);
        } else {
            document.getElementById('room-details').innerHTML = '<div class="placeholder-message">Pilih ruangan untuk melihat detail</div>';
        }
    });
    
    // Alert filter
    document.getElementById('alert-filter').addEventListener('change', function() {
        filterAlerts(this.value);
    });
    
    // Model control buttons
    document.getElementById('rotate-left').addEventListener('click', () => rotateModel('left'));
    document.getElementById('rotate-right').addEventListener('click', () => rotateModel('right'));
    document.getElementById('zoom-in').addEventListener('click', () => zoomModel('in'));
    document.getElementById('zoom-out').addEventListener('click', () => zoomModel('out'));
    document.getElementById('reset-view').addEventListener('click', resetModelView);
    
    // Prediction controls
    document.getElementById('prediction-model').addEventListener('change', updatePredictions);
    document.getElementById('prediction-timeframe').addEventListener('change', updatePredictions);
    
    // Trend parameter selectors
    document.getElementById('trend-location').addEventListener('change', updateTrendChart);
    document.getElementById('trend-parameter').addEventListener('change', updateTrendChart);
}

// Fetch initial data from API
function fetchInitialData() {
    // Fetch and update system health status initially
    fetchAndUpdateSystemHealth();

    // Set an interval to update health status periodically (e.g., every 30 seconds)
    setInterval(fetchAndUpdateSystemHealth, 30000);

    // Simulate fetching other environmental data (temperature, humidity, external weather)
    // This part can be replaced with actual API calls for those metrics if available
    setTimeout(() => {
        updateEnvironmentalStatus({ 
            temperature: {
                avg: 22.5,
                min: 19.2,
                max: 24.8
            },
            humidity: {
                avg: 48,
                min: 42,
                max: 53
            },
            external: {
                weather: "Cerah Berawan",
                temperature: 29.8
            }
            // System health data is now fetched separately
        });
        
        // showNotification('Sistem Digital Twin siap digunakan (data awal dimuat)', 'normal');
        // Consider moving this notification to after the first successful health check or other critical data load
    }, 1000);
}

async function fetchAndUpdateSystemHealth() {
    const systemHealthElement = document.getElementById('system-health');
    const activeDevicesElement = document.getElementById('active-devices');

    try {
        const response = await axios.get('/system/health/', {
            headers: {
                'X-API-Key': API_KEY
            }
        });
        const healthData = response.data;

        systemHealthElement.textContent = healthData.status;
        activeDevicesElement.textContent = `${healthData.active_devices}/${healthData.total_devices}`;

        // Update class for styling based on status
        systemHealthElement.className = 'status-value health-status'; // Reset to base classes
        if (healthData.status) {
            systemHealthElement.classList.add(healthData.status.toLowerCase()); // e.g., 'optimal', 'critical'
        }
        
        if (healthData.influxdb_connection === 'disconnected') {
            systemHealthElement.classList.add('db-disconnected');
            // Optionally, append to text or change it to indicate DB issue more clearly
            // systemHealthElement.textContent += ' (DB Error)'; 
        }
        
        console.log('System health updated:', healthData);
        // showNotification('Status kesehatan sistem diperbarui.', 'normal'); // Optional: notification for successful update

    } catch (error) {
        console.error('Error fetching system health:', error);
        systemHealthElement.textContent = 'Error';
        systemHealthElement.className = 'status-value health-status error'; // Add error class
        activeDevicesElement.textContent = 'N/A';
        
        // Check if showNotification function exists before calling it
        if (typeof showNotification === 'function') {
            showNotification('Gagal memuat status kesehatan sistem.', 'critical');
        } else {
            console.warn('showNotification function not found. Cannot display error notification.');
        }
    }
}

// Update environmental status display
function updateEnvironmentalStatus(data) {
    // This function now primarily handles non-system-health environmental data
    if (data.temperature) {
        document.getElementById('avg-temperature').textContent = `${data.temperature.avg}°C`;
        document.getElementById('min-temperature').textContent = `${data.temperature.min}°C`;
        document.getElementById('max-temperature').textContent = `${data.temperature.max}°C`;
    }
    
    if (data.humidity) {
        document.getElementById('avg-humidity').textContent = `${data.humidity.avg}%`;
        document.getElementById('min-humidity').textContent = `${data.humidity.min}%`;
        document.getElementById('max-humidity').textContent = `${data.humidity.max}%`;
    }
    
    if (data.external) {
        document.getElementById('weather-status').textContent = data.external.weather;
        document.getElementById('external-temperature').textContent = `Suhu Luar: ${data.external.temperature}°C`;
    }
    // System health part is now handled by fetchAndUpdateSystemHealth
}

// Switch floor in building model
function switchFloor(floor) {
    console.log(`Switching to floor ${floor}`);
    // This would trigger a change in the 3D model
    // Placeholder for actual implementation
}

// Filter alerts by severity
function filterAlerts(severity) {
    const alerts = document.querySelectorAll('.alert-item');
    
    if (severity === 'all') {
        alerts.forEach(alert => {
            alert.style.display = 'flex';
        });
    } else {
        alerts.forEach(alert => {
            if (alert.classList.contains(severity)) {
                alert.style.display = 'flex';
            } else {
                alert.style.display = 'none';
            }
        });
    }
}

// Load room details
function loadRoomDetails(roomId) {
    // This would normally be an API call to get room-specific data
    console.log(`Loading details for room ${roomId}`);
    
    // Simulate API delay
    document.getElementById('room-details').innerHTML = '<div class="placeholder-message">Mengambil data...</div>';
    
    setTimeout(() => {
        // Sample room details HTML
        const roomDetailsHTML = `
            <div class="room-detail-container">
                <div class="room-header">
                    <h3>Ruangan ${roomId}</h3>
                    <div class="room-status normal">Status: Normal</div>
                </div>
                <div class="room-metrics">
                    <div class="metric">
                        <div class="metric-name">Suhu Saat Ini</div>
                        <div class="metric-value">21.5°C</div>
                    </div>
                    <div class="metric">
                        <div class="metric-name">Kelembapan Saat Ini</div>
                        <div class="metric-value">47%</div>
                    </div>
                    <div class="metric">
                        <div class="metric-name">Status Perangkat</div>
                        <div class="metric-value">Online</div>
                    </div>
                </div>
                <div class="room-chart">
                    <canvas id="room-temperature-chart"></canvas>
                </div>
            </div>
        `;
        
        document.getElementById('room-details').innerHTML = roomDetailsHTML;
        
        // Initialize room-specific chart
        const ctx = document.getElementById('room-temperature-chart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['10:00', '11:00', '12:00', '13:00', '14:00', '15:00'],
                datasets: [{
                    label: 'Suhu (°C)',
                    data: [20.5, 21.0, 21.2, 21.5, 21.3, 21.5],
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    tension: 0.3,
                    fill: true
                }, {
                    label: 'Kelembapan (%)',
                    data: [46, 45, 46, 48, 47, 47],
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    tension: 0.3,
                    fill: true,
                    yAxisID: 'humidity'
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: false,
                        min: 18,
                        max: 25,
                        title: {
                            display: true,
                            text: 'Suhu (°C)'
                        }
                    },
                    humidity: {
                        position: 'right',
                        beginAtZero: false,
                        min: 40,
                        max: 60,
                        title: {
                            display: true,
                            text: 'Kelembapan (%)'
                        },
                        grid: {
                            drawOnChartArea: false
                        }
                    }
                },
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }, 800);
}

// Update trend chart based on selected parameters
function updateTrendChart(period) {
    const locationSelector = document.getElementById('trend-location');
    const parameterSelector = document.getElementById('trend-parameter');
    
    const location = locationSelector.value;
    const parameter = parameterSelector.value;
    period = period || document.querySelector('.period-btn.active').getAttribute('data-period');
    
    console.log(`Updating trend chart for ${location}, parameter ${parameter}, period ${period}`);
    
    // This would normally fetch data from an API
    // For now we'll just update the chart with random values
    
    const trendCtx = document.getElementById('trend-chart').getContext('2d');
    if (window.trendChart) {
        window.trendChart.destroy();
    }
    
    let labels, data;
    
    // Generate time labels based on selected period
    if (period === '24h') {
        labels = Array.from({length: 24}, (_, i) => `${i}:00`);
    } else if (period === '7d') {
        labels = ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min'];
    } else {
        labels = Array.from({length: 30}, (_, i) => `${i+1}`);
    }
    
    // Generate random data
    data = Array.from({length: labels.length}, () => Math.random() * 10 + (parameter === 'temperature' ? 20 : 45));
    
    // Create chart
    window.trendChart = new Chart(trendCtx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: parameter === 'temperature' ? 'Suhu (°C)' : 'Kelembapan (%)',
                data: data,
                borderColor: parameter === 'temperature' ? '#e74c3c' : '#3498db',
                backgroundColor: parameter === 'temperature' ? 'rgba(231, 76, 60, 0.1)' : 'rgba(52, 152, 219, 0.1)',
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: false,
                    min: parameter === 'temperature' ? 18 : 40,
                    max: parameter === 'temperature' ? 30 : 70,
                    title: {
                        display: true,
                        text: parameter === 'temperature' ? 'Suhu (°C)' : 'Kelembapan (%)'
                    }
                }
            },
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

// Update predictions based on selected model and timeframe
function updatePredictions() {
    const model = document.getElementById('prediction-model').value;
    const timeframe = document.getElementById('prediction-timeframe').value;
    
    console.log(`Updating predictions for model: ${model}, timeframe: ${timeframe}`);
    // Placeholder for actual prediction update logic
    // This would involve fetching data from the backend based on selected parameters
    // and then updating the prediction charts (temperature-prediction-chart, humidity-prediction-chart)
    // and the proactive recommendations list.
    
    // Example: Update recommendation list (simulated)
    const recommendationsList = document.querySelector('.recommendations-list');
    recommendationsList.innerHTML = `
        <div class="recommendation-item">
            <div class="recommendation-time">Prediksi untuk ${timeframe}</div>
            <div class="recommendation-content">
                <div class="recommendation-title">Rekomendasi berdasarkan model ${model}</div>
                <div class="recommendation-description">
                    Data prediksi sedang diproses... (Ini adalah placeholder)
                </div>
            </div>
        </div>
    `;
    
    // You would also update the prediction charts here using their respective Chart.js instances
    // e.g., temperaturePredictionChart.data.datasets[0].data = newTempPredictionData;
    // temperaturePredictionChart.update();
}

// Show notification message
// Ensure this function is defined, or remove calls to it if not used.
// Example basic implementation if not already present:
function showNotification(message, type) {
    console.log(`Notification (${type}): ${message}`);
    // A more sophisticated implementation would create a visible notification element on the page.
    // For example, creating a div, styling it, and appending it to the body, then removing it after a few seconds.
    // This is a placeholder if the function wasn't fully provided in the initial context.
    const notificationArea = document.getElementById('notifications') || document.body; // Or a dedicated notification area
    const notificationDiv = document.createElement('div');
    notificationDiv.className = `notification ${type}`; // e.g., 'notification critical', 'notification normal'
    notificationDiv.textContent = message;
    
    // Basic styling (can be moved to CSS)
    notificationDiv.style.position = 'fixed';
    notificationDiv.style.top = '20px';
    notificationDiv.style.right = '20px';
    notificationDiv.style.padding = '10px 20px';
    notificationDiv.style.backgroundColor = type === 'critical' ? 'red' : (type === 'warning' ? 'orange' : 'green');
    notificationDiv.style.color = 'white';
    notificationDiv.style.borderRadius = '5px';
    notificationDiv.style.zIndex = '1000';
    
    notificationArea.appendChild(notificationDiv);
    
    setTimeout(() => {
        notificationDiv.remove();
    }, 5000); // Remove after 5 seconds
}

// These functions would be implemented in building-model.js
function rotateModel(direction) {
    console.log(`Rotating model ${direction}`);
}

function zoomModel(direction) {
    console.log(`Zooming model ${direction}`);
}

function resetModelView() {
    console.log('Resetting model view');
}

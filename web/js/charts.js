// Chart configurations and initializations

// Make this a global function that app.js can call
window.initializeCharts = function() {
    // This file contains specific chart configurations
    // Most chart instantiations are already in app.js
    
    // Set global Chart.js defaults
    Chart.defaults.font.family = "'Roboto', sans-serif";
    Chart.defaults.color = '#7f8c8d';
    Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(52, 73, 94, 0.8)';
    Chart.defaults.plugins.tooltip.titleFont = {
        size: 14,
        weight: 'bold'
    };
    Chart.defaults.plugins.tooltip.bodyFont = {
        size: 13
    };
    Chart.defaults.plugins.tooltip.padding = 12;
    Chart.defaults.plugins.tooltip.cornerRadius = 6;
    Chart.defaults.plugins.tooltip.displayColors = true;
    Chart.defaults.plugins.tooltip.boxWidth = 10;
    Chart.defaults.plugins.tooltip.boxHeight = 10;
    Chart.defaults.plugins.tooltip.boxPadding = 4;
    
    // Create any additional charts not covered in app.js
    // These functions are defined below in this file.
    // If they are intended to create charts immediately, they can be called here.
    // For now, let's assume they are called as needed by other parts of the application
    // or that their primary purpose was to be available, which they now are globally.
    // createSensorDataDistributionChart(); 
    // createSystemHealthChart();
}; // Ensure this is explicitly assigned to window

// Additional chart for sensor data distribution
function createSensorDataDistributionChart() {
    // This chart would be created on demand when user explores analytics section
    // For now, just define the structure

    // Example data structure for sensor distribution chart
    const sensorDistributionData = {
        labels: ['F2', 'F3', 'F4', 'F5', 'F6', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8'],
        datasets: [
            {
                label: 'Rata-rata Suhu (°C)',
                data: [21.2, 22.5, 22.0, 21.8, 20.5, 21.9, 22.3, 20.8, 21.7, 22.1, 23.5, 20.9],
                backgroundColor: 'rgba(231, 76, 60, 0.7)',
                borderColor: 'rgba(192, 57, 43, 1)',
                borderWidth: 1
            },
            {
                label: 'Rata-rata Kelembapan (%)',
                data: [48, 45, 49, 50, 52, 47, 46, 51, 49, 48, 46, 52],
                backgroundColor: 'rgba(52, 152, 219, 0.7)',
                borderColor: 'rgba(41, 128, 185, 1)',
                borderWidth: 1
            }
        ]
    };
}

// Additional chart for system health monitoring
function createSystemHealthChart() {
    // This chart would show system performance metrics
    // For example: sensor uptime, data quality, etc.
    
    // Example data for system health
    const systemHealthData = {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [
            {
                label: 'Kualitas Data (%)',
                data: [92, 94, 98, 96, 95, 97],
                backgroundColor: 'rgba(46, 204, 113, 0.2)',
                borderColor: 'rgba(39, 174, 96, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(39, 174, 96, 1)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 4,
                fill: true,
                tension: 0.3
            },
            {
                label: 'Uptime Sensor (%)',
                data: [100, 99, 99.5, 98, 99.8, 99.9],
                backgroundColor: 'rgba(52, 152, 219, 0.2)',
                borderColor: 'rgba(52, 152, 219, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(52, 152, 219, 1)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 4,
                fill: true,
                tension: 0.3
            }
        ]
    };
}

// Function to create heat map visualization
function createTemperatureHeatMap(data) {
    // This would create a heatmap visualization of temperature across the building
    // Typically implemented with a specialized library like heatmap.js or D3.js
    // Here we just define the structure
    
    // Example implementation would look like:
    /*
    const heatmapInstance = h337.create({
        container: document.querySelector('.heatmap-container'),
        radius: 30,
        maxOpacity: 0.8,
        minOpacity: 0.1,
        blur: 0.75,
        gradient: {
            '.5': 'blue',
            '.8': 'green',
            '.95': 'yellow',
            '1.0': 'red'
        }
    });
    
    heatmapInstance.setData({
        max: 30,
        min: 18,
        data: data // Array of {x, y, value} points
    });
    */
}

// Function to create correlaton matrix
function createCorrelationMatrix() {
    // Would create a correlation matrix chart to show relationships
    // between different environmental variables
    
    // Example implementation would visualize correlations between:
    // - Internal temperature vs external temperature
    // - Humidity vs rainfall
    // - Temperature vs time of day
    // - etc.
}

// Function to create energy efficiency chart
function createEnergyEfficiencyChart() {
    // Would visualize energy usage in relation to environmental conditions
    
    // Example data structure:
    const energyData = {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [
            {
                label: 'Konsumsi Energi (kWh)',
                data: [1200, 1150, 980, 850, 920, 1050],
                backgroundColor: 'rgba(241, 196, 15, 0.2)',
                borderColor: 'rgba(241, 196, 15, 1)',
                borderWidth: 2,
                yAxisID: 'energy'
            },
            {
                label: 'Suhu Eksternal Rata-rata (°C)',
                data: [24, 25, 27, 28, 30, 31],
                backgroundColor: 'rgba(231, 76, 60, 0.0)',
                borderColor: 'rgba(231, 76, 60, 1)',
                borderWidth: 2,
                type: 'line',
                yAxisID: 'temperature'
            }
        ]
    };
}

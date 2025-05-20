#!/usr/bin/env python3
"""
Simple HTTP server for Digital Twin Web Interface
"""
import os
import json
import argparse
import socket
from http.server import HTTPServer, SimpleHTTPRequestHandler
from functools import partial
import threading
import time
from urllib.parse import parse_qs, urlparse
from influxdb_client import InfluxDBClient
from influxdb_client.client.exceptions import InfluxDBError
from datetime import datetime, timedelta
import pandas as pd

# Configuration
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "th1s_1s_a_v3ry_s3cur3_4nd_l0ng_4dm1n_t0k3n_f0r_d3v")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "iot_project_alpha")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "sensor_data_primary")

# Initialize InfluxDB client
try:
    influx_client = InfluxDBClient(
        url=INFLUXDB_URL,
        token=INFLUXDB_TOKEN,
        org=INFLUXDB_ORG
    )
    query_api = influx_client.query_api()
    print(f"Connected to InfluxDB at {INFLUXDB_URL}")
except Exception as e:
    print(f"Error connecting to InfluxDB: {e}")
    influx_client = None
    query_api = None

class DigitalTwinHTTPRequestHandler(SimpleHTTPRequestHandler):
    """Custom request handler for Digital Twin web application"""
    
    def __init__(self, base_path, *args, **kwargs):
        self.base_path = base_path
        super().__init__(*args, **kwargs)

    def translate_path(self, path):
        """Translate URL path to filesystem path"""
        path = super().translate_path(path)
        rel_path = os.path.relpath(path, os.getcwd())
        return os.path.join(self.base_path, rel_path)
    
    def do_GET(self):
        """Handle GET requests"""
        # API endpoints
        if self.path.startswith('/api/'):
            self.handle_api_request()
        else:
            return super().do_GET()
    
    def handle_api_request(self):
        """Handle API requests"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        
        # Check if the path is for sensor data
        if path == '/api/current-data':
            self.handle_current_data_request(query_params)
        elif path == '/api/trend-data':
            self.handle_trend_data_request(query_params)
        elif path == '/api/room-data':
            self.handle_room_data_request(query_params)
        elif path == '/api/prediction-data':
            self.handle_prediction_data_request(query_params)
        elif path == '/api/recommendations':
            self.handle_recommendations_request(query_params)
        else:
            self.send_error(404, "API endpoint not found")
    
    def handle_current_data_request(self, query_params):
        """Handle request for current sensor data"""
        try:
            # This is a demo implementation that returns sample data
            # In a real implementation, you would query InfluxDB
            sample_data = {
                "timestamp": datetime.now().isoformat(),
                "temperature": {
                    "avg": 22.5,
                    "min": 19.2,
                    "max": 24.8
                },
                "humidity": {
                    "avg": 48,
                    "min": 42,
                    "max": 53
                },
                "external": {
                    "weather": "Cerah Berawan",
                    "temperature": 29.8,
                    "humidity": 65
                },
                "system": {
                    "status": "Optimal",
                    "activeDevices": 12,
                    "totalDevices": 12
                },
                "alerts": [
                    {
                        "id": "alert-001",
                        "severity": "critical",
                        "title": "Kelembapan Terlalu Tinggi - G7",
                        "description": "Kelembapan mencapai 68%. Direkomendasikan untuk mengaktifkan dehumidifier segera.",
                        "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat()
                    },
                    {
                        "id": "alert-002",
                        "severity": "warning",
                        "title": "Suhu di Atas Optimal - F4",
                        "description": "Suhu naik menjadi 23.8°C. Direkomendasikan untuk menyesuaikan pengaturan AC.",
                        "timestamp": (datetime.now() - timedelta(minutes=28)).isoformat()
                    },
                    {
                        "id": "alert-003",
                        "severity": "normal",
                        "title": "Prediksi Cuaca - 3 Jam Mendatang",
                        "description": "Prakiraan hujan dalam 3 jam ke depan. Kemungkinan peningkatan kelembapan di ruang G2-G5.",
                        "timestamp": (datetime.now() - timedelta(minutes=45)).isoformat()
                    }
                ]
            }
            
            self.send_json_response(200, sample_data)
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})
    
    def handle_trend_data_request(self, query_params):
        """Handle request for trend data"""
        try:
            period = query_params.get('period', ['24h'])[0]
            location = query_params.get('location', ['all'])[0]
            parameter = query_params.get('parameter', ['temperature'])[0]
            
            # Generate sample data based on parameters
            if period == '24h':
                timestamps = [
                    (datetime.now() - timedelta(hours=i)).strftime('%H:%M')
                    for i in range(24, 0, -1)
                ]
            elif period == '7d':
                timestamps = [
                    (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                    for i in range(7, 0, -1)
                ]
            else:  # 30d
                timestamps = [
                    (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                    for i in range(30, 0, -1)
                ]
            
            # Generate sample values
            base_value = 22.5 if parameter == 'temperature' else 48
            values = []
            
            for i in range(len(timestamps)):
                if parameter == 'temperature':
                    # Simulate daily temperature patterns
                    hour = datetime.now().hour - i % 24
                    daily_factor = 2 * math.sin(hour * math.pi / 12 - math.pi/2) + 1
                    values.append(round(base_value + daily_factor + 2 * (random.random() - 0.5), 1))
                else:
                    values.append(round(base_value + 10 * (random.random() - 0.5), 1))
            
            response_data = {
                "timestamps": timestamps,
                "values": values,
                "parameter": parameter,
                "location": location,
                "period": period
            }
            
            self.send_json_response(200, response_data)
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})
    
    def handle_room_data_request(self, query_params):
        """Handle request for room-specific data"""
        try:
            room_id = query_params.get('id', [''])[0]
            
            if not room_id:
                self.send_json_response(400, {"error": "Room ID is required"})
                return
            
            # Generate sample data for the room
            response_data = {
                "id": room_id,
                "name": f"Ruangan {room_id}",
                "current": {
                    "temperature": round(21.5 + 2 * (random.random() - 0.5), 1),
                    "humidity": round(48 + 5 * (random.random() - 0.5)),
                    "status": "normal"
                },
                "history": {
                    "timestamps": [
                        (datetime.now() - timedelta(hours=i)).strftime('%H:%M')
                        for i in range(6, 0, -1)
                    ],
                    "temperature": [
                        round(21.5 + 2 * (random.random() - 0.5), 1)
                        for _ in range(6)
                    ],
                    "humidity": [
                        round(48 + 5 * (random.random() - 0.5))
                        for _ in range(6)
                    ]
                }
            }
            
            self.send_json_response(200, response_data)
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})
    
    def handle_prediction_data_request(self, query_params):
        """Handle request for prediction data"""
        try:
            model = query_params.get('model', ['default'])[0]
            timeframe = query_params.get('timeframe', ['24h'])[0]
            
            # Generate timestamps based on timeframe
            if timeframe == '6h':
                timestamps = ['Now'] + [
                    f"+{i}h" for i in range(1, 7)
                ]
                num_points = 7
            elif timeframe == '24h':
                timestamps = ['Now'] + [
                    f"+{i}h" for i in range(3, 25, 3)
                ]
                num_points = 9
            else:  # 7d
                timestamps = ['Today'] + [
                    f"Day {i+1}" for i in range(7)
                ]
                num_points = 8
            
            # Generate sample temperature prediction
            base_temp = 22.5
            temp_actual = [base_temp]
            temp_predicted = [base_temp]
            
            for i in range(1, num_points):
                if model == 'optimized':
                    variation = 1.5  # Less variation in optimized model
                else:
                    variation = 3.0  # More variation in default model
                
                # The first point is actual, rest are predicted
                if i == 1:
                    temp_actual.append(round(base_temp + variation * (random.random() - 0.5), 1))
                    temp_predicted.append(None)  # No prediction for actual data point
                else:
                    temp_actual.append(None)  # No actual data for future points
                    temp_predicted.append(round(base_temp + variation * (random.random() - 0.5), 1))
            
            # Generate sample humidity prediction
            base_humidity = 48
            humidity_actual = [base_humidity]
            humidity_predicted = [base_humidity]
            
            for i in range(1, num_points):
                if model == 'optimized':
                    variation = 3  # Less variation in optimized model
                else:
                    variation = 8  # More variation in default model
                
                # The first point is actual, rest are predicted
                if i == 1:
                    humidity_actual.append(round(base_humidity + variation * (random.random() - 0.5)))
                    humidity_predicted.append(None)  # No prediction for actual data point
                else:
                    humidity_actual.append(None)  # No actual data for future points
                    humidity_predicted.append(round(base_humidity + variation * (random.random() - 0.5)))
            
            response_data = {
                "model": model,
                "timeframe": timeframe,
                "timestamps": timestamps,
                "temperature": {
                    "actual": temp_actual,
                    "predicted": temp_predicted
                },
                "humidity": {
                    "actual": humidity_actual,
                    "predicted": humidity_predicted
                }
            }
            
            self.send_json_response(200, response_data)
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})
    
    def handle_recommendations_request(self, query_params):
        """Handle request for recommendations"""
        try:
            # Sample recommendations
            recommendations = [
                {
                    "id": "rec-001",
                    "timeframe": "16:00 - 20:00",
                    "title": "Antisipasi Kenaikan Kelembapan",
                    "description": "Prakiraan hujan akan meningkatkan kelembapan di area G7. Aktifkan dehumidifier mulai pukul 16:00.",
                    "severity": "medium",
                    "parameter": "humidity"
                },
                {
                    "id": "rec-002",
                    "timeframe": "Besok, 06:00 - 10:00",
                    "title": "Antisipasi Peningkatan Suhu",
                    "description": "Prakiraan cerah berawan dengan suhu eksternal mencapai 31°C. Persiapkan sistem pendingin di area F5-F6.",
                    "severity": "medium",
                    "parameter": "temperature"
                },
                {
                    "id": "rec-003",
                    "timeframe": "Maintenance",
                    "title": "Jadwal Perawatan Optimal",
                    "description": "Waktu optimal untuk perawatan AC adalah hari Rabu, 21 Mei 2025 pukul 10:00-14:00 saat beban sistem minimal.",
                    "severity": "low",
                    "parameter": "maintenance"
                }
            ]
            
            self.send_json_response(200, {"recommendations": recommendations})
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})
    
    def send_json_response(self, status_code, data):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
        self.wfile.write(json.dumps(data).encode('utf-8'))

def start_server(port=8002, directory=None):
    """Start the web server"""
    if directory is None:
        directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web')
    
    if not os.path.exists(directory):
        print(f"Error: Directory {directory} does not exist")
        return
    
    # Get server address
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    # Create server
    handler = partial(DigitalTwinHTTPRequestHandler, directory)
    server = HTTPServer(('0.0.0.0', port), handler)
    
    print(f"Starting Digital Twin Web Server on port {port}")
    print(f"Open http://localhost:{port} or http://{local_ip}:{port} in your browser")
    print("Press Ctrl+C to stop the server")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server")
        server.shutdown()

if __name__ == "__main__":
    # Add math and random for the sample data generation
    import math
    import random
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Digital Twin Web Interface Server')
    parser.add_argument('-p', '--port', type=int, default=8003, help='Port to run the server on')
    parser.add_argument('-d', '--directory', type=str, help='Directory to serve files from')
    
    args = parser.parse_args()
    
    start_server(port=args.port, directory=args.directory)

#!/usr/bin/env python3
"""
Script untuk memverifikasi implementasi ClimateDigitalTwin
"""

import requests
import time
import json
from datetime import datetime

def check_react_app():
    """Periksa apakah React app dapat diakses"""
    try:
        response = requests.get('http://localhost:3000', timeout=10)
        print(f"✅ React App Status: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ React App Error: {e}")
        return False

def check_component_files():
    """Periksa apakah file komponen ClimateDigitalTwin ada"""
    import os
    
    files_to_check = [
        '/home/lambda_one/project/digitalTwin/web-react/src/components/ClimateDigitalTwin.js',
        '/home/lambda_one/project/digitalTwin/web-react/src/components/ClimateDigitalTwin.css',
        '/home/lambda_one/project/digitalTwin/web-react/src/components/Dashboard.js'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ File exists: {file_path}")
        else:
            print(f"❌ File missing: {file_path}")

def check_container_status():
    """Periksa status container"""
    import subprocess
    
    try:
        result = subprocess.run(['docker', 'ps', '--filter', 'name=web_react_service'], 
                              capture_output=True, text=True)
        if 'web_react_service' in result.stdout:
            print("✅ Container web_react_service is running")
            return True
        else:
            print("❌ Container web_react_service is not running")
            return False
    except Exception as e:
        print(f"❌ Error checking container: {e}")
        return False

def main():
    print("🔍 VERIFIKASI CLIMATE DIGITAL TWIN IMPLEMENTATION")
    print("=" * 60)
    
    print("\n1. Checking component files...")
    check_component_files()
    
    print("\n2. Checking container status...")
    container_ok = check_container_status()
    
    print("\n3. Checking React app accessibility...")
    react_ok = check_react_app()
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY:")
    
    if container_ok and react_ok:
        print("✅ ClimateDigitalTwin should be implemented successfully")
        print("🌐 Access the dashboard at: http://localhost:3000")
        print("\n🎯 EXPECTED FEATURES:")
        print("   - 3D building model with room visualization")
        print("   - Color-coded climate conditions (temperature/humidity/air quality)")
        print("   - Interactive room selection with climate data")
        print("   - Heat map toggle and view mode selection")
        print("   - Real-time climate metrics for each room")
        print("   - Device status indicators (HVAC, Dehumidifier, Air Purifier)")
        print("   - Status indicators (Normal/Warning/Critical)")
    else:
        print("❌ There are issues with the implementation")
        print("🔧 TROUBLESHOOTING:")
        if not container_ok:
            print("   - Restart the container: docker-compose up -d web-react")
        if not react_ok:
            print("   - Check container logs: docker logs web_react_service")
    
    print("\n📝 CLIMATE VISUALIZATION FEATURES:")
    print("   🌡️  Temperature heat map with color coding")
    print("   💧 Humidity level visualization") 
    print("   🌬️  Air quality indicators")
    print("   🏠 Room-by-room environmental data")
    print("   📊 Real-time device status monitoring")
    print("   ⚠️  Alert system for critical conditions")

if __name__ == "__main__":
    main()

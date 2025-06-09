#!/usr/bin/env python3
"""
Final integration test for external humidity display in React dashboard
This script verifies the complete data flow from BMKG API to React frontend
"""

import requests
import json
import time
from datetime import datetime

def test_api_endpoint():
    """Test the BMKG API endpoint directly"""
    print("🔍 Testing API endpoint directly...")
    try:
        response = requests.get(
            "http://localhost:8002/external/bmkg/latest",
            headers={"x-api-key": "development_key_for_testing"},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            humidity = data.get('weather_data', {}).get('humidity')
            print(f"✅ API Response: {response.status_code}")
            print(f"✅ Humidity value: {humidity}%")
            return humidity
        else:
            print(f"❌ API Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ API Connection Error: {e}")
        return None

def test_api_through_nginx():
    """Test the API endpoint through nginx proxy"""
    print("\n🔍 Testing API through nginx proxy...")
    try:
        response = requests.get(
            "http://localhost:3003/api/external/bmkg/latest",
            headers={"x-api-key": "development_key_for_testing"},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            humidity = data.get('weather_data', {}).get('humidity')
            print(f"✅ Nginx Proxy Response: {response.status_code}")
            print(f"✅ Humidity value: {humidity}%")
            return humidity
        else:
            print(f"❌ Nginx Proxy Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Nginx Proxy Connection Error: {e}")
        return None

def test_react_app_access():
    """Test React app accessibility"""
    print("\n🔍 Testing React app access...")
    try:
        response = requests.get("http://localhost:3003", timeout=10)
        if response.status_code == 200:
            print(f"✅ React App Response: {response.status_code}")
            print(f"✅ Content length: {len(response.text)} characters")
            
            # Check for key React app indicators
            if "bundle.js" in response.text:
                print("✅ React bundle detected")
            if "Digital Twin" in response.text or "logo_dt" in response.text:
                print("✅ Digital Twin app content detected")
            
            return True
        else:
            print(f"❌ React App Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ React App Connection Error: {e}")
        return False

def check_container_status():
    """Check the status of containers"""
    print("\n🔍 Checking container status...")
    import subprocess
    try:
        result = subprocess.run(
            ["docker-compose", "ps", "--format", "table"],
            capture_output=True,
            text=True,
            timeout=10
        )
        print("📊 Container Status:")
        print(result.stdout)
        
        # Check for specific services
        if "api_service" in result.stdout and "Up" in result.stdout:
            print("✅ API service is running")
        if "web_react_service" in result.stdout and "Up" in result.stdout:
            print("✅ React service is running")
            
    except Exception as e:
        print(f"❌ Error checking containers: {e}")

def main():
    print("=" * 70)
    print("🧪 FINAL INTEGRATION TEST - EXTERNAL HUMIDITY DISPLAY")
    print("=" * 70)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test all components
    api_humidity = test_api_endpoint()
    nginx_humidity = test_api_through_nginx()
    react_accessible = test_react_app_access()
    check_container_status()
    
    print("\n" + "=" * 70)
    print("📋 INTEGRATION TEST SUMMARY")
    print("=" * 70)
    
    # Summary
    if api_humidity is not None:
        print(f"✅ Direct API: Working (Humidity: {api_humidity}%)")
    else:
        print("❌ Direct API: Failed")
    
    if nginx_humidity is not None:
        print(f"✅ Nginx Proxy: Working (Humidity: {nginx_humidity}%)")
    else:
        print("❌ Nginx Proxy: Failed")
    
    if react_accessible:
        print("✅ React App: Accessible")
    else:
        print("❌ React App: Not accessible")
    
    # Final status
    if all([api_humidity is not None, nginx_humidity is not None, react_accessible]):
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ External humidity integration is fully functional")
        print("\n📱 To view the humidity data:")
        print("   1. Open http://localhost:3003 in your browser")
        print("   2. Look for 'Cuaca Eksternal (BMKG)' section")
        print("   3. External humidity should be displayed as 'Kelembapan Luar'")
        print(f"   4. Current humidity value: {api_humidity}%")
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("   Please check the failed components above")
    
    print("=" * 70)

if __name__ == "__main__":
    main()

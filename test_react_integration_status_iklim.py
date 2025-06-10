#!/usr/bin/env python3

import requests
import time
import json

def test_react_app_api_integration():
    """Test integrasi antara React app dan API untuk Status Iklim Mikro"""
    
    print("🌡️ PENGUJIAN INTEGRASI REACT APP & API - STATUS IKLIM MIKRO")
    print("=" * 60)
    
    # Test 1: Check if React app is accessible
    print("\n🔍 Test 1: Checking React App Accessibility...")
    try:
        response = requests.get("http://localhost:3003", timeout=10)
        if response.status_code == 200:
            print("✅ React app is accessible")
            if "bundle.js" in response.text:
                print("✅ Bundle JavaScript detected")
            else:
                print("⚠️  Bundle JavaScript not found")
        else:
            print(f"❌ React app returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot access React app: {e}")
        return False
    
    # Test 2: Test API endpoints through nginx proxy
    print("\n🔍 Test 2: Testing API Endpoints through Nginx Proxy...")
    
    api_tests = [
        {
            "name": "BMKG Weather Data",
            "endpoint": "/api/external/bmkg/latest",
            "check_field": "weather_data"
        },
        {
            "name": "System Health",
            "endpoint": "/api/system/health/",
            "check_field": "status"
        },
        {
            "name": "Temperature Stats",
            "endpoint": "/api/stats/temperature/last-hour/stats/",
            "check_field": "avg_temperature"
        },
        {
            "name": "Humidity Stats", 
            "endpoint": "/api/stats/humidity/last-hour/stats/",
            "check_field": "avg_humidity"
        }
    ]
    
    all_apis_working = True
    api_results = {}
    
    for test in api_tests:
        print(f"\n   Testing {test['name']}...")
        try:
            url = f"http://localhost:3003{test['endpoint']}"
            headers = {"X-API-Key": "development_key_for_testing"}
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if test['check_field'] in data:
                    print(f"   ✅ {test['name']}: OK")
                    api_results[test['name']] = data
                else:
                    print(f"   ❌ {test['name']}: Missing field '{test['check_field']}'")
                    all_apis_working = False
            else:
                print(f"   ❌ {test['name']}: Status {response.status_code}")
                print(f"      Response: {response.text[:100]}...")
                all_apis_working = False
                
        except Exception as e:
            print(f"   ❌ {test['name']}: Error - {e}")
            all_apis_working = False
    
    # Test 3: Simulate frontend data processing  
    print("\n🔍 Test 3: Simulating Frontend Data Processing...")
    
    if all_apis_working and api_results:
        print("\n   📊 Processing data like React frontend would...")
        
        # Simulate EnvironmentalStatus.js data processing
        if "Temperature Stats" in api_results:
            temp_data = api_results["Temperature Stats"]
            print(f"   🌡️  Temperature: {temp_data.get('avg_temperature', 'N/A')}°C")
            print(f"       Range: {temp_data.get('min_temperature', 'N/A')}°C - {temp_data.get('max_temperature', 'N/A')}°C")
        
        if "Humidity Stats" in api_results:
            humidity_data = api_results["Humidity Stats"]
            print(f"   💧 Humidity: {humidity_data.get('avg_humidity', 'N/A')}%")
            print(f"       Range: {humidity_data.get('min_humidity', 'N/A')}% - {humidity_data.get('max_humidity', 'N/A')}%")
        
        if "BMKG Weather Data" in api_results:
            weather_data = api_results["BMKG Weather Data"].get('weather_data', {})
            print(f"   🌤️  External Weather: {weather_data.get('weather_condition', 'N/A')}")
            print(f"       External Temp: {weather_data.get('temperature', 'N/A')}°C")
            print(f"       External Humidity: {weather_data.get('humidity', 'N/A')}%")
        
        if "System Health" in api_results:
            health_data = api_results["System Health"]
            print(f"   🔧 System Health: {health_data.get('status', 'N/A')}")
            print(f"       Active Devices: {health_data.get('active_devices', 'N/A')}/{health_data.get('total_devices', 'N/A')}")
            print(f"       InfluxDB: {health_data.get('influxdb_connection', 'N/A')}")
        
        print("\n✅ Data processing simulation completed")
    else:
        print("❌ Cannot simulate data processing due to API errors")
    
    # Summary
    print(f"\n📊 SUMMARY")
    print("=" * 30)
    
    if all_apis_working:
        print("✅ React App Accessibility: PASS")
        print("✅ API Endpoints via Proxy: PASS") 
        print("✅ Data Processing: PASS")
        print("\n🎉 Status Iklim Mikro integration is working correctly!")
        
        print("\n💡 If you still see issues in the browser:")
        print("   1. Clear browser cache and reload")
        print("   2. Check browser console for JavaScript errors")
        print("   3. Verify React container logs for any errors")
        
        return True
    else:
        print("❌ React App Accessibility: PASS")
        print("❌ API Endpoints via Proxy: FAIL")
        print("❌ Data Processing: FAIL") 
        print("\n⚠️  There are issues with the API integration")
        return False

if __name__ == "__main__":
    test_react_app_api_integration()

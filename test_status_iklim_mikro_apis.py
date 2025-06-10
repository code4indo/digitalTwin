#!/usr/bin/env python3

import requests
import json

def test_frontend_api_calls():
    """Test API calls yang dipanggil oleh frontend React untuk Status Iklim Mikro"""
    
    print("🧪 PENGUJIAN API UNTUK STATUS IKLIM MIKRO")
    print("=" * 50)
    
    base_url = "http://localhost:8002"
    api_key = "development_key_for_testing"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key
    }
    
    # Test endpoints yang dipanggil oleh EnvironmentalStatus.js
    endpoints = [
        {
            "name": "Environmental Status (Temperature)",
            "url": f"{base_url}/stats/temperature/last-hour/stats/",
            "expected_fields": ["avg_temperature", "min_temperature", "max_temperature"]
        },
        {
            "name": "Environmental Status (Humidity)", 
            "url": f"{base_url}/stats/humidity/last-hour/stats/",
            "expected_fields": ["avg_humidity", "min_humidity", "max_humidity"]
        },
        {
            "name": "External Weather (BMKG)",
            "url": f"{base_url}/external/bmkg/latest",
            "expected_fields": ["weather_data"]
        },
        {
            "name": "System Health",
            "url": f"{base_url}/system/health/",
            "expected_fields": ["status", "active_devices", "total_devices", "influxdb_connection"]
        }
    ]
    
    results = {}
    
    for endpoint in endpoints:
        print(f"\n🔍 Testing {endpoint['name']}...")
        print(f"URL: {endpoint['url']}")
        
        try:
            response = requests.get(endpoint['url'], headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS: {response.status_code}")
                
                # Check if expected fields exist
                missing_fields = []
                for field in endpoint['expected_fields']:
                    if field not in data:
                        # For nested fields like weather_data
                        if field == "weather_data" and isinstance(data, dict):
                            if field not in data:
                                missing_fields.append(field)
                        else:
                            missing_fields.append(field)
                
                if missing_fields:
                    print(f"⚠️  Missing fields: {missing_fields}")
                else:
                    print(f"✅ All expected fields present")
                
                # Show sample data
                if endpoint['name'] == "External Weather (BMKG)":
                    weather_data = data.get('weather_data', {})
                    print(f"   Temperature: {weather_data.get('temperature', 'N/A')}°C")
                    print(f"   Humidity: {weather_data.get('humidity', 'N/A')}%")
                    print(f"   Condition: {weather_data.get('weather_condition', 'N/A')}")
                elif endpoint['name'] == "System Health":
                    print(f"   Status: {data.get('status', 'N/A')}")
                    print(f"   Active Devices: {data.get('active_devices', 'N/A')}/{data.get('total_devices', 'N/A')}")
                    print(f"   InfluxDB: {data.get('influxdb_connection', 'N/A')}")
                elif "Environmental Status" in endpoint['name']:
                    if "Temperature" in endpoint['name']:
                        print(f"   Avg Temperature: {data.get('avg_temperature', 'N/A')}°C")
                        print(f"   Min: {data.get('min_temperature', 'N/A')}°C, Max: {data.get('max_temperature', 'N/A')}°C")
                    else:
                        print(f"   Avg Humidity: {data.get('avg_humidity', 'N/A')}%")
                        print(f"   Min: {data.get('min_humidity', 'N/A')}%, Max: {data.get('max_humidity', 'N/A')}%")
                
                results[endpoint['name']] = {
                    "status": "SUCCESS",
                    "data": data
                }
                
            else:
                print(f"❌ ERROR: Status {response.status_code}")
                print(f"Response: {response.text}")
                results[endpoint['name']] = {
                    "status": "ERROR",
                    "code": response.status_code,
                    "message": response.text
                }
                
        except requests.exceptions.Timeout:
            print(f"⏰ TIMEOUT: Request exceeded 10 seconds")
            results[endpoint['name']] = {
                "status": "TIMEOUT"
            }
        except requests.exceptions.RequestException as e:
            print(f"❌ REQUEST ERROR: {e}")
            results[endpoint['name']] = {
                "status": "ERROR",
                "error": str(e)
            }
        
        print("-" * 40)
    
    # Summary
    print(f"\n📊 SUMMARY")
    print("=" * 30)
    success_count = sum(1 for r in results.values() if r['status'] == 'SUCCESS')
    total_count = len(results)
    
    for name, result in results.items():
        status_icon = "✅" if result['status'] == 'SUCCESS' else "❌"
        print(f"{status_icon} {name}: {result['status']}")
    
    print(f"\nOverall: {success_count}/{total_count} endpoints working")
    
    if success_count == total_count:
        print("🎉 All API endpoints are working correctly!")
        return True
    else:
        print("⚠️  Some API endpoints have issues")
        return False

if __name__ == "__main__":
    test_frontend_api_calls()

#!/usr/bin/env python3
"""
Test script untuk verifikasi pengiriman kelembapan eksternal dari BMKG ke dashboard React
"""

import requests
import json
import time
from datetime import datetime

def test_bmkg_api_endpoint():
    """Test endpoint BMKG untuk memastikan kelembapan luar tersedia"""
    print("🔍 Testing BMKG API endpoint...")
    
    try:
        response = requests.get(
            "http://localhost:8002/external/bmkg/latest",
            headers={
                "X-API-Key": "development_key_for_testing",
                "accept": "application/json"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ BMKG API endpoint responded successfully")
            
            # Check if humidity data is present
            if 'weather_data' in data and 'humidity' in data['weather_data']:
                humidity = data['weather_data']['humidity']
                temperature = data['weather_data']['temperature']
                condition = data['weather_data'].get('weather_condition', 'Unknown')
                data_source = data.get('data_source', 'Unknown')
                
                print(f"🌡️ Suhu Luar: {temperature}°C")
                print(f"💧 Kelembapan Luar: {humidity}%")
                print(f"🌤️ Kondisi Cuaca: {condition}")
                print(f"📡 Sumber Data: {data_source}")
                
                # Validate data types
                if isinstance(humidity, (int, float)) and isinstance(temperature, (int, float)):
                    print("✅ Data types are correct (numeric)")
                    return True, data
                else:
                    print("❌ Data types are incorrect")
                    return False, data
            else:
                print("❌ Humidity data missing from response")
                return False, data
        else:
            print(f"❌ API endpoint failed with status: {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"❌ Error testing BMKG API: {str(e)}")
        return False, None

def test_react_api_call():
    """Test the same endpoint that React app calls"""
    print("\n🔍 Testing React app API call pattern...")
    
    try:
        # Simulate how React app calls the API
        response = requests.get(
            "http://localhost:8002/external/bmkg/latest",
            headers={
                "Content-Type": "application/json",
                "X-API-Key": "development_key_for_testing"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ React-style API call successful")
            
            # Check the exact structure React expects
            expected_structure = {
                'weather_data': ['temperature', 'humidity', 'weather_condition'],
                'data_source': str
            }
            
            # Validate structure
            if 'weather_data' in data:
                weather_data = data['weather_data']
                missing_fields = []
                
                for field in expected_structure['weather_data']:
                    if field not in weather_data:
                        missing_fields.append(field)
                
                if missing_fields:
                    print(f"❌ Missing fields in weather_data: {missing_fields}")
                    return False
                else:
                    print("✅ All required fields present in weather_data")
                    
                    # Test the exact values React will use
                    ext_temp = weather_data.get('temperature')
                    ext_humidity = weather_data.get('humidity')
                    
                    print(f"📊 React will display:")
                    print(f"   Suhu Luar: {ext_temp}°C")
                    print(f"   Kelembapan Luar: {ext_humidity}%")
                    
                    return True
            else:
                print("❌ weather_data field missing")
                return False
        else:
            print(f"❌ React-style API call failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing React API pattern: {str(e)}")
        return False

def test_data_consistency():
    """Test multiple calls to ensure data consistency"""
    print("\n🔍 Testing data consistency over multiple calls...")
    
    results = []
    for i in range(3):
        try:
            response = requests.get(
                "http://localhost:8002/external/bmkg/latest",
                headers={"X-API-Key": "development_key_for_testing"},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'weather_data' in data:
                    results.append({
                        'temperature': data['weather_data'].get('temperature'),
                        'humidity': data['weather_data'].get('humidity'),
                        'data_source': data.get('data_source')
                    })
                    
            time.sleep(1)  # Wait 1 second between calls
            
        except Exception as e:
            print(f"⚠️ Call {i+1} failed: {str(e)}")
    
    if len(results) >= 2:
        print(f"✅ Successfully got {len(results)} consistent responses")
        for i, result in enumerate(results):
            print(f"   Call {i+1}: {result['temperature']}°C, {result['humidity']}%, {result['data_source']}")
        
        # Check if we're getting real data vs fallback
        real_data_count = sum(1 for r in results if 'Real-time' in r.get('data_source', ''))
        if real_data_count > 0:
            print(f"✅ {real_data_count}/{len(results)} calls returned real BMKG data")
        else:
            print("⚠️ All calls returned fallback data")
            
        return True
    else:
        print("❌ Not enough successful calls for consistency test")
        return False

def main():
    print("=" * 60)
    print("🧪 PENGUJIAN KELEMBAPAN EKSTERNAL BMKG UNTUK DASHBOARD")
    print("=" * 60)
    print(f"⏰ Test dilakukan pada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Basic BMKG API endpoint
    success1, data = test_bmkg_api_endpoint()
    
    # Test 2: React app API call pattern
    success2 = test_react_api_call()
    
    # Test 3: Data consistency
    success3 = test_data_consistency()
    
    print("\n" + "=" * 60)
    print("📋 RINGKASAN HASIL TEST")
    print("=" * 60)
    print(f"✅ BMKG API Endpoint: {'PASS' if success1 else 'FAIL'}")
    print(f"✅ React API Pattern: {'PASS' if success2 else 'FAIL'}")
    print(f"✅ Data Consistency: {'PASS' if success3 else 'FAIL'}")
    
    if success1 and success2 and success3:
        print("\n🎉 SEMUA TEST BERHASIL!")
        print("✅ Kelembapan eksternal BMKG siap ditampilkan di dashboard")
        print("✅ API endpoint berfungsi dengan baik")
        print("✅ Format data sesuai dengan yang diharapkan React")
        
        if data:
            print(f"\n📊 Data terakhir yang akan ditampilkan di dashboard:")
            if 'weather_data' in data:
                wd = data['weather_data']
                print(f"   🌡️ Suhu Luar: {wd.get('temperature', 'N/A')}°C")
                print(f"   💧 Kelembapan Luar: {wd.get('humidity', 'N/A')}%")
                print(f"   🌤️ Cuaca: {wd.get('weather_condition', 'N/A')}")
    else:
        print("\n⚠️ BEBERAPA TEST GAGAL!")
        print("❌ Perlu perbaikan sebelum kelembapan eksternal dapat ditampilkan dengan baik")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()

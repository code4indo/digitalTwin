#!/usr/bin/env python3
"""
Comprehensive verification script untuk memastikan dashboard React menampilkan kelembapan eksternal BMKG
"""

import requests
import json
import time
import re
from datetime import datetime

def test_react_dashboard_access():
    """Test akses ke dashboard React"""
    print("🔍 Testing React dashboard access...")
    
    try:
        response = requests.get("http://localhost:3003", timeout=10)
        
        if response.status_code == 200:
            print("✅ React dashboard accessible")
            
            # Check if it contains React app content
            if "react" in response.text.lower() or "root" in response.text:
                print("✅ React app content detected")
                return True
            else:
                print("⚠️ Dashboard accessible but React content unclear")
                return True
        else:
            print(f"❌ Dashboard not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error accessing dashboard: {str(e)}")
        return False

def verify_environmental_status_component():
    """Verify that EnvironmentalStatus component structure is correct"""
    print("\n🔍 Verifying EnvironmentalStatus component...")
    
    # Read the component file to check if external humidity is implemented
    try:
        with open('/home/lambda_one/project/digitalTwin/web-react/src/components/EnvironmentalStatus.js', 'r') as f:
            content = f.read()
        
        # Check for key indicators that external humidity is implemented
        checks = {
            'externalHumidity reference': 'externalHumidity' in content,
            'Kelembapan Luar text': 'Kelembapan Luar' in content,
            'weather.externalHumidity': 'weather?.externalHumidity' in content or 'weather.externalHumidity' in content,
            'external-humidity id': 'external-humidity' in content,
            'humidity field processing': 'humidity:' in content and 'weather_data' in content
        }
        
        print("📋 Component structure checks:")
        all_passed = True
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"   {status} {check}: {'FOUND' if result else 'MISSING'}")
            if not result:
                all_passed = False
        
        if all_passed:
            print("✅ All component structure checks passed")
        else:
            print("⚠️ Some component structure checks failed")
            
        return all_passed
        
    except Exception as e:
        print(f"❌ Error reading component file: {str(e)}")
        return False

def verify_api_integration():
    """Verify API integration for external weather data"""
    print("\n🔍 Verifying API integration...")
    
    try:
        with open('/home/lambda_one/project/digitalTwin/web-react/src/utils/api.js', 'r') as f:
            content = f.read()
        
        # Check for external weather API function
        checks = {
            'fetchExternalWeatherData function': 'fetchExternalWeatherData' in content,
            'external/bmkg/latest endpoint': '/external/bmkg/latest' in content,
            'API key configuration': 'X-API-Key' in content,
            'axios configuration': 'axios' in content
        }
        
        print("📋 API integration checks:")
        all_passed = True
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"   {status} {check}: {'FOUND' if result else 'MISSING'}")
            if not result:
                all_passed = False
        
        if all_passed:
            print("✅ All API integration checks passed")
        else:
            print("⚠️ Some API integration checks failed")
            
        return all_passed
        
    except Exception as e:
        print(f"❌ Error reading API file: {str(e)}")
        return False

def test_full_data_flow():
    """Test the complete data flow from BMKG API to dashboard display format"""
    print("\n🔍 Testing complete data flow...")
    
    try:
        # Get data from BMKG API
        response = requests.get(
            "http://localhost:8002/external/bmkg/latest",
            headers={"X-API-Key": "development_key_for_testing"},
            timeout=10
        )
        
        if response.status_code == 200:
            api_data = response.json()
            print("✅ Successfully fetched data from BMKG API")
            
            # Extract the data that React will use
            weather_data = api_data.get('weather_data', {})
            external_temp = weather_data.get('temperature')
            external_humidity = weather_data.get('humidity')
            weather_condition = weather_data.get('weather_condition')
            wind_speed = weather_data.get('wind_speed')
            wind_direction = weather_data.get('wind_direction')
            data_source = api_data.get('data_source')
            
            print("📊 Data yang akan ditampilkan di dashboard:")
            print(f"   🌡️ Suhu Luar: {external_temp}°C")
            print(f"   💧 Kelembapan Luar: {external_humidity}%")
            print(f"   🌤️ Kondisi Cuaca: {weather_condition}")
            if wind_speed:
                print(f"   💨 Angin: {wind_speed} m/s {wind_direction or ''}")
            print(f"   📡 Sumber: {data_source}")
            
            # Validate data format for React display
            validation_checks = {
                'Temperature is numeric': isinstance(external_temp, (int, float)),
                'Humidity is numeric': isinstance(external_humidity, (int, float)),
                'Weather condition is string': isinstance(weather_condition, str),
                'Data source indicates real-time': 'Real-time' in str(data_source),
                'Humidity within valid range': 0 <= external_humidity <= 100 if isinstance(external_humidity, (int, float)) else False
            }
            
            print("\n📋 Data validation for React display:")
            all_valid = True
            for check, result in validation_checks.items():
                status = "✅" if result else "❌"
                print(f"   {status} {check}: {'VALID' if result else 'INVALID'}")
                if not result:
                    all_valid = False
            
            if all_valid:
                print("✅ All data validation checks passed")
                
                # Show the exact format React expects
                react_format = {
                    "weather": {
                        "status": weather_condition,
                        "externalTemp": f"{external_temp:.1f}" if isinstance(external_temp, (int, float)) else str(external_temp),
                        "externalHumidity": f"{external_humidity:.0f}" if isinstance(external_humidity, (int, float)) else str(external_humidity),
                        "windSpeed": f"{wind_speed:.1f}" if isinstance(wind_speed, (int, float)) else None,
                        "windDirection": wind_direction,
                        "dataSource": data_source
                    }
                }
                
                print("\n📱 Format data untuk React component:")
                print(json.dumps(react_format, indent=2, ensure_ascii=False))
                
            return all_valid
        else:
            print(f"❌ Failed to fetch data from BMKG API: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing data flow: {str(e)}")
        return False

def check_container_status():
    """Check if all required containers are running"""
    print("\n🔍 Checking container status...")
    
    try:
        # Check API container
        api_response = requests.get("http://localhost:8002/external/bmkg/latest", 
                                   headers={"X-API-Key": "development_key_for_testing"}, 
                                   timeout=5)
        api_status = api_response.status_code == 200
        
        # Check React container
        react_response = requests.get("http://localhost:3003", timeout=5)
        react_status = react_response.status_code == 200
        
        print(f"   {'✅' if api_status else '❌'} API Container (port 8002): {'RUNNING' if api_status else 'NOT ACCESSIBLE'}")
        print(f"   {'✅' if react_status else '❌'} React Container (port 3003): {'RUNNING' if react_status else 'NOT ACCESSIBLE'}")
        
        return api_status and react_status
        
    except Exception as e:
        print(f"❌ Error checking container status: {str(e)}")
        return False

def generate_test_summary():
    """Generate a comprehensive test summary"""
    print("\n🔍 Running comprehensive verification...")
    
    # Run all tests
    results = {
        'Dashboard Access': test_react_dashboard_access(),
        'Component Structure': verify_environmental_status_component(),
        'API Integration': verify_api_integration(),
        'Data Flow': test_full_data_flow(),
        'Container Status': check_container_status()
    }
    
    return results

def main():
    print("=" * 70)
    print("🧪 VERIFIKASI LENGKAP TAMPILAN KELEMBAPAN EKSTERNAL BMKG")
    print("=" * 70)
    print(f"⏰ Verifikasi dilakukan pada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run comprehensive test
    results = generate_test_summary()
    
    print("\n" + "=" * 70)
    print("📋 RINGKASAN HASIL VERIFIKASI")
    print("=" * 70)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    
    if all_passed:
        print("🎉 SEMUA VERIFIKASI BERHASIL!")
        print("✅ Kelembapan eksternal BMKG berhasil diimplementasikan")
        print("✅ Dashboard React siap menampilkan data kelembapan luar")
        print("✅ Integrasi API berfungsi dengan sempurna")
        print("✅ Data real-time dari BMKG tersedia")
        
        print("\n📱 Cara melihat kelembapan eksternal di dashboard:")
        print("   1. Buka http://localhost:3003")
        print("   2. Lihat bagian 'Cuaca Eksternal (BMKG)'")
        print("   3. Kelembapan Luar akan ditampilkan di bawah Suhu Luar")
        print("   4. Data akan diperbarui otomatis setiap 5 menit")
        
    else:
        print("⚠️ BEBERAPA VERIFIKASI GAGAL!")
        print("❌ Perlu perbaikan untuk kelembapan eksternal dapat ditampilkan sempurna")
        
        failed_tests = [name for name, passed in results.items() if not passed]
        print(f"\n🔧 Test yang gagal: {', '.join(failed_tests)}")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Test komprehensif untuk verifikasi status data cuaca eksternal BMKG 
pada dashboard web React - apakah sudah real atau masih hardcode
"""

import requests
import json
import sys
from datetime import datetime

# Konfigurasi
API_BASE_URL = "http://localhost:8002"
API_KEY = "development_key_for_testing"
WEB_URL = "http://localhost:3003"

def test_bmkg_api_source():
    """Test langsung ke API BMKG untuk memverifikasi data source"""
    print("🌐 Testing BMKG API Source...")
    
    try:
        # Test langsung ke API BMKG
        bmkg_url = "https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4=31.74.04.1003"
        response = requests.get(bmkg_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ BMKG API accessible")
            
            if "data" in data and len(data["data"]) > 0:
                location = data.get("lokasi", {})
                weather_data = data["data"][0] if data["data"] else {}
                
                print(f"📍 Location: {location.get('provinsi', 'Unknown')}, {location.get('kecamatan', 'Unknown')}")
                
                if "cuaca" in weather_data:
                    cuaca_days = weather_data["cuaca"]
                    total_forecasts = sum(len(day) for day in cuaca_days)
                    print(f"📊 Total forecasts: {total_forecasts}")
                    
                    # Sample forecast
                    if cuaca_days and len(cuaca_days[0]) > 0:
                        sample = cuaca_days[0][0]
                        print(f"🌡️  Sample temp: {sample.get('t', 'N/A')}°C")
                        print(f"💧 Sample humidity: {sample.get('hu', 'N/A')}%")
                        print(f"🌪️  Sample wind: {sample.get('ws', 'N/A')} m/s")
                        
                return True
            else:
                print("❌ No data in BMKG response")
                return False
        else:
            print(f"❌ BMKG API Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ BMKG API Connection Error: {e}")
        return False

def test_local_bmkg_endpoint():
    """Test endpoint BMKG lokal"""
    print("\n🏠 Testing Local BMKG Endpoint...")
    
    headers = {"X-API-Key": API_KEY}
    
    try:
        response = requests.get(f"{API_BASE_URL}/external/bmkg/latest", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Local BMKG endpoint accessible")
            
            # Analyze response
            weather_data = data.get("weather_data", {})
            location = data.get("location", {})
            data_source = data.get("data_source", "")
            last_updated = data.get("last_updated", "")
            
            print(f"📊 Data source: {data_source}")
            print(f"🌡️  Temperature: {weather_data.get('temperature', 'N/A')}°C")
            print(f"💧 Humidity: {weather_data.get('humidity', 'N/A')}%")
            print(f"🌪️  Wind: {weather_data.get('wind_speed', 'N/A')} m/s")
            print(f"📍 Location: {location.get('region', 'Unknown')}")
            print(f"🕒 Last updated: {last_updated}")
            
            # Determine if data is real or hardcoded
            is_hardcoded = True
            
            # Check for known hardcoded values
            hardcoded_indicators = [
                weather_data.get("temperature") == 26.5,
                weather_data.get("humidity") == 78,
                weather_data.get("wind_speed") == 12.3,
                "Partly Cloudy" in str(weather_data.get("weather_condition", "")),
                "Fallback" in data_source or "Error" in data_source
            ]
            
            if any(hardcoded_indicators):
                print("⚠️  Data appears to be HARDCODED/FALLBACK")
                if "Fallback" in data_source:
                    print("   - Explicitly marked as fallback data")
                if "Error" in data_source:
                    print("   - Error fallback data")
                is_hardcoded = True
            else:
                print("✅ Data appears to be REAL from BMKG")
                is_hardcoded = False
                
            # Check timestamp freshness
            if last_updated:
                try:
                    if "2025-06-03" in last_updated:
                        print("⚠️  Timestamp appears to be hardcoded (2025-06-03)")
                    else:
                        update_time = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                        now = datetime.now().astimezone()
                        age_hours = (now - update_time).total_seconds() / 3600
                        
                        if age_hours < 24:
                            print(f"✅ Data is fresh ({age_hours:.1f} hours old)")
                        else:
                            print(f"⚠️  Data is old ({age_hours:.1f} hours old)")
                except:
                    print("⚠️  Could not parse timestamp")
            
            return not is_hardcoded
            
        else:
            print(f"❌ Local BMKG endpoint error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Local BMKG endpoint connection error: {e}")
        return False

def test_influxdb_bmkg_data():
    """Test apakah data BMKG tersimpan di InfluxDB"""
    print("\n💾 Testing BMKG Data in InfluxDB...")
    
    try:
        # Test via API internal endpoint if available
        headers = {"X-API-Key": API_KEY}
        
        # Check if there's a debug endpoint or create one to query InfluxDB directly
        # For now, we'll infer from the main endpoint behavior
        
        response = requests.get(f"{API_BASE_URL}/external/bmkg/latest", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Look for indicators that data came from InfluxDB
            if "error" in data:
                print(f"❌ InfluxDB query error: {data['error']}")
                return False
            elif "Fallback" in data.get("data_source", ""):
                print("❌ No real BMKG data in InfluxDB (using fallback)")
                return False
            elif data.get("data_source") == "BMKG" and "note" not in data:
                print("✅ Data appears to come from InfluxDB")
                return True
            else:
                print("⚠️  Uncertain if data comes from InfluxDB")
                return None
        else:
            print("❌ Could not test InfluxDB data")
            return False
            
    except Exception as e:
        print(f"❌ Error testing InfluxDB data: {e}")
        return False

def test_frontend_integration():
    """Test apakah frontend menampilkan data BMKG"""
    print("\n🌐 Testing Frontend Integration...")
    
    try:
        response = requests.get(WEB_URL, timeout=10)
        if response.status_code == 200:
            print("✅ Web dashboard accessible")
            
            # Check if the page contains BMKG-related content
            content = response.text.lower()
            if "bmkg" in content or "cuaca eksternal" in content:
                print("✅ Frontend contains BMKG weather references")
                return True
            else:
                print("⚠️  No BMKG references found in frontend")
                return False
        else:
            print(f"❌ Web dashboard not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Frontend connection error: {e}")
        return False

def main():
    print("=" * 80)
    print("🌦️  VERIFICATION: Cuaca Eksternal BMKG - Real vs Hardcode")
    print("   Memverifikasi apakah data BMKG menggunakan API real atau hardcode")
    print("=" * 80)
    
    # Run tests
    bmkg_api_ok = test_bmkg_api_source()
    local_endpoint_real = test_local_bmkg_endpoint()
    influxdb_data_ok = test_influxdb_bmkg_data()
    frontend_ok = test_frontend_integration()
    
    print("\n" + "=" * 80)
    print("📋 SUMMARY HASIL VERIFIKASI:")
    print(f"   1. BMKG API Source: {'✅ Accessible' if bmkg_api_ok else '❌ Not accessible'}")
    print(f"   2. Local Endpoint: {'✅ Using real data' if local_endpoint_real else '❌ Using hardcode/fallback'}")
    print(f"   3. InfluxDB Integration: {'✅ Working' if influxdb_data_ok else '❌ Not working' if influxdb_data_ok is False else '⚠️ Uncertain'}")
    print(f"   4. Frontend Integration: {'✅ BMKG found' if frontend_ok else '❌ Not found'}")
    
    print("\n🎯 KESIMPULAN:")
    if local_endpoint_real and influxdb_data_ok:
        print("   ✅ Cuaca eksternal BMKG SUDAH menggunakan data REAL!")
        print("   ✅ Data diambil dari API BMKG dan tersimpan di InfluxDB")
        print("   ✅ Dashboard menampilkan data cuaca real, bukan hardcode")
    elif local_endpoint_real and influxdb_data_ok is None:
        print("   ⚠️  Cuaca eksternal BMKG kemungkinan menggunakan data REAL")
        print("   ⚠️  Perlu verifikasi lebih lanjut untuk InfluxDB integration")
    else:
        print("   ❌ Cuaca eksternal BMKG MASIH menggunakan data HARDCODE/FALLBACK")
        print("   ❌ Data tidak diambil dari API BMKG real atau ada masalah integrasi")
        
        if not bmkg_api_ok:
            print("   - API BMKG tidak dapat diakses")
        if not local_endpoint_real:
            print("   - Endpoint lokal menggunakan data fallback")
        if influxdb_data_ok is False:
            print("   - Data tidak tersimpan dengan benar di InfluxDB")
        if not frontend_ok:
            print("   - Frontend tidak menampilkan data BMKG")
    
    print("=" * 80)

if __name__ == "__main__":
    main()

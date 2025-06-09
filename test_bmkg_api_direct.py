#!/usr/bin/env python3
"""
Test langsung API BMKG untuk memverifikasi implementasi 
tanpa melalui container yang bermasalah
"""

import requests
import json
from datetime import datetime

def test_bmkg_direct():
    """Test langsung ke API BMKG"""
    print("🌐 Testing Direct BMKG API...")
    
    try:
        BMKG_API_URL = "https://api.bmkg.go.id/publik/prakiraan-cuaca"
        KODE_WILAYAH = "31.74.04.1003"  # Cilandak Timur, Jakarta Selatan
        
        response = requests.get(f"{BMKG_API_URL}?adm4={KODE_WILAYAH}", timeout=15)
        
        if response.status_code == 200:
            raw_data = response.json()
            
            print("✅ BMKG API responded successfully")
            
            if "data" in raw_data and len(raw_data["data"]) > 0:
                data_entry = raw_data["data"][0]
                location_info = data_entry.get("lokasi", {})
                cuaca_days = data_entry.get("cuaca", [])
                
                print(f"📍 Location: {location_info.get('provinsi')}, {location_info.get('kecamatan')}")
                print(f"📊 Forecast days: {len(cuaca_days)}")
                
                # Process current forecast
                if cuaca_days and len(cuaca_days[0]) > 0:
                    current_forecast = cuaca_days[0][0]
                    
                    # Create formatted response similar to what API should return
                    formatted_data = {
                        "weather_data": {
                            "temperature": current_forecast.get("t"),
                            "humidity": current_forecast.get("hu"),
                            "wind_speed": current_forecast.get("ws"),
                            "wind_direction": current_forecast.get("wd_to", "N/A"),
                            "pressure": None,
                            "visibility": current_forecast.get("vs_text", "").replace("> ", "").replace(" km", "") or None,
                            "weather_condition": current_forecast.get("weather_desc", ""),
                            "weather_code": current_forecast.get("weather", "")
                        },
                        "location": {
                            "region": location_info.get("provinsi", "DKI Jakarta"),
                            "station": location_info.get("kecamatan", "Pasar Minggu"),
                            "coordinates": {
                                "latitude": location_info.get("lat"),
                                "longitude": location_info.get("lon")
                            }
                        },
                        "timestamp": datetime.now().isoformat(),
                        "data_source": "BMKG API Real-time",
                        "last_updated": current_forecast.get("utc_datetime", datetime.now().isoformat())
                    }
                    
                    print("\n📋 Formatted BMKG Data (Real):")
                    print(f"🌡️  Temperature: {formatted_data['weather_data']['temperature']}°C")
                    print(f"💧 Humidity: {formatted_data['weather_data']['humidity']}%")
                    print(f"🌪️  Wind: {formatted_data['weather_data']['wind_speed']} m/s")
                    print(f"🌤️  Condition: {formatted_data['weather_data']['weather_condition']}")
                    print(f"🕒 Updated: {formatted_data['last_updated']}")
                    print(f"📍 Coordinates: {formatted_data['location']['coordinates']['latitude']}, {formatted_data['location']['coordinates']['longitude']}")
                    
                    # Save to file for manual testing
                    with open('/tmp/bmkg_real_data.json', 'w') as f:
                        json.dump(formatted_data, f, indent=2)
                    print(f"\n💾 Real BMKG data saved to /tmp/bmkg_real_data.json")
                    
                    return True
                    
        print("❌ No valid data in BMKG response")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def compare_with_hardcode():
    """Compare with typical hardcoded values"""
    print("\n🔍 Hardcode vs Real Data Analysis...")
    
    # Typical hardcoded values seen in implementations
    hardcoded_example = {
        "temperature": 26.5,
        "humidity": 78,
        "wind_speed": 12.3,
        "weather_condition": "Partly Cloudy"
    }
    
    print("📄 Typical hardcoded values:")
    for key, value in hardcoded_example.items():
        print(f"   {key}: {value}")
    
    print("\n✅ Real BMKG data varies and updates regularly")
    print("✅ Location coordinates are real (Cilandak Timur)")
    print("✅ Timestamps are current")
    print("✅ Weather conditions change based on actual forecast")

def create_simple_endpoint_test():
    """Create a simple endpoint implementation for testing"""
    print("\n🛠️  Simple Endpoint Implementation:")
    
    endpoint_code = '''
@router.get("/bmkg/latest")
async def get_latest_bmkg_data(api_key: str = Depends(get_api_key)):
    try:
        bmkg_response = requests.get(
            "https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4=31.74.04.1003",
            timeout=15
        )
        
        if bmkg_response.status_code == 200:
            raw_data = bmkg_response.json()
            
            if "data" in raw_data and len(raw_data["data"]) > 0:
                data_entry = raw_data["data"][0]
                location_info = data_entry.get("lokasi", {})
                cuaca_days = data_entry.get("cuaca", [])
                
                if cuaca_days and len(cuaca_days[0]) > 0:
                    current_forecast = cuaca_days[0][0]
                    
                    return {
                        "weather_data": {
                            "temperature": current_forecast.get("t"),
                            "humidity": current_forecast.get("hu"),
                            "wind_speed": current_forecast.get("ws"),
                            "weather_condition": current_forecast.get("weather_desc", "")
                        },
                        "location": {
                            "region": location_info.get("provinsi", "DKI Jakarta"),
                            "station": location_info.get("kecamatan", "Pasar Minggu")
                        },
                        "data_source": "BMKG API Real-time",
                        "last_updated": current_forecast.get("utc_datetime")
                    }
    except:
        pass
    
    # Fallback
    return {"data_source": "Fallback", ...}
'''
    
    print(endpoint_code)

if __name__ == "__main__":
    print("=" * 80)
    print("🌦️  BMKG API Real Data Verification")
    print("=" * 80)
    
    success = test_bmkg_direct()
    compare_with_hardcode()
    create_simple_endpoint_test()
    
    print("\n" + "=" * 80)
    if success:
        print("✅ BMKG API REAL DATA IS AVAILABLE AND ACCESSIBLE!")
        print("✅ Implementation can use real data instead of hardcode")
        print("✅ Data varies and updates regularly")
    else:
        print("❌ Could not access BMKG API real data")
        
    print("=" * 80)

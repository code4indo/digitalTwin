#!/usr/bin/env python3
"""
Final verification: Show the exact data that React dashboard should display
"""

import requests
import json
from datetime import datetime

def get_react_display_data():
    """Get the data exactly as it would appear in the React dashboard"""
    try:
        # Fetch data from the same endpoint React uses
        response = requests.get(
            "http://localhost:3003/api/external/bmkg/latest",
            headers={"x-api-key": "development_key_for_testing"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Process exactly like the React component does
            weather_data = data.get('weather_data', {})
            
            # Extract values using the same logic as React
            humidity = weather_data.get('humidity')
            temperature = weather_data.get('temperature')
            condition = weather_data.get('weather_condition', 'Cerah Berawan')
            wind_speed = weather_data.get('wind_speed')
            wind_direction = weather_data.get('wind_direction')
            
            # Format exactly like React component
            formatted_data = {
                'externalTemp': f"{temperature:.1f}" if isinstance(temperature, (int, float)) else '29.8',
                'externalHumidity': f"{humidity:.0f}" if isinstance(humidity, (int, float)) else '65',
                'status': condition,
                'windSpeed': f"{wind_speed:.1f}" if isinstance(wind_speed, (int, float)) else None,
                'windDirection': wind_direction,
                'dataSource': data.get('data_source', 'Unknown')
            }
            
            return formatted_data, data
        else:
            return None, None
            
    except Exception as e:
        print(f"Error: {e}")
        return None, None

def main():
    print("🎯 EXACT REACT DASHBOARD DISPLAY DATA")
    print("=" * 60)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    react_data, raw_data = get_react_display_data()
    
    if react_data:
        print("📱 WHAT YOU SHOULD SEE IN THE DASHBOARD:")
        print("─" * 40)
        print(f"Suhu Luar: {react_data['externalTemp']}°C")
        print(f"Kelembapan Luar: {react_data['externalHumidity']}%")
        print(f"Kondisi: {react_data['status']}")
        if react_data['windSpeed']:
            wind_text = f"Angin: {react_data['windSpeed']} m/s"
            if react_data['windDirection']:
                wind_text += f" {react_data['windDirection']}"
            print(wind_text)
        print(f"Sumber: {react_data['dataSource']}")
        print()
        
        print("📊 RAW API DATA:")
        print("─" * 40)
        print(json.dumps(raw_data['weather_data'], indent=2))
        print()
        
        print("✅ SUCCESS!")
        print(f"The React dashboard should display external humidity as: {react_data['externalHumidity']}%")
        print()
        print("🌐 To verify in browser:")
        print("1. Open http://localhost:3003")
        print("2. Look for 'Cuaca Eksternal (BMKG)' section")
        print("3. Find 'Kelembapan Luar' field")
        print("4. It should show the humidity value above")
    else:
        print("❌ FAILED to fetch data")
        print("Please check if the API service is running")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Debug humidity display issue - comprehensive test
"""

import requests
import json
import time
from datetime import datetime

def main():
    print("🧪 DEBUGGING HUMIDITY DISPLAY ISSUE")
    print("=" * 50)
    
    # Test 1: API data
    print("1. Testing API data...")
    try:
        response = requests.get(
            "http://localhost:3003/api/external/bmkg/latest",
            headers={"x-api-key": "development_key_for_testing"},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            humidity = data.get('weather_data', {}).get('humidity')
            print(f"✅ API returns humidity: {humidity}%")
        else:
            print(f"❌ API error: {response.status_code}")
    except Exception as e:
        print(f"❌ API error: {e}")
    
    # Test 2: React app access
    print("\n2. Testing React app...")
    try:
        response = requests.get("http://localhost:3003", timeout=10)
        if response.status_code == 200:
            print("✅ React app accessible")
        else:
            print(f"❌ React error: {response.status_code}")
    except Exception as e:
        print(f"❌ React error: {e}")
    
    print("\n" + "="*50)
    print("🔍 MANUAL STEPS TO CHECK:")
    print("="*50)
    print("1. Open http://localhost:3003 in browser")
    print("2. Open Developer Tools (F12)")
    print("3. Go to Console tab")
    print("4. Refresh page and look for debug messages:")
    print("   - 'WEATHER DEBUG - Full data received:'")
    print("   - 'HUMIDITY DEBUG - Raw data:'")
    print("5. Check if 'Kelembapan Luar' appears in UI")
    print("="*50)

if __name__ == "__main__":
    main()

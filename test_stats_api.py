#!/usr/bin/env python3
"""
Script untuk menguji endpoint statistik lingkungan yang baru dibuat.
Script ini dirancang untuk bekerja dengan API yang berjalan di dalam container.
"""

import requests
import json
from datetime import datetime, timedelta
import os

# Konfigurasi URL API - Gunakan environment variable atau default ke localhost
# Format URL disesuaikan dengan container deployment
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "dev-key-123") # Ganti dengan API key yang sesuai

def print_json_response(response):
    """Mencetak respons JSON dengan format yang readable."""
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(f"Non-JSON response: {response.text}")

def test_temperature_stats():
    """Test endpoint statistik suhu."""
    print("\n=== Testing Temperature Stats Endpoint ===")
    
    # Test dengan parameter default (24 jam terakhir)
    url = f"{API_BASE_URL}/stats/temperature/"
    headers = {"X-API-KEY": API_KEY}
    
    print(f"\nTesting GET {url} (default parameters)")
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print(f"✅ Status code: {response.status_code}")
            print_json_response(response)
        else:
            print(f"❌ Error: Status code {response.status_code}")
            print_json_response(response)
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Test dengan rentang waktu yang ditentukan (7 hari terakhir)
    start_time = (datetime.now() - timedelta(days=7)).isoformat()
    params = {"start_time": start_time}
    
    print(f"\nTesting GET {url} with start_time={start_time}")
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            print(f"✅ Status code: {response.status_code}")
            print_json_response(response)
        else:
            print(f"❌ Error: Status code {response.status_code}")
            print_json_response(response)
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

def test_humidity_stats():
    """Test endpoint statistik kelembapan."""
    print("\n=== Testing Humidity Stats Endpoint ===")
    
    # Test dengan parameter default (24 jam terakhir)
    url = f"{API_BASE_URL}/stats/humidity/"
    headers = {"X-API-KEY": API_KEY}
    
    print(f"\nTesting GET {url} (default parameters)")
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print(f"✅ Status code: {response.status_code}")
            print_json_response(response)
        else:
            print(f"❌ Error: Status code {response.status_code}")
            print_json_response(response)
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

def test_environmental_stats():
    """Test endpoint gabungan statistik lingkungan."""
    print("\n=== Testing Environmental Stats Endpoint ===")
    
    # Test dengan parameter default (24 jam terakhir)
    url = f"{API_BASE_URL}/stats/environmental/"
    headers = {"X-API-KEY": API_KEY}
    
    print(f"\nTesting GET {url} (default parameters)")
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print(f"✅ Status code: {response.status_code}")
            print_json_response(response)
        else:
            print(f"❌ Error: Status code {response.status_code}")
            print_json_response(response)
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Test dengan rentang waktu dan lokasi
    start_time = (datetime.now() - timedelta(days=3)).isoformat()
    params = {
        "start_time": start_time,
        "locations": ["F2", "F3", "G2", "G3"]
    }
    
    print(f"\nTesting GET {url} with start_time and locations filter")
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            print(f"✅ Status code: {response.status_code}")
            print_json_response(response)
        else:
            print(f"❌ Error: Status code {response.status_code}")
            print_json_response(response)
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

def check_response_structure(response_data):
    """Verifikasi struktur respons sesuai dengan yang diharapkan frontend."""
    print("\n=== Checking Response Structure for Frontend Compatibility ===")
    
    # Struktur yang diharapkan oleh EnvironmentalStatus.js
    expected_temp_keys = ["avg_temperature", "min_temperature", "max_temperature"]
    expected_humid_keys = ["avg_humidity", "min_humidity", "max_humidity"]
    
    # Check temperature endpoint
    if "temperature" in response_data:  # Combined endpoint
        temp_data = response_data["temperature"]
        for key in expected_temp_keys:
            if key not in temp_data:
                print(f"❌ Missing key in temperature data: {key}")
                return False
        print("✅ Temperature data structure is compatible with frontend")
    elif "avg_temperature" in response_data:  # Temperature-only endpoint
        for key in expected_temp_keys:
            if key not in response_data:
                print(f"❌ Missing key in temperature data: {key}")
                return False
        print("✅ Temperature data structure is compatible with frontend")
    
    # Check humidity endpoint
    if "humidity" in response_data:  # Combined endpoint
        humid_data = response_data["humidity"]
        for key in expected_humid_keys:
            if key not in humid_data:
                print(f"❌ Missing key in humidity data: {key}")
                return False
        print("✅ Humidity data structure is compatible with frontend")
    elif "avg_humidity" in response_data:  # Humidity-only endpoint
        for key in expected_humid_keys:
            if key not in response_data:
                print(f"❌ Missing key in humidity data: {key}")
                return False
        print("✅ Humidity data structure is compatible with frontend")
    
    return True

if __name__ == "__main__":
    print("Starting API endpoint testing...")
    print(f"API URL: {API_BASE_URL}")
    
    # Test individual endpoints
    test_temperature_stats()
    test_humidity_stats()
    test_environmental_stats()
    
    # Test structure compatibility with frontend
    print("\n=== Checking Frontend Compatibility ===")
    url = f"{API_BASE_URL}/stats/environmental/"
    headers = {"X-API-KEY": API_KEY}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            check_response_structure(response.json())
        else:
            print(f"❌ Could not check structure: Status code {response.status_code}")
    except Exception as e:
        print(f"❌ Exception when checking structure: {str(e)}")
    
    print("\nEndpoint testing completed.")

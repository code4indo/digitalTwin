#!/usr/bin/env python
"""
Script untuk menguji endpoint API ruangan.
"""

import requests
import json
import sys
import os
from datetime import datetime

# Konfigurasi
API_URL = os.getenv("API_URL", "http://localhost:8002")
API_KEY = os.getenv("API_KEY", "development_key_for_testing")  # Ganti dengan API key yang valid

# Function untuk melakukan request ke API
def api_request(endpoint, method="GET", data=None):
    url = f"{API_URL}{endpoint}"
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Sending {method} request to {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        else:
            print(f"HTTP method {method} not supported")
            return None
        
        # Print hasil
        print(f"Status: {response.status_code}")
        
        if response.status_code >= 200 and response.status_code < 300:
            return response.json()
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Exception: {str(e)}")
        return None

# Menguji endpoint daftar ruangan
def test_get_rooms():
    print("\n=== Testing GET /rooms/ ===")
    result = api_request("/rooms/")
    
    if result:
        print(f"Found {len(result)} rooms")
        print(json.dumps(result[:2], indent=2))  # Tampilkan 2 ruangan pertama saja
    else:
        print("Failed to get rooms list")
    
    return result

# Menguji endpoint detail ruangan
def test_get_room_details(room_id):
    print(f"\n=== Testing GET /rooms/{room_id} ===")
    result = api_request(f"/rooms/{room_id}")
    
    if result:
        print(f"Room details for {room_id}:")
        print(json.dumps(result, indent=2))
    else:
        print(f"Failed to get details for room {room_id}")
    
    return result

# Main function
def main():
    print("=== Room API Endpoints Test ===")
    
    # Uji endpoint daftar ruangan
    rooms = test_get_rooms()
    
    # Uji endpoint detail ruangan
    if rooms and len(rooms) > 0:
        # Pilih salah satu ruangan untuk diuji
        room_id = rooms[0]["id"]
        test_get_room_details(room_id)
    else:
        # Coba dengan ID ruangan hardcoded jika daftar ruangan kosong
        test_get_room_details("F2")
        test_get_room_details("G3")

if __name__ == "__main__":
    main()
